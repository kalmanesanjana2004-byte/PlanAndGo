"""
PackAndGo - Forms
All form definitions for user input and validation.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Driver, Booking, Review, Complaint, Payment


# ─────────────────────────────────────────────
# USER REGISTRATION
# ─────────────────────────────────────────────
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})


# ─────────────────────────────────────────────
# USER PROFILE
# ─────────────────────────────────────────────
class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ─────────────────────────────────────────────
# DRIVER REGISTRATION
# ─────────────────────────────────────────────
class DriverRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    class Meta:
        model = Driver
        fields = ['driver_name', 'email', 'phone', 'vehicle_type', 'vehicle_number', 
                  'license_number', 'city', 'profile_image']
        widgets = {
            'driver_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vehicle Number'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data


# ─────────────────────────────────────────────
# BOOKING FORM
# ─────────────────────────────────────────────
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['pickup_location', 'drop_location', 'pickup_city', 'drop_city',
                  'item_description', 'vehicle_type', 'booking_date', 'distance_km',
                  'item_image', 'special_instructions']
        widgets = {
            'pickup_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter pickup address'
            }),
            'drop_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter drop address'
            }),
            'pickup_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pickup City'
            }),
            'drop_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Drop City'
            }),
            'item_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe items to be transported'
            }),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'distance_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Distance in KM',
                'step': '0.1'
            }),
            'item_image': forms.FileInput(attrs={'class': 'form-control'}),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any special instructions (optional)'
            }),
        }


# ─────────────────────────────────────────────
# PAYMENT FORM
# ─────────────────────────────────────────────
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(),
        }


# ─────────────────────────────────────────────
# REVIEW FORM
# ─────────────────────────────────────────────
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }


# ─────────────────────────────────────────────
# COMPLAINT FORM
# ─────────────────────────────────────────────
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['booking', 'subject', 'description']
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Complaint Subject'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your issue in detail...'
            }),
        }
