"""
PackAndGo - URL Routing
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Public Pages ──────────────────────────────
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),

    # ── Authentication ────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # ── User Dashboard ────────────────────────────
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('booking/new/', views.new_booking, name='new_booking'),
    path('booking/history/', views.booking_history, name='booking_history'),
    path('booking/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('booking/<int:pk>/payment/', views.payment_page, name='payment_page'),
    path('booking/<int:pk>/review/', views.submit_review, name='submit_review'),
    path('profile/', views.user_profile, name='user_profile'),
    path('complaint/', views.submit_complaint, name='submit_complaint'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),

    # ── API ───────────────────────────────────────
    path('api/calculate-price/', views.calculate_price_api, name='calculate_price_api'),

    # ── Driver ────────────────────────────────────
    path('driver/register/', views.driver_register, name='driver_register'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('driver/jobs/', views.driver_jobs, name='driver_jobs'),
    path('driver/jobs/<int:pk>/accept/', views.accept_booking, name='accept_booking'),
    path('driver/jobs/<int:pk>/update/', views.update_booking_status, name='update_booking_status'),
    path('driver/earnings/', views.driver_earnings, name='driver_earnings'),
    path('driver/toggle-availability/', views.toggle_availability, name='toggle_availability'),

    # ── Admin Panel ───────────────────────────────
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:pk>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('admin-panel/drivers/', views.admin_drivers, name='admin_drivers'),
    path('admin-panel/drivers/<int:pk>/action/', views.approve_driver, name='approve_driver'),
    path('admin-panel/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin-panel/payments/', views.admin_payments, name='admin_payments'),
    path('admin-panel/complaints/', views.admin_complaints, name='admin_complaints'),
]
