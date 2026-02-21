from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum
from datetime import timedelta
from .models import FoodStall, FoodItem, TimeSlot, Order, DemandAnalytics, StallOwner
from .forms import (StudentRegistrationForm, OrderForm,
                    FoodItemForm, FoodStallForm, TimeSlotForm,
                    StallOwnerCreationForm)

def is_admin(user):
    return user.is_staff

def is_stall_owner(user):
    return hasattr(user, 'stall_owner_profile')

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        if is_stall_owner(request.user):
            return redirect('stall_owner_dashboard')
        return redirect('student_dashboard')
    stalls = FoodStall.objects.filter(is_active=True)
    return render(request, 'home.html', {'stalls': stalls})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in as {user.username}.")
            if user.is_staff:
                return redirect('admin_dashboard')
            if is_stall_owner(user):
                return redirect('stall_owner_dashboard')
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    if is_stall_owner(request.user):
        return redirect('stall_owner_dashboard')
    user_orders = Order.objects.filter(user=request.user).select_related(
        'food_item', 'food_item__stall', 'time_slot'
    )
    recent_orders    = user_orders[:5]
    total_orders     = user_orders.count()
    pending_orders   = user_orders.filter(status='Pending').count()
    completed_orders = user_orders.filter(status='Completed').count()
    all_slots        = TimeSlot.objects.filter(is_active=True)
    orders_by_stall = (
        user_orders
        .values('food_item__stall__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    context = {
        'recent_orders':    recent_orders,
        'total_orders':     total_orders,
        'pending_orders':   pending_orders,
        'completed_orders': completed_orders,
        'all_slots':        all_slots,
        'orders_by_stall':  orders_by_stall,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def menu_view(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    if is_stall_owner(request.user):
        return redirect('stall_owner_dashboard')
    stall_filter = request.GET.get('stall')          # optional filter
    all_stalls   = FoodStall.objects.filter(is_active=True)
    if stall_filter:
        stalls_with_items = all_stalls.filter(id=stall_filter)
    else:
        stalls_with_items = all_stalls
    stall_data = []
    for stall in stalls_with_items:
        items = stall.food_items.filter(is_available=True)
        stall_data.append({'stall': stall, 'items': items})
    return render(request, 'student/menu.html', {
        'stall_data':    stall_data,
        'all_stalls':    all_stalls,
        'stall_filter':  stall_filter,
    })


@login_required
def place_order(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    if is_stall_owner(request.user):
        return redirect('stall_owner_dashboard')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order      = form.save(commit=False)
            order.user = request.user

            slot = order.time_slot
            if slot.is_full():
                messages.error(request,
                    f"'{slot.slot_name}' just became full. Please pick another slot.")
                return render(request, 'student/order.html', _order_context(form))
            order.save()
            slot.current_orders += 1
            slot.save()
            stall_name = order.food_item.stall.name if order.food_item.stall else 'General'
            messages.success(request,
                f"Order #{order.id} placed from {stall_name}!")
            return redirect('my_orders')
    else:
        form = OrderForm()
    return render(request, 'student/order.html', _order_context(form))


def _order_context(form):
    slots = list(TimeSlot.objects.filter(is_active=True).values(
        'id', 'slot_name', 'max_capacity', 'current_orders'
    ))
    food_items_js = list(
        FoodItem.objects.filter(is_available=True)
        .values('id', 'stall_id', 'name', 'price')
    )
    stalls_js = list(FoodStall.objects.filter(is_active=True).values('id', 'name'))
    return {
        'form':         form,
        'slots':        slots,
        'food_items_js': food_items_js,
        'stalls_js':    stalls_js,
    }

@login_required
def my_orders(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    if is_stall_owner(request.user):
        return redirect('stall_owner_dashboard')
    status_filter = request.GET.get('status', 'all')
    stall_filter  = request.GET.get('stall', 'all')
    orders = Order.objects.filter(user=request.user).select_related(
        'food_item', 'food_item__stall', 'time_slot'
    )
    if status_filter in ('Pending', 'Completed', 'Cancelled'):
        orders = orders.filter(status=status_filter)
    if stall_filter != 'all':
        orders = orders.filter(food_item__stall__id=stall_filter)
    all_stalls = FoodStall.objects.filter(is_active=True)
    return render(request, 'student/my_orders.html', {
        'orders':        orders,
        'status_filter': status_filter,
        'stall_filter':  stall_filter,
        'all_stalls':    all_stalls,
    })

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != 'Pending':
        messages.warning(request, "Only Pending orders can be cancelled.")
        return redirect('my_orders')
    slot = order.time_slot
    if slot.current_orders > 0:
        slot.current_orders -= 1
        slot.save()
    order.status = 'Cancelled'
    order.save()
    messages.info(request, f"Order #{order.id} has been cancelled.")
    return redirect('my_orders')

@login_required
def stall_owner_dashboard(request):
    if not is_stall_owner(request.user):
        return redirect('home')
    owner = request.user.stall_owner_profile
    stall = owner.stall
    today = timezone.localdate()
    all_orders = (
        Order.objects
        .filter(food_item__stall=stall)
        .select_related('user', 'food_item', 'time_slot')
        .order_by('-order_time')
    )
    today_orders  = all_orders.filter(order_time__date=today)
    revenue_today = today_orders.filter(
        status__in=['Pending', 'Completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0
    status_filter = request.GET.get('status', 'all')
    display_orders = all_orders
    if status_filter in ('Pending', 'Completed', 'Cancelled'):
        display_orders = all_orders.filter(status=status_filter)
    context = {
        'owner':           owner,
        'stall':           stall,
        'orders':          display_orders[:50],
        'today_count':     today_orders.count(),
        'revenue_today':   revenue_today,
        'pending_count':   all_orders.filter(status='Pending').count(),
        'completed_count': all_orders.filter(status='Completed').count(),
        'status_filter':   status_filter,
    }
    return render(request, 'stall_owner/dashboard.html', context)

@login_required
def stall_owner_update_order(request, order_id):
    if not is_stall_owner(request.user):
        return redirect('home')

    owner = request.user.stall_owner_profile
    order = get_object_or_404(Order, id=order_id, food_item__stall=owner.stall)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ('Completed', 'Cancelled'):
            if new_status == 'Cancelled' and order.status == 'Pending':
                slot = order.time_slot
                if slot.current_orders > 0:
                    slot.current_orders -= 1
                    slot.save()
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} marked as {new_status}.")

    return redirect('stall_owner_dashboard')
    today = timezone.localdate()

    total_orders_today = Order.objects.filter(order_time__date=today).count()
    revenue_today = Order.objects.filter(
        order_time__date=today, status__in=['Pending', 'Completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    pending_orders = Order.objects.filter(status='Pending').count()
    all_slots      = TimeSlot.objects.filter(is_active=True)
    recent_orders  = Order.objects.select_related(
        'user', 'food_item', 'food_item__stall', 'time_slot'
    )[:10]

    # Per-stall revenue today
    stall_revenue = (
        Order.objects
        .filter(order_time__date=today, status__in=['Pending', 'Completed'])
        .values('food_item__stall__name')
        .annotate(revenue=Sum('total_price'), orders=Count('id'))
        .order_by('-revenue')
    )

    context = {
        'total_orders_today': total_orders_today,
        'revenue_today':      revenue_today,
        'pending_orders':     pending_orders,
        'all_slots':          all_slots,
        'recent_orders':      recent_orders,
        'stall_revenue':      stall_revenue,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_stalls(request):
    """Admin: view all stalls + add a new one."""
    stalls = FoodStall.objects.all()

    if request.method == 'POST':
        form = FoodStallForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Stall added successfully.")
            return redirect('manage_stalls')
    else:
        form = FoodStallForm()

    return render(request, 'admin_dashboard/stalls.html', {
        'stalls': stalls, 'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def edit_stall(request, stall_id):
    """Admin: edit an existing food stall."""
    stall = get_object_or_404(FoodStall, id=stall_id)

    if request.method == 'POST':
        form = FoodStallForm(request.POST, request.FILES, instance=stall)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{stall.name}' updated.")
            return redirect('manage_stalls')
    else:
        form = FoodStallForm(instance=stall)

    return render(request, 'admin_dashboard/edit_stall.html', {
        'form': form, 'stall': stall
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_stall(request, stall_id):
    """Admin: delete a food stall (POST only)."""
    stall = get_object_or_404(FoodStall, id=stall_id)
    if request.method == 'POST':
        name = stall.name
        stall.delete()
        messages.success(request, f"'{name}' deleted.")
    return redirect('manage_stalls')


@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_stall_owners(request):
    """Admin: list all stall owners and create a new one."""
    owners = StallOwner.objects.select_related('user', 'stall').all()

    if request.method == 'POST':
        form = StallOwnerCreationForm(request.POST)
        if form.is_valid():
            owner = form.save()
            messages.success(
                request,
                f"Stall owner '{owner.user.username}' created. "
                f"Stall Code: {owner.stall_code}"
            )
            return redirect('manage_stall_owners')
    else:
        form = StallOwnerCreationForm()

    return render(request, 'admin_dashboard/stall_owners.html', {
        'owners': owners,
        'form':   form,
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_stall_owner(request, owner_id):
    owner = get_object_or_404(StallOwner, id=owner_id)
    if request.method == 'POST':
        username = owner.user.username
        owner.user.delete()          # cascade deletes StallOwner too
        messages.success(request, f"Stall owner '{username}' removed.")
    return redirect('manage_stall_owners')

@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_food(request):
    # Allow filtering by stall
    stall_filter = request.GET.get('stall')
    all_stalls   = FoodStall.objects.all()
    food_items   = FoodItem.objects.select_related('stall').all()

    if stall_filter:
        food_items = food_items.filter(stall__id=stall_filter)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Food item added successfully.")
            return redirect('manage_food')
    else:
        form = FoodItemForm()

    return render(request, 'admin_dashboard/food_items.html', {
        'food_items':   food_items,
        'form':         form,
        'all_stalls':   all_stalls,
        'stall_filter': stall_filter,
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def edit_food(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{item.name}' updated.")
            return redirect('manage_food')
    else:
        form = FoodItemForm(instance=item)

    return render(request, 'admin_dashboard/edit_food.html', {'form': form, 'item': item})


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_food(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f"'{name}' deleted.")
    return redirect('manage_food')

@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_slots(request):
    """Admin: view all time slots + add a new one."""
    slots = TimeSlot.objects.all()

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Time slot added.")
            return redirect('manage_slots')
    else:
        form = TimeSlotForm()

    return render(request, 'admin_dashboard/time_slots.html', {
        'slots': slots, 'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def edit_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, "Slot updated.")
            return redirect('manage_slots')
    else:
        form = TimeSlotForm(instance=slot)

    return render(request, 'admin_dashboard/edit_slot.html', {'form': form, 'slot': slot})


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)
    if request.method == 'POST':
        slot.delete()
        messages.success(request, "Slot deleted.")
    return redirect('manage_slots')


@login_required
@user_passes_test(is_admin, login_url='/login/')
def update_order_status(request, order_id):
    order  = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')

    if status in ('Completed', 'Cancelled', 'Pending'):
        if order.status == 'Pending' and status == 'Cancelled':
            slot = order.time_slot
            if slot.current_orders > 0:
                slot.current_orders -= 1
                slot.save()
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} marked as {status}.")

    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin, login_url='/login/')
def analytics_view(request):
    today    = timezone.localdate()
    week_ago = today - timedelta(days=6)

    # Orders per food item
    orders_by_item = (
        Order.objects
        .filter(order_time__date__gte=week_ago)
        .values('food_item__name', 'food_item__stall__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Orders per stall (last 7 days)
    orders_by_stall = (
        Order.objects
        .filter(order_time__date__gte=week_ago)
        .values('food_item__stall__name')
        .annotate(total=Count('id'), revenue=Sum('total_price'))
        .order_by('-total')
    )

    slot_data = TimeSlot.objects.filter(is_active=True)

    # Simple demand prediction per item
    predictions = []
    for item in FoodItem.objects.filter(is_available=True).select_related('stall'):
        past_orders = Order.objects.filter(
            food_item=item, order_time__date__gte=week_ago
        ).count()
        avg = round(past_orders / 7, 1)
        predictions.append({
            'food':        item.name,
            'stall':       item.stall.name if item.stall else 'General',
            'avg_per_day': avg,
            'high_demand': avg >= 5,
        })
    predictions.sort(key=lambda x: x['avg_per_day'], reverse=True)

    # Chart.js data — items
    chart_labels = [d['food_item__name'] for d in orders_by_item]
    chart_values = [d['total'] for d in orders_by_item]

    # Chart.js data — stalls
    stall_chart_labels = [d['food_item__stall__name'] or 'General' for d in orders_by_stall]
    stall_chart_values = [d['total'] for d in orders_by_stall]

    context = {
        'orders_by_item':    orders_by_item,
        'orders_by_stall':   orders_by_stall,
        'slot_data':         slot_data,
        'predictions':       predictions,
        'chart_labels':      chart_labels,
        'chart_values':      chart_values,
        'stall_chart_labels': stall_chart_labels,
        'stall_chart_values': stall_chart_values,
        'week_ago':          week_ago,
        'today':             today,
    }
    return render(request, 'admin_dashboard/analytics.html', context)

def is_admin(user):
    return user.is_staff

def home_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in as {user.username}.")
            # Redirect admin to admin dashboard
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    user_orders = Order.objects.filter(user=request.user).select_related('food_item', 'time_slot')
    recent_orders = user_orders[:5]  # Show 5 most recent
    total_orders     = user_orders.count()
    pending_orders   = user_orders.filter(status='Pending').count()
    completed_orders = user_orders.filter(status='Completed').count()
    all_slots = TimeSlot.objects.filter(is_active=True)
    context = {
        'recent_orders':   recent_orders,
        'total_orders':    total_orders,
        'pending_orders':  pending_orders,
        'completed_orders': completed_orders,
        'all_slots':       all_slots,
    }
    return render(request, 'student/dashboard.html', context)

@login_required
def menu_view(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    food_items = FoodItem.objects.filter(is_available=True)
    return render(request, 'student/menu.html', {'food_items': food_items})
@login_required
def place_order(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  
            slot = order.time_slot
            if slot.is_full():
                messages.error(request, f"'{slot.slot_name}' just became full. Please pick another slot.")
                return render(request, 'student/order.html', {'form': form})

            order.save()  # total_price is auto-calculated in model.save()
            # Increment the slot's current_orders counter
            slot.current_orders += 1
            slot.save()
            messages.success(request, f"Order placed successfully! Order #{order.id}")
            return redirect('my_orders')
    else:
        form = OrderForm()

    slots = TimeSlot.objects.filter(is_active=True).values(
        'id', 'slot_name', 'max_capacity', 'current_orders'
    )
    return render(request, 'student/order.html', {'form': form, 'slots': list(slots)})


@login_required
def my_orders(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    status_filter = request.GET.get('status', 'all')
    orders = Order.objects.filter(user=request.user).select_related('food_item', 'time_slot')
    if status_filter in ('Pending', 'Completed', 'Cancelled'):
        orders = orders.filter(status=status_filter)
    return render(request, 'student/my_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
    })
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'Pending':
        messages.warning(request, "Only Pending orders can be cancelled.")
        return redirect('my_orders')

    # Decrement slot counter
    slot = order.time_slot
    if slot.current_orders > 0:
        slot.current_orders -= 1
        slot.save()

    order.status = 'Cancelled'
    order.save()
    messages.info(request, f"Order #{order.id} has been cancelled.")
    return redirect('my_orders')

@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_dashboard(request):
    today = timezone.localdate()

    total_orders_today = Order.objects.filter(order_time__date=today).count()
    revenue_today      = Order.objects.filter(
        order_time__date=today, status__in=['Pending', 'Completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    pending_orders = Order.objects.filter(status='Pending').count()
    all_slots      = TimeSlot.objects.filter(is_active=True)
    recent_orders  = Order.objects.select_related('user', 'food_item', 'time_slot')[:10]

    context = {
        'total_orders_today': total_orders_today,
        'revenue_today':      revenue_today,
        'pending_orders':     pending_orders,
        'all_slots':          all_slots,
        'recent_orders':      recent_orders,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_food(request):
    """Admin: view all food items + add a new one."""
    food_items = FoodItem.objects.all()

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Food item added successfully.")
            return redirect('manage_food')
    else:
        form = FoodItemForm()

    return render(request, 'admin_dashboard/food_items.html', {
        'food_items': food_items, 'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def edit_food(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)

    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{item.name}' updated.")
            return redirect('manage_food')
    else:
        form = FoodItemForm(instance=item)

    return render(request, 'admin_dashboard/edit_food.html', {'form': form, 'item': item})


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_food(request, item_id):
    """Admin: delete a food item (POST only)."""
    item = get_object_or_404(FoodItem, id=item_id)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f"'{name}' deleted.")
    return redirect('manage_food')


@login_required
@user_passes_test(is_admin, login_url='/login/')
def manage_slots(request):
    """Admin: view all time slots + add a new one."""
    slots = TimeSlot.objects.all()

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Time slot added.")
            return redirect('manage_slots')
    else:
        form = TimeSlotForm()

    return render(request, 'admin_dashboard/time_slots.html', {
        'slots': slots, 'form': form
    })


@login_required
@user_passes_test(is_admin, login_url='/login/')
def edit_slot(request, slot_id):
    """Admin: edit a time slot."""
    slot = get_object_or_404(TimeSlot, id=slot_id)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, "Slot updated.")
            return redirect('manage_slots')
    else:
        form = TimeSlotForm(instance=slot)

    return render(request, 'admin_dashboard/edit_slot.html', {'form': form, 'slot': slot})


@login_required
@user_passes_test(is_admin, login_url='/login/')
def delete_slot(request, slot_id):
    """Admin: delete a time slot (POST only)."""
    slot = get_object_or_404(TimeSlot, id=slot_id)
    if request.method == 'POST':
        slot.delete()
        messages.success(request, "Slot deleted.")
    return redirect('manage_slots')


@login_required
@user_passes_test(is_admin, login_url='/login/')
def update_order_status(request, order_id):
    """Admin: mark an order as Completed or Cancelled."""
    order  = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')

    if status in ('Completed', 'Cancelled', 'Pending'):
        if order.status == 'Pending' and status == 'Cancelled':
            slot = order.time_slot
            if slot.current_orders > 0:
                slot.current_orders -= 1
                slot.save()
        order.status = status
        order.save()
        messages.success(request, f"Order #{order.id} marked as {status}.")

    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin, login_url='/login/')
def analytics_view(request):
    """
    Admin analytics page:
      - Bar chart data: orders per food item (last 7 days)
      - Peak slot detection
      - Basic demand prediction (7-day moving average)
    """
    today      = timezone.localdate()
    week_ago   = today - timedelta(days=6)  
    orders_by_item = (
        Order.objects
        .filter(order_time__date__gte=week_ago)
        .values('food_item__name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    slot_data = TimeSlot.objects.filter(is_active=True)
    predictions = []
    for item in FoodItem.objects.filter(is_available=True):
        past_orders = Order.objects.filter(
            food_item=item,
            order_time__date__gte=week_ago
        ).count()
        avg = round(past_orders / 7, 1)
        predictions.append({
            'food': item.name,
            'avg_per_day': avg,
            'high_demand': avg >= 5,   
        })
    predictions.sort(key=lambda x: x['avg_per_day'], reverse=True)
    chart_labels = [d['food_item__name'] for d in orders_by_item]
    chart_values = [d['total'] for d in orders_by_item]

    context = {
        'orders_by_item': orders_by_item,
        'slot_data':      slot_data,
        'predictions':    predictions,
        'chart_labels':   chart_labels,
        'chart_values':   chart_values,
        'week_ago':       week_ago,
        'today':          today,
    }
    return render(request, 'admin_dashboard/analytics.html', context)
