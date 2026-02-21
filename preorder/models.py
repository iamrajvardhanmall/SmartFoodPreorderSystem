
import random
from django.db import models
from django.contrib.auth.models import User



class FoodStall(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location    = models.CharField(max_length=150, blank=True,
                                   help_text="e.g., Block A Ground Floor, Near Main Gate")
    is_active   = models.BooleanField(default=True)
    image       = models.ImageField(upload_to='stall_images/', blank=True, null=True)
    def __str__(self):
        return self.name
    def available_items_count(self):
        return self.food_items.filter(is_available=True).count()
    class Meta:
        ordering = ['name']

class FoodItem(models.Model):
    stall           = models.ForeignKey(FoodStall, on_delete=models.CASCADE,
                                        null=True, blank=True, related_name='food_items')
    name            = models.CharField(max_length=100)
    description     = models.TextField(blank=True)
    price           = models.DecimalField(max_digits=6, decimal_places=2)
    available_qty   = models.PositiveIntegerField(default=50)
    is_available    = models.BooleanField(default=True)
    image           = models.ImageField(upload_to='food_images/', blank=True, null=True)
    def __str__(self):
        stall_name = self.stall.name if self.stall else "General"
        return f"[{stall_name}] {self.name} (₹{self.price})"
    class Meta:
        ordering = ['stall__name', 'name']

class TimeSlot(models.Model):
    slot_name       = models.CharField(max_length=50)   # e.g., "10:30 AM - 10:45 AM"
    max_capacity    = models.PositiveIntegerField(default=30)
    current_orders  = models.PositiveIntegerField(default=0)
    is_active       = models.BooleanField(default=True)
    def occupancy_percent(self):
        if self.max_capacity == 0:
            return 100
        return (self.current_orders / self.max_capacity) * 100
    def is_full(self):
        return self.current_orders >= self.max_capacity
    def is_peak(self):
        return self.occupancy_percent() >= 70
    def __str__(self):
        return self.slot_name
    class Meta:
        ordering = ['slot_name']


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user                  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    food_item             = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    time_slot             = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    quantity              = models.PositiveIntegerField(default=1)
    order_time            = models.DateTimeField(auto_now_add=True)  # Set automatically
    status                = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price           = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    special_instructions  = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        self.total_price = self.food_item.price * self.quantity
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Order #{self.id} — {self.user.username} — {self.food_item.name}"
    class Meta:
        ordering = ['-order_time']  # Newest first


class DemandAnalytics(models.Model):
    date         = models.DateField()
    food_item    = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='analytics')
    total_orders = models.PositiveIntegerField(default=0)
    def __str__(self):
        return f"{self.date} | {self.food_item.name} | {self.total_orders} orders"
    class Meta:
        unique_together = ('date', 'food_item')  # One record per item per day
        ordering = ['-date']


class StallOwner(models.Model):
    user       = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='stall_owner_profile'
    )
    stall      = models.ForeignKey(
        FoodStall, on_delete=models.CASCADE, related_name='owners'
    )
    stall_code = models.CharField(max_length=5, unique=True, blank=True,
                                  help_text='Auto-generated 5-digit owner ID')
    def save(self, *args, **kwargs):
        if not self.stall_code:
            for _ in range(100):          # try up to 100 times
                code = str(random.randint(10000, 99999))
                if not StallOwner.objects.filter(stall_code=code).exists():
                    self.stall_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} → {self.stall.name} (Code: {self.stall_code})"

    class Meta:
        ordering = ['stall__name']
