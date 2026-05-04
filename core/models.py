"""
PackAndGo - Core Models
Defines all database models for the transportation management system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ─────────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username


# ─────────────────────────────────────────────
# VEHICLE TYPES
# ─────────────────────────────────────────────
VEHICLE_CHOICES = [
    ('bike', 'Bike Delivery'),
    ('mini_truck', 'Mini Truck'),
    ('pickup_van', 'Pickup Van'),
    ('tempo', 'Tempo'),
    ('large_truck', 'Large Truck'),
]

VEHICLE_BASE_PRICE = {
    'bike': 50,
    'mini_truck': 200,
    'pickup_van': 300,
    'tempo': 400,
    'large_truck': 600,
}


# ─────────────────────────────────────────────
# DRIVER
# ─────────────────────────────────────────────
class Driver(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile', null=True, blank=True)
    driver_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=30)
    availability = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    profile_image = models.ImageField(upload_to='drivers/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_trips = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver_name} - {self.get_vehicle_type_display()}"


# ─────────────────────────────────────────────
# BOOKING
# ─────────────────────────────────────────────
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    pickup_city = models.CharField(max_length=100, blank=True)
    drop_city = models.CharField(max_length=100, blank=True)
    item_description = models.TextField()
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES)
    booking_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    item_image = models.ImageField(upload_to='bookings/', blank=True, null=True)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.user.username} ({self.status})"

    @property
    def status_percentage(self):
        """Returns progress percentage for status tracking UI."""
        mapping = {
            'pending': 10,
            'confirmed': 30,
            'picked_up': 55,
            'in_transit': 75,
            'delivered': 100,
            'cancelled': 0,
        }
        return mapping.get(self.status, 0)

    @property
    def status_color(self):
        mapping = {
            'pending': 'warning',
            'confirmed': 'info',
            'picked_up': 'primary',
            'in_transit': 'purple',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return mapping.get(self.status, 'secondary')


# ─────────────────────────────────────────────
# PAYMENT
# ─────────────────────────────────────────────
class Payment(models.Model):
    METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cash')
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking #{self.booking.id} - ₹{self.amount}"


# ─────────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────────
class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='reviews')
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.driver.driver_name} - {self.rating}★"


# ─────────────────────────────────────────────
# NOTIFICATION
# ─────────────────────────────────────────────
class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking', 'Booking Update'),
        ('payment', 'Payment'),
        ('driver', 'Driver Update'),
        ('system', 'System'),
        ('promo', 'Promotion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


# ─────────────────────────────────────────────
# COMPLAINT
# ─────────────────────────────────────────────
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Complaint #{self.id} by {self.user.username} - {self.status}"
