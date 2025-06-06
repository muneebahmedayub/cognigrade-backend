# Generated by Django 5.1 on 2025-04-30 04:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('omr', '0003_alter_omrquestions_omr'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OMRSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField()),
                ('omr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='omr.omr')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='omr_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
