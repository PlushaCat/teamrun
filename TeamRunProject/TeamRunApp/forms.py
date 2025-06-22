from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from TeamRunApp.models import CustomUser, Task, List, Project


class BaseForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 mt-2 text-gray-700 bg-white border rounded-lg focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-300 transition-colors duration-200'
            })
            if isinstance(field.widget, forms.PasswordInput):
                field.widget.attrs['placeholder'] = '••••••••'

class LoginForm(BaseForm, AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваш логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class RegisterForm(BaseForm, UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'email')

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Придумайте логин'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Создайте пароль'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите пароль'
        })
    )




class TaskListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Название списка'
            })
        }
        labels = {
            'name': 'Название списка',
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Название задачи'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Описание задачи',
                'rows': 3
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border rounded-lg'
            })
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Описание задачи',
            'due_date': 'Срок выполнения',
        }

class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Название проекта'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg',
                'placeholder': 'Описание проекта'
            })
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'avatar']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'avatar': 'Аватарка',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500'
        })
        self.fields['avatar'].widget.attrs.update({
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
        })


        