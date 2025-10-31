# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Event, SessionalMark, Notification


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    enrollment_no = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role', 'phone', 'enrollment_no', 'department']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'date', 'time', 'venue', 'description', 'max_marks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class MarkEntryForm(forms.ModelForm):
    class Meta:
        model = SessionalMark
        fields = ['student', 'event', 'marks_obtained', 'remarks']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role='student')
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean_marks_obtained(self):
        marks = self.cleaned_data.get('marks_obtained')
        event = self.cleaned_data.get('event')
        if event and marks > event.max_marks:
            raise forms.ValidationError(f'Marks cannot exceed {event.max_marks}')
        return marks

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'target_role', 'is_active']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass user from view
        super().__init__(*args, **kwargs)
        
        # If faculty, limit choices
        if user and user.role == 'faculty':
            self.fields['target_role'].choices = [
                ('all', 'All Users'),
                ('student', 'Students Only'),
            ]
        
        for field in self.fields:
            if field != 'is_active':
                self.fields[field].widget.attrs.update({'class': 'form-control'})


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}))


# core/forms.py - Update NotificationForm

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['title', 'message', 'target_role', 'is_active']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'is_active':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
