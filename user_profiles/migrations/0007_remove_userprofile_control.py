# Generated by Django 2.1.7 on 2019-04-08 23:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profiles', '0006_change_meta_on_profile_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='control',
        ),
    ]
