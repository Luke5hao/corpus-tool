from django.contrib import admin
from .models import TextEntry

@admin.register(TextEntry)
class TextEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'submission_date')
    search_fields = ('text', 'user__username')
    list_filter = ('user',)

    def submission_date(self, obj):
        return obj.id
    submission_date.admin_order_field = 'id'
    submission_date.short_description = 'Submission Date'