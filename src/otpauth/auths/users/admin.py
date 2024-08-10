from django.contrib import admin

from .models import BaseUser

# Register your models here.


@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_admin', 'is_active', 'created', 'updated')
    list_filter = ('is_admin','is_active', 'created', 'updated')
    search_fields = ('phone_number',)
    list_editable = ('is_admin', 'is_active')
