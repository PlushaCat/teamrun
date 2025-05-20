
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils.html import format_html

def user_avatar_path(instance, filename):
    # Файл будет загружен в MEDIA_ROOT/user_<id>/avatar/<filename>
    return f'user_{instance.id}/avatar/{filename}'

class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=[('manager', 'Manager'), ('developer', 'Developer')])
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    def get_avatar(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return format_html('<img src="{}" alt="User avatar" class="h-32 w-32 rounded-full object-cover border-4 border-blue-100">', self.avatar.url)
        else:
            # Возвращаем букву никнейма в виде HTML
            first_letter = self.username[0].upper()  # Получаем первую букву никнейма
            return format_html('<div class="h-32 w-32 rounded-full flex items-center justify-center border-4 border-blue-100 text-2xl">{}</div>', first_letter)
    
    def get_avatar_small(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return format_html('<img src="{}" alt="User avatar" class="h-12 w-12 rounded-full object-cover border-4 border-blue-100">', self.avatar.url)
        else:
            # Возвращаем букву никнейма в виде HTML
            first_letter = self.username[0].upper()  # Получаем первую букву никнейма
            return format_html('<div class="h-6 w-6 rounded-full flex items-center justify-center border-4 border-blue-100 text-2xl">{}</div>', first_letter)

    def __str__(self):
        return f"{self.username} ({self.role})"

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})
    

    def add_member(self, user):
        """Добавить пользователя в проект"""
        ProjectMembership.objects.get_or_create(project=self, user=user)
    
    def remove_member(self, user):
        """Удалить пользователя из проекта"""
        self.memberships.filter(user=user).delete()
    
    def get_members(self):
        """Получить всех участников проекта"""
        return CustomUser.objects.filter(project_memberships__project=self)
    
    def is_member(self, user):
        """Проверить, является ли пользователь участником проекта"""
        return self.memberships.filter(user=user).exists()
    

    def is_owner(self, user):
        """Проверяет, является ли пользователь владельцем проекта."""
        return self.owner == user

    def is_manager(self, user):
        """Проверяет, является ли пользователь менеджером проекта."""
        return self.memberships.filter(user=user, role='manager').exists()

    def is_owner_or_manager(self, user):
        """Проверяет, является ли пользователь владельцем или менеджером."""
        return self.is_owner(user) or self.is_manager(user)
    
class List(models.Model):
    name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lists')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    list = models.ForeignKey(List, related_name='tasks', on_delete=models.CASCADE, null=True)
    assigned_to = models.ManyToManyField(CustomUser, related_name='tasks')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def get_assigned_users(self):
        return self.assigned_to.all()
    


class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('member', 'Member'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f"{self.user.username} ({self.role}) in {self.project.name}"
    

class ProjectInvitation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invitations')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_invitations')
    inviter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_invitations')
    role = models.CharField(max_length=20, choices=ProjectMembership.ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'user', 'status')

    def __str__(self):
        return f"{self.user.username} -> {self.project.name} ({self.status})"    
    

