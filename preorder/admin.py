from django.contrib import admin
from .models import FoodStall, FoodItem, TimeSlot, Order, DemandAnalytics, StallOwner
@admin.register(StallOwner)
class StallOwnerAdmin(admin.ModelAdmin):
    list_display  = ('stall_code', 'user', 'stall')
    search_fields = ('stall_code', 'user__username', 'stall__name')
    readonly_fields = ('stall_code',)
@admin.register(FoodStall)
class FoodStallAdmin(admin.ModelAdmin):
    list_display  = ('name', 'location', 'is_active', 'available_items_count')
    list_editable = ('is_active',)
    search_fields = ('name', 'location')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display  = ('name', 'stall', 'price', 'available_qty', 'is_available')
    list_editable = ('price', 'available_qty', 'is_available')
    search_fields = ('name', 'stall__name')
    list_filter   = ('is_available', 'stall')
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display  = ('slot_name', 'max_capacity', 'current_orders', 'is_active')
    list_editable = ('max_capacity', 'is_active')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user', 'food_item', 'stall_name', 'time_slot',
                     'quantity', 'total_price', 'status', 'order_time')
    list_filter   = ('status', 'time_slot', 'food_item__stall')
    search_fields = ('user__username', 'food_item__name', 'food_item__stall__name')
    list_editable = ('status',)
    ordering      = ('-order_time',)
    def stall_name(self, obj):
        return obj.food_item.stall.name if obj.food_item.stall else '—'
    stall_name.short_description = 'Stall'

@admin.register(DemandAnalytics)
class DemandAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'food_item', 'total_orders')
    list_filter  = ('date', 'food_item')
