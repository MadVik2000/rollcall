# Generated by Django 5.1 on 2024-08-28 15:36

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Roster",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("date_deleted", models.DateTimeField(blank=True, null=True)),
                ("title", models.CharField(max_length=256)),
                ("is_active", models.BooleanField(default=False)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Roster",
                "verbose_name_plural": "Rosters",
            },
        ),
        migrations.CreateModel(
            name="RosterManager",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("date_deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "manager",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "roster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rosters.roster"
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Roster Manager",
                "verbose_name_plural": "Roster Managers",
                "constraints": [
                    models.UniqueConstraint(
                        fields=("roster", "manager"),
                        name="roster_manager_unique_constraint",
                        violation_error_message="User is already manager for this roster.",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="RosterUserSchedule",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("date_deleted", models.DateTimeField(blank=True, null=True)),
                ("schedule_date", models.DateField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "roster",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="rosters.roster"
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Roster User Schedule",
                "verbose_name_plural": "Roster User Schedules",
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("date_deleted__isnull", True)),
                        fields=("roster", "user", "schedule_date"),
                        name="roster_user_schedule_date_unique_constraint",
                        violation_error_message="Staff user can only have one active schedule on a day.",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="ScheduleSwapRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("date_updated", models.DateTimeField(auto_now=True)),
                ("date_deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "Pending"), (2, "Accepted"), (3, "Rejected")],
                        default=1,
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_created_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "receiver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="receiver",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sender",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender_schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="rosters.rosteruserschedule",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(class)s_updated_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Schedule Swap Request",
                "verbose_name_plural": "Schedule Swap Requests",
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("date_deleted__isnull", True)),
                        fields=("sender", "receiver", "sender_schedule"),
                        name="sender_receiver_sender_schedule_unique_constraint",
                        violation_error_message="A swap request already exists.",
                    )
                ],
            },
        ),
    ]
