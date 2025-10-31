from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import User, Event, SessionalMark, Notification
from .forms import (
    UserRegisterForm, EventForm, MarkEntryForm,
    NotificationForm, SearchForm
)

# -------------------------------
# HOME PAGE
# -------------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


# -------------------------------
# AUTHENTICATION
# -------------------------------
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome {user.username}')
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please check your details.')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# -------------------------------
# DASHBOARD
# -------------------------------
@login_required
def dashboard(request):
    user = request.user
    notifications = Notification.objects.filter(is_active=True)[:5]

    # ---------- STUDENT ----------
    if user.role == 'student':
        marks = SessionalMark.objects.filter(student=user).select_related('event')
        upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
        context = {
            'marks': marks,
            'upcoming_events': upcoming_events,
            'notifications': notifications,
            'total_events': marks.count(),
        }
        return render(request, 'student_dashboard.html', context)

    # ---------- FACULTY ----------
    elif user.role == 'faculty':
        # Get all events created by this faculty, including date and time
        events = Event.objects.filter(created_by=user).order_by('date', 'time')
        total_marks_entered = SessionalMark.objects.filter(entered_by=user).count()

        # Upcoming 5 events for convenience
        upcoming_events = events.filter(date__gte=timezone.now().date())[:5]

        context = {
            'events': events,
            'upcoming_events': upcoming_events,
            'total_events': events.count(),
            'total_marks_entered': total_marks_entered,
            'notifications': notifications,
        }
        return render(request, 'faculty_dashboard.html', context)

    # ---------- ADMIN ----------
    elif user.role == 'admin':
        users = User.objects.all()
        events = Event.objects.all()
        marks = SessionalMark.objects.all()
        context = {
            'users': users,
            'events': events,
            'total_users': users.count(),
            'total_students': users.filter(role='student').count(),
            'total_faculty': users.filter(role='faculty').count(),
            'total_events': events.count(),
            'total_marks': marks.count(),
            'notifications': notifications,
        }
        return render(request, 'admin_dashboard.html', context)

    else:
        messages.error(request, "Invalid role assigned. Contact admin.")
        return redirect('home')


# -------------------------------
# EVENT MANAGEMENT
# -------------------------------
@login_required
def event_list(request):
    events = Event.objects.all()
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        if query:
            events = events.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(venue__icontains=query)
            )
    return render(request, 'event_list.html', {'events': events, 'search_form': search_form})


@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    marks = SessionalMark.objects.filter(event=event).select_related('student')
    return render(request, 'event_detail.html', {'event': event, 'marks': marks})


@login_required
def event_create(request):
    if request.user.role not in ['faculty', 'admin']:
        messages.error(request, 'You do not have permission to create events.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
    else:
        form = EventForm()

    return render(request, 'event_form.html', {'form': form, 'title': 'Create Event'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.role != 'admin' and event.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)

    return render(request, 'event_form.html', {'form': form, 'title': 'Edit Event', 'event': event})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.role != 'admin' and event.created_by != request.user:
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('event_list')

    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('event_list')


# -------------------------------
# MARK ENTRY
# -------------------------------
@login_required
def mark_entry(request):
    if request.user.role not in ['faculty', 'admin']:
        messages.error(request, 'You do not have permission to enter marks.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = MarkEntryForm(request.POST)
        if form.is_valid():
            mark = form.save(commit=False)
            mark.entered_by = request.user
            mark.save()
            messages.success(request, 'Marks entered successfully!')
            return redirect('mark_entry')
    else:
        form = MarkEntryForm()

    recent_marks = SessionalMark.objects.filter(entered_by=request.user)[:10]
    return render(request, 'mark_entry.html', {'form': form, 'recent_marks': recent_marks})


# -------------------------------
# NOTIFICATIONS
# -------------------------------
@login_required
def notifications_view(request):
    all_notifications = Notification.objects.all()
    return render(request, 'notifications.html', {'notifications': all_notifications})


@login_required
def notification_create(request):
    if request.user.role not in ['admin', 'faculty']:
        messages.error(request, 'Only admins and faculty can create notifications.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.created_by = request.user

            # Restrict faculty to send only to students/all
            if request.user.role == 'faculty' and notification.target_role not in ['student', 'all']:
                messages.error(request, 'Faculty can only send notifications to students or all users.')
                return render(request, 'notification_form.html', {'form': form})

            notification.save()
            messages.success(request, 'Notification created successfully!')
            return redirect('notifications')
    else:
        form = NotificationForm()
        if request.user.role == 'faculty':
            form.fields['target_role'].choices = [
                ('all', 'All Users'),
                ('student', 'Students Only'),
            ]

    return render(request, 'notification_form.html', {'form': form})


# -------------------------------
# REVALUATION REQUEST (Student)
# -------------------------------
@login_required
def request_reval(request):
    if request.method == 'POST' and request.user.role == 'student':
        exam_title = request.POST.get('exam_title')
        req_type = request.POST.get('type')
        reason = request.POST.get('reason')
        messages.success(request, 'Your revaluation request has been submitted successfully.')
        return redirect('dashboard')
    messages.error(request, 'Invalid request.')
    return redirect('dashboard')


# -------------------------------
# ADMIN USER MANAGEMENT
# -------------------------------
@login_required
def edit_user(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.department = request.POST.get('department', '')
        user.phone = request.POST.get('phone', '')
        user.enrollment_no = request.POST.get('enrollment_no', '')
        user.save()
        messages.success(request, "User details updated successfully.")
        return redirect('dashboard')

    return render(request, 'edit_user.html', {'user': user})


@login_required
def delete_user(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Unauthorized access.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, 'User deleted successfully.')
    return redirect('dashboard')
