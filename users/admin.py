from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail

from survey.models.response import Response

from users.models import User, Subscriber
from users.data_server import get_ids_with_data
from users.filters import SurveyNotDoneFilter

from polar_auth.settings import DEFAULT_FROM_EMAIL as from_address


@admin.action(description='Send email')
def admin_email(adminobject, request, queryset):
    if 'apply' in request.POST:
        subject = request.POST['subject']
        message = request.POST['message']
        html_message = request.POST['html_message']
        for object in queryset:
            send_mail(
                subject, message, from_address,
                [object.email],
                html_message=html_message, fail_silently=False,
            )

            object.has_received_email = True
            object.save()

        adminobject.message_user(request, f"Sent email to {queryset.count()} addresses.")
        return HttpResponseRedirect(request.get_full_path())

    context = {'queryset': queryset, 'count': queryset.count()}
    return render(request, 'admin/send_email.html', context=context)


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'consent', 'privacy', 'first_survey_done', 'authorized', 'device_sent', 'get_received_data')
    list_filter = ('email', 'consent', 'privacy', 'first_survey_done', 'authorized', 'device_sent', 'received_data', 'filled_surveys', SurveyNotDoneFilter, 'dropped_out')
    fieldsets = (
        (None, {'fields': ('email', 'home_address', 'size', 'consent', 'privacy', 'first_survey_done', 'password', 'authorized', 'device_sent', 'received_data',
        'filled_surveys', 'dropped_out')}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )
    readonly_fields = ['get_received_data']

    search_fields = ('email',)
    ordering = ('email',)
    actions = [admin_email]

    def get_received_data(self, obj):
        ids = get_ids_with_data()

        for response in Response.objects.all():
            if obj.user_id == response.user_id:
                obj.filled_surveys.add(response.survey)

        if obj.received_data:
            return True

        for id, date in ids:
            if int(obj.user_id) == id:
                obj.received_data = True
                obj.save()
                return True

        return False

    get_received_data.short_description = 'Received data'
    get_received_data.admin_order_field = 'received_data'
    get_received_data.boolean = True

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class SubscriberAdmin(ModelAdmin):
    model = Subscriber
    list_display = ('email', 'has_received_email')
    list_filter = ('email', 'has_received_email')
    actions = [admin_email]

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'has_received_email')}
         ),
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
