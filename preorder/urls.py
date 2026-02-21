
from django.urls import path
from . import views

urlpatterns = [
    path('',               views.home_view,     name='home'),
    path('register/',      views.register_view, name='register'),
    path('login/',         views.login_view,    name='login'),
    path('logout/',        views.logout_view,   name='logout'),
    path('dashboard/',     views.student_dashboard, name='student_dashboard'),
    path('menu/',          views.menu_view,          name='menu'),
    path('order/',         views.place_order,         name='place_order'),
    path('my-orders/',     views.my_orders,           name='my_orders'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('admin-panel/',                           views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/stalls/',                    views.manage_stalls,   name='manage_stalls'),
    path('admin-panel/stalls/edit/<int:stall_id>/',   views.edit_stall,   name='edit_stall'),
    path('admin-panel/stalls/delete/<int:stall_id>/', views.delete_stall, name='delete_stall'),
    path('admin-panel/food/',                      views.manage_food,     name='manage_food'),
    path('admin-panel/food/edit/<int:item_id>/',   views.edit_food,       name='edit_food'),
    path('admin-panel/food/delete/<int:item_id>/', views.delete_food,     name='delete_food'),
    path('admin-panel/slots/',                     views.manage_slots,    name='manage_slots'),
    path('admin-panel/slots/edit/<int:slot_id>/',  views.edit_slot,       name='edit_slot'),
    path('admin-panel/slots/delete/<int:slot_id>/',views.delete_slot,     name='delete_slot'),
    path('admin-panel/orders/update/<int:order_id>/',
         views.update_order_status, name='update_order_status'),
    path('admin-panel/analytics/', views.analytics_view, name='analytics'),
    path('admin-panel/stall-owners/',
         views.manage_stall_owners, name='manage_stall_owners'),
    path('admin-panel/stall-owners/delete/<int:owner_id>/',
         views.delete_stall_owner, name='delete_stall_owner'),
    path('stall-owner/dashboard/',
         views.stall_owner_dashboard, name='stall_owner_dashboard'),
    path('stall-owner/orders/update/<int:order_id>/',
         views.stall_owner_update_order, name='stall_owner_update_order'),]

