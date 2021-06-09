from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from .models import Subscriber

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'consent', 'privacy', 'is_active',)
    list_filter = ('email', 'consent', 'privacy', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'consent', 'privacy', 'password')}),
        ('Permissions', {'fields': ('is_superuser','is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'consent', 'privacy', 'password', 'is_superuser', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriber)
