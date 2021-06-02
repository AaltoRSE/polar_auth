from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from .models import Subscriber

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'consent', 'is_staff', 'is_active',)
    list_filter = ('email', 'consent', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'consent', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'consent', 'password', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriber)
