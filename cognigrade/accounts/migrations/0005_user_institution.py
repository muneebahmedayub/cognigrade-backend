# Generated by Django 5.1 on 2024-09-03 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_first_name_user_last_name'),
        ('institutions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='institution_admin', to='institutions.institutions'),
        ),
    ]
