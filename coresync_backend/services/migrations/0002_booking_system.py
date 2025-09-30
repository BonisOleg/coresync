# Generated migration for booking system
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import uuid
from datetime import time as dt_time


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=100)),
                ('room_type', models.CharField(choices=[('mensuite', 'Mensuite Room'), ('private', 'Coresync Private Room'), ('shared', 'Shared Space'), ('vip', 'VIP Suite')], max_length=20)),
                ('capacity', models.PositiveIntegerField(default=1)),
                ('features', models.JSONField(default=list, help_text="List of room features (e.g., ['AI_massage_bed', 'smart_mirror', 'aromatherapy'])")),
                ('has_iot_control', models.BooleanField(default=True)),
                ('iot_device_ids', models.JSONField(default=list, help_text='List of connected IoT device IDs')),
                ('maintenance_mode', models.BooleanField(default=False)),
                ('opening_time', models.TimeField(default=dt_time(9, 0))),
                ('closing_time', models.TimeField(default=dt_time(21, 0))),
                ('premium_modifier', models.DecimalField(decimal_places=2, default=1.00, help_text='Multiplier for room pricing (1.0 = standard, 1.2 = 20% premium)', max_digits=5)),
            ],
            options={
                'verbose_name': 'Booking Room',
                'verbose_name_plural': 'Booking Rooms',
                'db_table': 'booking_rooms',
                'ordering': ['room_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('booking_reference', models.CharField(editable=False, help_text='Format: CS-YYYY-NNNNNN', max_length=20, unique=True)),
                ('guest_name', models.CharField(blank=True, help_text='For bookings made by members for guests', max_length=100)),
                ('guest_phone', models.CharField(blank=True, max_length=20)),
                ('guest_email', models.EmailField(blank=True, max_length=254)),
                ('booking_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('duration', models.PositiveIntegerField(help_text='Duration in minutes')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('no_show', 'No Show'), ('rescheduled', 'Rescheduled')], default='pending', max_length=20)),
                ('is_priority_booking', models.BooleanField(default=False, help_text='Priority bookings for members (2-3 months advance)')),
                ('booking_tier', models.CharField(choices=[('member_priority', 'Member Priority (2-3 months)'), ('member_standard', 'Member Standard'), ('non_member', 'Non-Member (3 days only)'), ('vip', 'VIP/Unlimited')], default='non_member', max_length=20)),
                ('ai_program', models.CharField(blank=True, help_text='Selected AI massage program', max_length=100)),
                ('scene_preferences', models.JSONField(default=dict, help_text='IoT scene settings (lighting, scent, temperature)')),
                ('special_requests', models.TextField(blank=True)),
                ('allergies_notes', models.TextField(blank=True)),
                ('medical_notes', models.TextField(blank=True, help_text='Staff only')),
                ('base_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('addons_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_applied', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('final_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('partial', 'Partially Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')], default='pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255)),
                ('booked_at', models.DateTimeField(auto_now_add=True)),
                ('confirmed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('cancellation_reason', models.TextField(blank=True)),
                ('assigned_technician', models.CharField(blank=True, max_length=100)),
                ('technician_notes', models.TextField(blank=True)),
                ('quickbooks_synced', models.BooleanField(default=False)),
                ('quickbooks_invoice_id', models.CharField(blank=True, max_length=100)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='services.room')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='services.service')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='users.user')),
            ],
            options={
                'verbose_name': 'Booking',
                'verbose_name_plural': 'Bookings',
                'db_table': 'bookings',
                'ordering': ['-booking_date', '-start_time'],
            },
        ),
        migrations.CreateModel(
            name='BookingAddon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('preferences', models.JSONField(blank=True, default=dict)),
                ('addon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.serviceaddon')),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking_addons', to='services.booking')),
            ],
            options={
                'verbose_name': 'Booking Add-on',
                'verbose_name_plural': 'Booking Add-ons',
                'db_table': 'booking_addons',
            },
        ),
        migrations.CreateModel(
            name='AvailabilitySlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('max_bookings', models.PositiveIntegerField(default=1)),
                ('current_bookings', models.PositiveIntegerField(default=0)),
                ('member_only_until', models.DateTimeField(help_text='Non-members can book after this date/time')),
                ('vip_only_until', models.DateTimeField(blank=True, help_text='VIP/Unlimited members get first access', null=True)),
                ('base_price_modifier', models.DecimalField(decimal_places=2, default=1.00, help_text='Price modifier for this slot (e.g., 1.5 for peak hours)', max_digits=5)),
                ('is_blocked', models.BooleanField(default=False)),
                ('block_reason', models.CharField(blank=True, max_length=255)),
                ('is_premium_slot', models.BooleanField(default=False)),
                ('tags', models.JSONField(default=list, help_text="Tags like ['peak_hour', 'weekend', 'holiday']")),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_slots', to='services.room')),
            ],
            options={
                'verbose_name': 'Availability Slot',
                'verbose_name_plural': 'Availability Slots',
                'db_table': 'availability_slots',
                'ordering': ['date', 'start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['user', 'booking_date'], name='bookings_user_id_39f1f2_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['booking_date', 'start_time'], name='bookings_booking_ec7f82_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['status', 'booking_date'], name='bookings_status_d7deba_idx'),
        ),
        migrations.AddIndex(
            model_name='availabilityslot',
            index=models.Index(fields=['date', 'room'], name='availabilit_date_ab4c13_idx'),
        ),
        migrations.AddIndex(
            model_name='availabilityslot',
            index=models.Index(fields=['member_only_until'], name='availabilit_member__3b4e91_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='bookingaddon',
            unique_together={('booking', 'addon')},
        ),
        migrations.AlterUniqueTogether(
            name='availabilityslot',
            unique_together={('date', 'start_time', 'room')},
        ),
        migrations.AddField(
            model_name='booking',
            name='addons',
            field=models.ManyToManyField(blank=True, through='services.BookingAddon', to='services.serviceaddon'),
        ),
    ]
