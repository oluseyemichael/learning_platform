# Generated by Django 5.1.2 on 2024-11-15 09:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduleprogress',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='LearningPathProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('progress_percentage', models.FloatField(default=0.0)),
                ('learning_path', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.learningpath')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_path_progress', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
