"""
PackAndGo - Views
All view functions for the transportation management system.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
import json
import random
import string
import functools

from .models import (
    UserProfile, Driver, Booking, Payment, Review,
    Notification, Complaint, VEHICLE_BASE_PRICE
)
from .forms import (
    UserRegistrationForm, UserProfileForm, DriverRegistrationForm,
    BookingForm, PaymentForm, ReviewForm, ComplaintForm
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def calculate_price(vehicle_type, distance_km):
    """AI-based dynamic price estimation."""
    base = VEHICLE_BASE_PRICE.get(vehicle_type, 200)
    distance = float(distance_km) if distance_km else 10
    # Price formula: base + (distance * per_km_rate) + handling_fee
    per_km_rates = {
        'bike': 8, 'mini_truck': 15, 'pickup_van': 18,
        'tempo': 22, 'large_truck': 30
    }
    rate = per_km_rates.get(vehicle_type, 15)
    handling = base * 0.1
    price = base + (distance * rate) + handling
    return round(price, 2)


def add_notification(user, message, notif_type='system'):
    """Helper to create a notification for a user."""
    Notification.objects.create(user=user, message=message, notif_type=notif_type)


def generate_transaction_id():
    """Generate a random transaction ID."""
    return 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


# ─────────────────────────────────────────────
# PUBLIC PAGES
# ─────────────────────────────────────────────
def landing(request):
    """Landing / Home page."""
    stats = {
        'total_bookings': Booking.objects.count(),
        'total_drivers': Driver.objects.filter(status='approved').count(),
        'total_users': User.objects.filter(is_staff=False).count(),
        'cities_covered': 50,
    }
    reviews = Review.objects.select_related('user', 'driver').order_by('-created_at')[:6]
    return render(request, 'public/landing.html', {'stats': stats, 'reviews': reviews})


def about(request):
    return render(request, 'public/about.html')


def services(request):
    return render(request, 'public/services.html')


def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Your message has been sent! We will get back to you soon.')
        return redirect('contact')
    return render(request, 'public/contact.html')


# ─────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────
def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
            )
            add_notification(user, 'Welcome to PackAndGo! Your account has been created.', 'system')
            login(request, user)
            messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """User/Driver/Admin login."""
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            # Redirect based on role
            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')
            try:
                driver = user.driver_profile
                return redirect('driver_dashboard')
            except Driver.DoesNotExist:
                pass
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('landing')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            messages.success(request, 'Password reset link has been sent to your email.')
        else:
            messages.error(request, 'No account found with this email address.')
    return render(request, 'auth/forgot_password.html')


# ─────────────────────────────────────────────
# USER DASHBOARD
# ─────────────────────────────────────────────
@login_required
def user_dashboard(request):
    """Main user dashboard."""
    bookings = Booking.objects.filter(user=request.user)
    recent_bookings = bookings.order_by('-created_at')[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    stats = {
        'total_bookings': bookings.count(),
        'active_bookings': bookings.filter(status__in=['pending', 'confirmed', 'picked_up', 'in_transit']).count(),
        'completed_bookings': bookings.filter(status='delivered').count(),
        'total_spent': bookings.filter(status='delivered').aggregate(
            total=Sum('estimated_price'))['total'] or 0,
    }

    return render(request, 'user/dashboard.html', {
        'recent_bookings': recent_bookings,
        'stats': stats,
        'notifications': notifications,
    })


@login_required
def new_booking(request):
    """Create a new booking."""
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # Calculate price
            booking.estimated_price = calculate_price(
                booking.vehicle_type,
                booking.distance_km
            )
            booking.save()

            # Create payment record
            Payment.objects.create(
                booking=booking,
                amount=booking.estimated_price,
                payment_status='pending'
            )

            add_notification(
                request.user,
                f'Booking #{booking.id} created successfully! Estimated price: ₹{booking.estimated_price}',
                'booking'
            )
            messages.success(request, f'Booking created! Estimated price: ₹{booking.estimated_price}')
            return redirect('booking_detail', pk=booking.id)
        else:
            messages.error(request, 'Please fix the errors in the form.')
    else:
        form = BookingForm()

    return render(request, 'user/new_booking.html', {'form': form})


@login_required
def booking_history(request):
    """View all bookings with filtering."""
    bookings = Booking.objects.filter(user=request.user)

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Search
    search = request.GET.get('search', '')
    if search:
        bookings = bookings.filter(
            Q(pickup_location__icontains=search) |
            Q(drop_location__icontains=search) |
            Q(item_description__icontains=search)
        )

    paginator = Paginator(bookings, 10)
    page = request.GET.get('page', 1)
    bookings_page = paginator.get_page(page)

    return render(request, 'user/booking_history.html', {
        'bookings': bookings_page,
        'status_filter': status_filter,
        'search': search,
    })


@login_required
def booking_detail(request, pk):
    """Booking detail / tracking page."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    payment = getattr(booking, 'payment', None)
    review = getattr(booking, 'review', None)
    review_form = ReviewForm() if booking.status == 'delivered' and not review else None

    return render(request, 'user/booking_detail.html', {
        'booking': booking,
        'payment': payment,
        'review': review,
        'review_form': review_form,
    })


@login_required
def payment_page(request, pk):
    """Payment page for a booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    payment = getattr(booking, 'payment', None)

    if payment and payment.payment_status == 'completed':
        messages.info(request, 'Payment already completed.')
        return redirect('booking_detail', pk=pk)

    if request.method == 'POST':
        method = request.POST.get('payment_method', 'cash')
        if payment:
            payment.payment_method = method
            payment.payment_status = 'completed'
            payment.transaction_id = generate_transaction_id()
            payment.paid_at = timezone.now()
            payment.save()
        else:
            Payment.objects.create(
                booking=booking,
                amount=booking.estimated_price,
                payment_method=method,
                payment_status='completed',
                transaction_id=generate_transaction_id(),
                paid_at=timezone.now()
            )

        add_notification(
            request.user,
            f'Payment of ₹{booking.estimated_price} completed for Booking #{booking.id}.',
            'payment'
        )
        messages.success(request, 'Payment successful!')
        return redirect('booking_detail', pk=pk)

    return render(request, 'user/payment.html', {'booking': booking, 'payment': payment})


@login_required
def submit_review(request, pk):
    """Submit a review for a completed booking."""
    booking = get_object_or_404(Booking, pk=pk, user=request.user)

    if booking.status != 'delivered':
        messages.error(request, 'You can only review completed bookings.')
        return redirect('booking_detail', pk=pk)

    if hasattr(booking, 'review'):
        messages.info(request, 'You have already reviewed this booking.')
        return redirect('booking_detail', pk=pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid() and booking.driver:
            review = form.save(commit=False)
            review.user = request.user
            review.driver = booking.driver
            review.booking = booking
            review.save()

            # Update driver rating
            driver = booking.driver
            avg = Review.objects.filter(driver=driver).aggregate(avg=Avg('rating'))['avg']
            driver.rating = round(avg, 2)
            driver.save()

            messages.success(request, 'Thank you for your review!')
    return redirect('booking_detail', pk=pk)


@login_required
def user_profile(request):
    """User profile management."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User model fields
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })

    return render(request, 'user/profile.html', {'form': form, 'profile': profile})


@login_required
def submit_complaint(request):
    """Submit a complaint."""
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully. We will review it shortly.')
            return redirect('user_dashboard')
    else:
        user_bookings = Booking.objects.filter(user=request.user)
        form = ComplaintForm()
        form.fields['booking'].queryset = user_bookings

    return render(request, 'user/complaint.html', {'form': form})


@login_required
def mark_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


# ─────────────────────────────────────────────
# PRICE CALCULATOR API
# ─────────────────────────────────────────────
def calculate_price_api(request):
    """AJAX endpoint for dynamic price calculation."""
    vehicle_type = request.GET.get('vehicle_type', 'mini_truck')
    distance = request.GET.get('distance', 10)
    try:
        price = calculate_price(vehicle_type, float(distance))
    except (ValueError, TypeError):
        price = 0
    return JsonResponse({'price': price})


# ─────────────────────────────────────────────
# DRIVER VIEWS
# ─────────────────────────────────────────────
def driver_register(request):
    """Driver registration."""
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save(commit=False)
            # Create a Django user for the driver
            username = form.cleaned_data['email'].split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['driver_name'].split()[0],
            )
            driver.user = user
            driver.save()
            messages.success(request, 'Registration submitted! Await admin approval.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = DriverRegistrationForm()

    return render(request, 'driver/register.html', {'form': form})


def driver_required(view_func):
    """Decorator to ensure user is an approved driver."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            driver = request.user.driver_profile
            if driver.status != 'approved':
                messages.error(request, 'Your driver account is pending approval.')
                return redirect('login')
        except Driver.DoesNotExist:
            messages.error(request, 'Driver profile not found.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@driver_required
def driver_dashboard(request):
    """Driver dashboard."""
    driver = request.user.driver_profile
    jobs = Booking.objects.filter(driver=driver)
    active_jobs = jobs.filter(status__in=['confirmed', 'picked_up', 'in_transit'])
    recent_jobs = jobs.order_by('-created_at')[:5]

    stats = {
        'total_jobs': jobs.count(),
        'active_jobs': active_jobs.count(),
        'completed_jobs': jobs.filter(status='delivered').count(),
        'total_earnings': driver.total_earnings,
        'rating': driver.rating,
    }

    # Available bookings matching driver's vehicle type
    available_bookings = Booking.objects.filter(
        status='pending',
        vehicle_type=driver.vehicle_type,
        driver__isnull=True
    ).order_by('-created_at')[:10]

    return render(request, 'driver/dashboard.html', {
        'driver': driver,
        'stats': stats,
        'active_jobs': active_jobs,
        'recent_jobs': recent_jobs,
        'available_bookings': available_bookings,
    })


@driver_required
def driver_jobs(request):
    """Driver's assigned jobs."""
    driver = request.user.driver_profile
    jobs = Booking.objects.filter(driver=driver)

    status_filter = request.GET.get('status', '')
    if status_filter:
        jobs = jobs.filter(status=status_filter)

    paginator = Paginator(jobs, 10)
    page = request.GET.get('page', 1)
    jobs_page = paginator.get_page(page)

    return render(request, 'driver/jobs.html', {
        'jobs': jobs_page,
        'status_filter': status_filter,
        'driver': request.user.driver_profile,
    })


@driver_required
def accept_booking(request, pk):
    """Driver accepts a booking."""
    booking = get_object_or_404(Booking, pk=pk, status='pending', driver__isnull=True)
    driver = request.user.driver_profile

    if booking.vehicle_type != driver.vehicle_type:
        messages.error(request, 'This booking requires a different vehicle type.')
        return redirect('driver_dashboard')

    booking.driver = driver
    booking.status = 'confirmed'
    booking.save()

    add_notification(
        booking.user,
        f'Your booking #{booking.id} has been accepted by driver {driver.driver_name}!',
        'booking'
    )
    messages.success(request, f'Booking #{booking.id} accepted!')
    return redirect('driver_dashboard')


@driver_required
def update_booking_status(request, pk):
    """Driver updates booking status."""
    booking = get_object_or_404(Booking, pk=pk, driver=request.user.driver_profile)
    driver = request.user.driver_profile

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_transitions = {
            'confirmed': ['picked_up'],
            'picked_up': ['in_transit'],
            'in_transit': ['delivered'],
        }

        if new_status in valid_transitions.get(booking.status, []):
            booking.status = new_status
            if new_status == 'delivered':
                booking.delivery_date = timezone.now().date()
                # Update driver earnings
                driver.total_earnings += booking.estimated_price
                driver.total_trips += 1
                driver.save()
                # Mark payment as completed if cash
                payment = getattr(booking, 'payment', None)
                if payment and payment.payment_method == 'cash':
                    payment.payment_status = 'completed'
                    payment.paid_at = timezone.now()
                    payment.save()
            booking.save()

            add_notification(
                booking.user,
                f'Your booking #{booking.id} status updated to: {booking.get_status_display()}',
                'booking'
            )
            messages.success(request, f'Status updated to {booking.get_status_display()}')
        else:
            messages.error(request, 'Invalid status transition.')

    return redirect('driver_jobs')


@driver_required
def driver_earnings(request):
    """Driver earnings page."""
    driver = request.user.driver_profile
    completed_jobs = Booking.objects.filter(driver=driver, status='delivered')

    # Monthly earnings data for chart
    monthly_data = {}
    for booking in completed_jobs:
        month = booking.delivery_date.strftime('%b %Y') if booking.delivery_date else 'Unknown'
        monthly_data[month] = monthly_data.get(month, 0) + float(booking.estimated_price)

    return render(request, 'driver/earnings.html', {
        'driver': driver,
        'completed_jobs': completed_jobs[:20],
        'monthly_data': json.dumps(monthly_data),
    })


@driver_required
def toggle_availability(request):
    """Toggle driver availability."""
    driver = request.user.driver_profile
    driver.availability = not driver.availability
    driver.save()
    status = 'available' if driver.availability else 'unavailable'
    messages.success(request, f'You are now {status}.')
    return redirect('driver_dashboard')


# ─────────────────────────────────────────────
# ADMIN VIEWS
# ─────────────────────────────────────────────
def admin_required(view_func):
    """Decorator to ensure user is admin/staff."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Admin access required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_dashboard(request):
    """Admin analytics dashboard."""
    # Core stats
    stats = {
        'total_users': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'total_drivers': Driver.objects.count(),
        'approved_drivers': Driver.objects.filter(status='approved').count(),
        'pending_drivers': Driver.objects.filter(status='pending').count(),
        'total_bookings': Booking.objects.count(),
        'active_bookings': Booking.objects.filter(
            status__in=['pending', 'confirmed', 'picked_up', 'in_transit']).count(),
        'completed_bookings': Booking.objects.filter(status='delivered').count(),
        'total_revenue': Payment.objects.filter(
            payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0,
        'open_complaints': Complaint.objects.filter(status='open').count(),
    }

    # Recent bookings
    recent_bookings = Booking.objects.select_related('user', 'driver').order_by('-created_at')[:10]

    # Booking status distribution for chart
    status_data = {}
    for choice in Booking.STATUS_CHOICES:
        count = Booking.objects.filter(status=choice[0]).count()
        status_data[choice[1]] = count

    # Vehicle type distribution
    vehicle_data = {}
    for choice in Booking._meta.get_field('vehicle_type').choices:
        count = Booking.objects.filter(vehicle_type=choice[0]).count()
        vehicle_data[choice[1]] = count

    # Monthly revenue for chart
    from django.db.models.functions import TruncMonth
    monthly_revenue = Payment.objects.filter(
        payment_status='completed'
    ).annotate(month=TruncMonth('paid_at')).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')[:12]

    monthly_labels = [str(m['month'].strftime('%b %Y')) if m['month'] else '' for m in monthly_revenue]
    monthly_values = [float(m['total']) for m in monthly_revenue]

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_bookings': recent_bookings,
        'status_data': json.dumps(status_data),
        'vehicle_data': json.dumps(vehicle_data),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_values': json.dumps(monthly_values),
    })


@admin_required
def admin_users(request):
    """Manage users."""
    search = request.GET.get('search', '')
    users = User.objects.filter(is_staff=False, is_superuser=False).select_related('profile')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search)
        )
    paginator = Paginator(users, 15)
    page = request.GET.get('page', 1)
    return render(request, 'admin_panel/users.html', {
        'users': paginator.get_page(page),
        'search': search,
    })


@admin_required
def admin_drivers(request):
    """Manage drivers."""
    status_filter = request.GET.get('status', '')
    drivers = Driver.objects.all()
    if status_filter:
        drivers = drivers.filter(status=status_filter)

    paginator = Paginator(drivers, 15)
    page = request.GET.get('page', 1)
    return render(request, 'admin_panel/drivers.html', {
        'drivers': paginator.get_page(page),
        'status_filter': status_filter,
    })


@admin_required
def approve_driver(request, pk):
    """Approve or reject a driver."""
    driver = get_object_or_404(Driver, pk=pk)
    action = request.POST.get('action', 'approve')

    if action == 'approve':
        driver.status = 'approved'
        driver.save()
        if driver.user:
            add_notification(driver.user, 'Congratulations! Your driver account has been approved.', 'driver')
        messages.success(request, f'Driver {driver.driver_name} approved.')
    elif action == 'reject':
        driver.status = 'rejected'
        driver.save()
        if driver.user:
            add_notification(driver.user, 'Your driver application has been rejected.', 'driver')
        messages.warning(request, f'Driver {driver.driver_name} rejected.')
    elif action == 'suspend':
        driver.status = 'suspended'
        driver.save()
        messages.warning(request, f'Driver {driver.driver_name} suspended.')

    return redirect('admin_drivers')


@admin_required
def admin_bookings(request):
    """Manage all bookings."""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    bookings = Booking.objects.select_related('user', 'driver').all()

    if status_filter:
        bookings = bookings.filter(status=status_filter)
    if search:
        bookings = bookings.filter(
            Q(user__username__icontains=search) |
            Q(pickup_location__icontains=search) |
            Q(drop_location__icontains=search)
        )

    paginator = Paginator(bookings, 15)
    page = request.GET.get('page', 1)
    return render(request, 'admin_panel/bookings.html', {
        'bookings': paginator.get_page(page),
        'status_filter': status_filter,
        'search': search,
    })


@admin_required
def admin_payments(request):
    """View all payments."""
    payments = Payment.objects.select_related('booking__user').order_by('-created_at')
    total_revenue = payments.filter(payment_status='completed').aggregate(
        total=Sum('amount'))['total'] or 0

    paginator = Paginator(payments, 15)
    page = request.GET.get('page', 1)
    return render(request, 'admin_panel/payments.html', {
        'payments': paginator.get_page(page),
        'total_revenue': total_revenue,
    })


@admin_required
def admin_complaints(request):
    """Manage complaints."""
    complaints = Complaint.objects.select_related('user', 'booking').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        response = request.POST.get('admin_response', '')
        new_status = request.POST.get('status', 'resolved')
        complaint = get_object_or_404(Complaint, pk=complaint_id)
        complaint.admin_response = response
        complaint.status = new_status
        complaint.save()
        messages.success(request, 'Complaint updated.')
        return redirect('admin_complaints')

    paginator = Paginator(complaints, 15)
    page = request.GET.get('page', 1)
    return render(request, 'admin_panel/complaints.html', {
        'complaints': paginator.get_page(page),
        'status_filter': status_filter,
    })


@admin_required
def toggle_user_status(request, pk):
    """Activate/deactivate a user."""
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_users')
