# Generated by Django 2.2.7 on 2019-11-21 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0002_add_ordering_in_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='faqitem',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
