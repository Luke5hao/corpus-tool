from django.contrib import admin
from .models import TextEntry

@admin.register(TextEntry)
class TextEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'truncated_worklog', 'user', 'submission_date')
    search_fields = ('text', 'user__username')
    list_filter = ('user',)

    def truncated_worklog(self, obj):
        return obj.worklog[:35] + '...' if len(obj.worklog) > 35 else obj.worklog
    truncated_worklog.short_description = 'Worklog Link'

    def submission_date(self, obj):
        return obj.created_at
    submission_date.admin_order_field = 'created_at'
    submission_date.short_description = 'Submission Date'
