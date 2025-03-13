from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import TextEntry, UserProfile

@admin.register(TextEntry)
class TextEntryAdmin(admin.ModelAdmin):
    list_display = ('text', 'truncated_worklog', 'user', 'get_class_id', 'submission_date')
    search_fields = ('text', 'user__username', 'user__userprofile__class_id')
    list_filter = ('user', 'user__userprofile__class_id')

    def get_class_id(self, obj):
        return obj.user.userprofile.class_id
    get_class_id.short_description = 'Class ID'
    get_class_id.admin_order_field = 'user__userprofile__class_id'

    def truncated_worklog(self, obj):
        return obj.worklog[:35] + '...' if len(obj.worklog) > 35 else obj.worklog
    truncated_worklog.short_description = 'Worklog Link'

    def submission_date(self, obj):
        return obj.created_at
    submission_date.admin_order_field = 'created_at'
    submission_date.short_description = 'Submission Date'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_class_id', 'is_staff')
    
    def get_class_id(self, obj):
        try:
            return obj.userprofile.class_id
        except UserProfile.DoesNotExist:
            return '-'
    get_class_id.short_description = 'Class ID'
    get_class_id.admin_order_field = 'userprofile__class_id'

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)