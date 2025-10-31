# core/admin.py - Make sure it looks like this
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Event, SessionalMark, Notification  # No Department!

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_staff')
    list_filter = ('role', 'department', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'enrollment_no', 'department')}),
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'date', 'created_by', 'max_marks')
    list_filter = ('event_type', 'date', 'created_by')
    search_fields = ('title', 'description', 'venue')
    date_hierarchy = 'date'

@admin.register(SessionalMark)
class SessionalMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'event', 'marks_obtained', 'percentage', 'entered_by', 'entered_at')
    list_filter = ('event', 'entered_by', 'entered_at')
    search_fields = ('student__username', 'event__title')
    
    def percentage(self, obj):
        return f"{obj.percentage():.2f}%"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'message')
