# Generated by Django 5.0.7 on 2024-08-11 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_failedattempt_remove_otprequest_password_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otprequest',
            name='user',
        ),
        migrations.AddField(
            model_name='otprequest',
            name='phone_number',
            field=models.CharField(max_length=13, null=True),
        ),
    ]
