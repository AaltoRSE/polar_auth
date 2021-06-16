from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User
from .models import Subscriber


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'consent', 'privacy', 'first_survey_done', 'is_active')
    list_filter = ('email', 'consent', 'privacy', 'first_survey_done', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'home_address', 'consent', 'privacy', 'first_survey_done', 'password', 'user_id')}),
        ('Permissions', {'fields': ('is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'home_address', 'consent', 'privacy', 'first_survey_done', 'password'
                       'is_superuser', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriber)
