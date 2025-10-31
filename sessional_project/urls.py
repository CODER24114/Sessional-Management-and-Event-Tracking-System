from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Marks
    path('marks/entry/', views.mark_entry, name='mark_entry'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    
    # Student requests
    path('request_reval/', views.request_reval, name='request_reval'),
    
    # Admin user management
    path('edit_user/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:pk>/', views.delete_user, name='delete_user'),

    # 🔹 Password Reset URLs (Forgot Password)
    path(
        'password_reset/', 
        auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), 
        name='password_reset'
    ),
    path(
        'password_reset/done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
        name='password_reset_confirm'
    ),
    path(
        'reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_done.html'), 
        name='password_reset_complete'
    ),
]
