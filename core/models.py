# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    enrollment_no = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"


class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('sessional', 'Sessional Exam'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('quiz', 'Quiz'),
        ('workshop', 'Workshop'),
    )
    
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=200, choices=EVENT_TYPE_CHOICES, default='sessional')
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    venue = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    max_marks = models.IntegerField(default=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    
    # NEW: Assign events to specific students (if blank, visible to all students)
    assigned_students = models.ManyToManyField(
        User, 
        related_name='assigned_events', 
        blank=True, 
        limit_choices_to={'role': 'student'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.title} - {self.date}"


class SessionalMark(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="marks")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.IntegerField()
    remarks = models.TextField(blank=True)
    entered_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entered_marks')
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'event')
        ordering = ['-entered_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.event.title} - {self.marks_obtained}/{self.event.max_marks}"
    
    def percentage(self):
        return (self.marks_obtained / self.event.max_marks) * 100


class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


# core/models.py - Update Notification model

class Notification(models.Model):
    RECIPIENT_CHOICES = (
        ('all', 'All Users'),
        ('student', 'Students Only'),
        ('faculty', 'Faculty Only'),
        ('admin', 'Admins Only'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_created')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # NEW: Target specific user roles
    target_role = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
