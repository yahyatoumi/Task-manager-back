# Generated by Django 4.2.11 on 2024-04-24 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0004_alter_task_created_by_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='room_id',
        ),
    ]
