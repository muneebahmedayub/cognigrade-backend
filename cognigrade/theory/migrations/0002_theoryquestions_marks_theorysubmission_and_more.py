# Generated by Django 5.1 on 2025-04-29 07:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('theory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='theoryquestions',
            name='marks',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='TheorySubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField()),
                ('answers', models.JSONField(default=list)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
                ('theory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='theory.theory')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TheorySubmissionAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('answer', models.TextField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='theory_answers', to='theory.theoryquestions')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='theory_answers', to='theory.theorysubmission')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
