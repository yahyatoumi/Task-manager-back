# Generated by Django 4.2.11 on 2024-04-28 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanager', '0005_remove_task_room_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='color',
            field=models.CharField(default='#007bff', max_length=255),
        ),
    ]
