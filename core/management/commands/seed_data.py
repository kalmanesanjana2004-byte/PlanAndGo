"""
PackAndGo - Seed Data Command
Creates sample data for development and testing.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random

from core.models import UserProfile, Driver, Booking, Payment, Review, Notification


class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding PackAndGo database...')

        # ── Create Superuser ──────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@packandgo.in',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✅ Admin created: admin / admin123'))
        else:
            admin = User.objects.get(username='admin')

        # ── Create Sample Users ───────────────────────────
        users_data = [
            ('rahul_sharma', 'Rahul', 'Sharma', 'rahul@example.com', '9876543210', 'Mumbai'),
            ('priya_patel', 'Priya', 'Patel', 'priya@example.com', '9876543211', 'Delhi'),
            ('amit_kumar', 'Amit', 'Kumar', 'amit@example.com', '9876543212', 'Bangalore'),
            ('sneha_gupta', 'Sneha', 'Gupta', 'sneha@example.com', '9876543213', 'Chennai'),
        ]

        created_users = []
        for username, first, last, email, phone, city in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, password='user123',
                    first_name=first, last_name=last, email=email
                )
                UserProfile.objects.create(user=user, phone=phone, city=city)
                created_users.append(user)
            else:
                created_users.append(User.objects.get(username=username))

        self.stdout.write(self.style.SUCCESS(f'✅ {len(users_data)} users created (password: user123)'))

        # ── Create Sample Drivers ─────────────────────────
        drivers_data = [
            ('Ravi Kumar', 'ravi@driver.com', '9111111111', 'mini_truck', 'MH01AB1234', 'DL123456', 'Mumbai'),
            ('Suresh Singh', 'suresh@driver.com', '9111111112', 'pickup_van', 'DL02CD5678', 'DL789012', 'Delhi'),
            ('Mohan Das', 'mohan@driver.com', '9111111113', 'tempo', 'KA03EF9012', 'KA345678', 'Bangalore'),
            ('Vijay Yadav', 'vijay@driver.com', '9111111114', 'bike', 'TN04GH3456', 'TN901234', 'Chennai'),
            ('Arun Verma', 'arun@driver.com', '9111111115', 'large_truck', 'GJ05IJ7890', 'GJ567890', 'Ahmedabad'),
        ]

        created_drivers = []
        for name, email, phone, vtype, vnum, lic, city in drivers_data:
            if not Driver.objects.filter(email=email).exists():
                username = email.split('@')[0]
                duser = User.objects.create_user(
                    username=username, password='driver123',
                    first_name=name.split()[0], email=email
                )
                driver = Driver.objects.create(
                    user=duser, driver_name=name, email=email, phone=phone,
                    vehicle_type=vtype, vehicle_number=vnum, license_number=lic,
                    city=city, status='approved', availability=True,
                    rating=round(random.uniform(3.5, 5.0), 1),
                    total_trips=random.randint(10, 100),
                    total_earnings=random.randint(5000, 50000)
                )
                created_drivers.append(driver)
            else:
                created_drivers.append(Driver.objects.get(email=email))

        self.stdout.write(self.style.SUCCESS(f'✅ {len(drivers_data)} drivers created (password: driver123)'))

        # ── Create Sample Bookings ────────────────────────
        vehicle_types = ['bike', 'mini_truck', 'pickup_van', 'tempo', 'large_truck']
        statuses = ['delivered', 'delivered', 'delivered', 'in_transit', 'confirmed', 'pending']
        routes = [
            ('123 MG Road, Mumbai', 'Mumbai', '456 Linking Road, Pune', 'Pune', 150),
            ('Connaught Place, Delhi', 'Delhi', 'Sector 18, Noida', 'Noida', 25),
            ('Koramangala, Bangalore', 'Bangalore', 'Whitefield, Bangalore', 'Bangalore', 15),
            ('Anna Nagar, Chennai', 'Chennai', 'OMR Road, Chennai', 'Chennai', 20),
            ('Navrangpura, Ahmedabad', 'Ahmedabad', 'Surat City Center', 'Surat', 280),
        ]

        for i, user in enumerate(created_users):
            for j in range(3):
                route = random.choice(routes)
                vtype = random.choice(vehicle_types)
                status = random.choice(statuses)
                driver = random.choice(created_drivers) if status != 'pending' else None
                days_ago = random.randint(1, 60)
                bdate = date.today() - timedelta(days=days_ago)

                from core.views import calculate_price
                price = calculate_price(vtype, route[4])

                booking = Booking.objects.create(
                    user=user,
                    driver=driver,
                    pickup_location=route[0],
                    pickup_city=route[1],
                    drop_location=route[2],
                    drop_city=route[3],
                    item_description=random.choice([
                        'Household furniture and appliances',
                        'Office equipment and files',
                        'Luggage and personal items',
                        'Electronic goods',
                        'Boxes and packages'
                    ]),
                    vehicle_type=vtype,
                    booking_date=bdate,
                    delivery_date=bdate + timedelta(days=1) if status == 'delivered' else None,
                    status=status,
                    estimated_price=price,
                    distance_km=route[4],
                )

                # Create payment
                pay_status = 'completed' if status == 'delivered' else 'pending'
                Payment.objects.create(
                    booking=booking,
                    amount=price,
                    payment_method=random.choice(['cash', 'upi', 'card']),
                    payment_status=pay_status,
                    transaction_id=f'TXN{random.randint(100000, 999999)}' if pay_status == 'completed' else '',
                    paid_at=timezone.now() if pay_status == 'completed' else None,
                )

                # Create review for delivered bookings
                if status == 'delivered' and driver:
                    Review.objects.get_or_create(
                        user=user, driver=driver, booking=booking,
                        defaults={
                            'rating': random.randint(3, 5),
                            'comment': random.choice([
                                'Excellent service! Very professional driver.',
                                'Good experience, items delivered safely.',
                                'On time delivery, would recommend.',
                                'Driver was helpful and careful with items.',
                                'Great service, will use again!',
                            ])
                        }
                    )

                # Notification
                Notification.objects.create(
                    user=user,
                    message=f'Booking #{booking.id} status: {booking.get_status_display()}',
                    notif_type='booking'
                )

        self.stdout.write(self.style.SUCCESS('✅ Sample bookings, payments, and reviews created'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Database seeded successfully!'))
        self.stdout.write('')
        self.stdout.write('📋 Login Credentials:')
        self.stdout.write('   Admin:  admin / admin123  → /admin-panel/')
        self.stdout.write('   User:   rahul_sharma / user123  → /dashboard/')
        self.stdout.write('   Driver: ravi / driver123  → /driver/dashboard/')
        self.stdout.write('')
        self.stdout.write('🚀 Run: python manage.py runserver')
