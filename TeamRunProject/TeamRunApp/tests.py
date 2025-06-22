from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import CustomUser, Project, ProjectMembership, List, Task

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass123',
            role='developer'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.role, 'developer')
        self.assertEqual(str(self.user), 'testuser (developer)')

    def test_get_avatar_small(self):
        small_avatar = self.user.get_avatar_small()
        self.assertIn('h-6 w-6', small_avatar)  # Проверяем размер small аватара



class ProjectModelTest(TestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(username='owner', role='manager')
        self.member = CustomUser.objects.create_user(username='member', role='developer')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            owner=self.owner
        )

    def test_add_member(self):
        self.project.add_member(self.member)
        self.assertTrue(self.project.is_member(self.member))

    def test_remove_member(self):
        self.project.add_member(self.member)
        self.project.remove_member(self.member)
        self.assertFalse(self.project.is_member(self.member))

    def test_is_owner_or_manager(self):
        self.assertTrue(self.project.is_owner(self.owner))
        self.assertFalse(self.project.is_owner(self.member))

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='taskuser', role='developer')
        self.project = Project.objects.create(name='Task Project', owner=self.user)
        self.task_list = List.objects.create(name='To Do', project=self.project)
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            list=self.task_list
        )

    def test_task_creation(self):
        self.assertEqual(str(self.task), 'Test Task')

    def test_assign_users(self):
        self.task.assigned_to.add(self.user)
        self.assertIn(self.user, self.task.get_assigned_users())