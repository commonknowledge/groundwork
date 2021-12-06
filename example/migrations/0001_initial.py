# Generated by Django 3.2.9 on 2021-12-03 09:07

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Party",
            fields=[
                ("last_sync_time", models.DateTimeField()),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("external_id", models.IntegerField()),
                ("name", models.CharField(max_length=512)),
                ("foreground_colour", models.CharField(max_length=16, null=True)),
                ("background_colour", models.CharField(max_length=16, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="MP",
            fields=[
                ("last_sync_time", models.DateTimeField()),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("external_id", models.IntegerField()),
                ("name_display_as", models.CharField(max_length=512)),
                ("thumbnail_url", models.URLField(max_length=512)),
                (
                    "latest_party",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="example.party",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Constituency",
            fields=[
                ("last_sync_time", models.DateTimeField()),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("external_id", models.IntegerField()),
                ("name", models.CharField(max_length=512)),
                ("ons_code", models.CharField(max_length=512)),
                (
                    "current_mp",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="example.mp",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]