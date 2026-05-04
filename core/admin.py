"""
PackAndGo - Django Admin Configuration
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Driver, Booking, Payment, Review, Notification, Complaint


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['driver_name', 'email', 'vehicle_type', 'status', 'availability', 'rating', 'total_trips']
    list_filter = ['status', 'vehicle_type', 'availability']
    search_fields = ['driver_name', 'email', 'phone', 'vehicle_number']
    list_editable = ['status', 'availability']
    readonly_fields = ['total_earnings', 'rating', 'total_trips']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'driver', 'vehicle_type', 'status', 'estimated_price', 'booking_date', 'created_at']
    list_filter = ['status', 'vehicle_type', 'booking_date']
    search_fields = ['user__username', 'pickup_location', 'drop_location']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']

    def colored_status(self, obj):
        colors = {
            'pending': 'orange', 'confirmed': 'blue', 'picked_up': 'purple',
            'in_transit': 'teal', 'delivered': 'green', 'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'payment_method', 'payment_status', 'transaction_id', 'paid_at']
    list_filter = ['payment_status', 'payment_method']
    search_fields = ['booking__id', 'transaction_id']
    readonly_fields = ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'driver', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['user__username', 'driver__driver_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'notif_type', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']
    search_fields = ['user__username', 'message']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username', 'subject']


# Customize admin site
admin.site.site_header = "PackAndGo Administration"
admin.site.site_title = "PackAndGo Admin"
admin.site.index_title = "Welcome to PackAndGo Admin Panel"
