from django.contrib.admin import SimpleListFilter
from survey.models.survey import Survey


class SurveyNotDoneFilter(SimpleListFilter):
    title = "Survey Not Done"
    parameter_name = "Survey"

    def lookups(self, request, model_admin):
        return ((survey.pk, survey.name) for survey in Survey.objects.all())

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.exclude(filled_surveys__pk=self.value())
