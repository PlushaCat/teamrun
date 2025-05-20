
import TeamRunApp.models
import django.db
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .forms import *
from django.views.generic import TemplateView, DetailView, CreateView, ListView, DeleteView, UpdateView
from .models import *



def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('menu')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('menu')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def get_list_form(request, project_id):
    """Возвращает форму для создания списка"""
    return render(request, 'list_form.html')

def menu(request):
    return render(request, 'menu.html')

class CreateProjectView(TemplateView):
    template_name = "create_project.html"

class InvitationsView(TemplateView):
    template_name = "invite_to_project.html"

class MyProjectsView(ListView, LoginRequiredMixin):
    model = Project
    template_name = 'my_projects.html'
    context_object_name = 'project'

    def get_queryset(self):
        # Получаем ID проектов, где пользователь является участником
        user_memberships = ProjectMembership.objects.filter(user=self.request.user)
        project_ids = user_memberships.values_list('project_id', flat=True)
        
        # Возвращаем только проекты, в которых пользователь состоит
        return Project.objects.filter(id__in=project_ids)

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'index.html'
    context_object_name = 'project'






class TaskListCreateView(CreateView):
    model = List
    form_class = TaskListForm
    template_name = 'add_task_list.html'

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['project_id']
        return super().form_valid(form)

    
    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['project_id']})

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'add_task.html'

    def form_valid(self, form):
        form.instance.list_id = self.kwargs['list_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['project_id']})
    

class UpdateTaskOrderView(View):
    def post(self, request, project_id):
        task_id = request.POST.get('task_id')
        new_list_id = request.POST.get('list_id')
        old_list_id = request.POST.get('old_list_id')

        task = Task.objects.get(id=task_id)
        new_list = List.objects.get(id=new_list_id)
        old_list = List.objects.get(id=old_list_id)

        # Удалить таску из старого списка
        old_list.tasks.remove(task)

        # Добавить таску в новый список
        new_list.tasks.add(task)

        return HttpResponse('OK')

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.kwargs['project_id']})
    

class ProjectTeamView(LoginRequiredMixin, ListView):
    model = ProjectMembership
    template_name = 'project_team.html'
    context_object_name = 'memberships'

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        self.project = get_object_or_404(Project, id=project_id)
        
        if not self.project.is_member(self.request.user):
            raise PermissionDenied("У вас нет доступа к этому проекту")
        
        return ProjectMembership.objects.filter(project=self.project).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['project'] = self.project
        context['is_owner_or_manager'] = self.project.is_owner_or_manager(self.request.user)
        context['available_users'] = CustomUser.objects.exclude(
            project_memberships__project=self.project
        ).exclude(id=self.project.owner.id)
        return context
    
    
class RemoveProjectMemberView(LoginRequiredMixin, DeleteView):
    model = ProjectMembership
    template_name = 'project_team.html'

    def dispatch(self, request, *args, **kwargs):
        self.membership = self.get_object()
        self.project = self.membership.project
        
        if not self.project.is_owner_or_manager(request.user):
            raise PermissionDenied("Недостаточно прав для удаления участников")
        
        if self.membership.user == self.project.owner or self.membership.role == 'manager':
            raise PermissionDenied("Нельзя удалить владельца или менеджера проекта")
        
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('project_team', kwargs={'project_id': self.project.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context

class TaskAssignmentView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'assign_task.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object
        context['project'] = task.list.project
        context['users_assigned'] = task.assigned_to.all()
        context['members'] = task.list.project.get_members()
        return context
    
class ProcessAssignmentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        task_id = kwargs.get('pk')
        task = get_object_or_404(Task, pk=task_id)
        project = task.list.project
        
        if not project.is_member(request.user):
            messages.error(request, "Нет прав для назначения задач")
            return redirect('project_detail', pk=project.id)
        
        user_id = request.POST.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
            if project.is_member(user):
                task.assigned_to.add(user)
                messages.success(request, f"Задача назначена на {user.username}")
            else:
                messages.error(request, "Пользователь не в проекте")
        else:
            task.assigned_to = None
            messages.success(request, "Назначение снято")
        
        return redirect('project_detail', project.id)
    

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = CreateProjectForm
    template_name = 'create_project.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        
        ProjectMembership.objects.create(
            project=self.object,
            user=self.request.user,
            role='manager'
        )
        
        return response
    

class InviteMemberView(LoginRequiredMixin, TemplateView):
    template_name = 'add_member.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, id=kwargs['project_id'])
        if not self.has_permission():
            messages.error(request, "Недостаточно прав для приглашения")
            return redirect('project_detail', pk=self.project.id)
        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        # Проверяем, является ли пользователь владельцем или менеджером проекта
        return (
            self.project.owner == self.request.user or
            self.project.memberships.filter(
                user=self.request.user, 
                role='manager'
            ).exists()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        search_query = self.request.GET.get('username')
        
        if search_query:
            User = get_user_model()
            context['users'] = User.objects.filter(
                username__icontains=search_query
            ).exclude(
                id__in=self.project.memberships.values_list('user_id', flat=True)
            ).exclude(
                id__in=self.project.invitations.filter(status='pending').values_list('user_id', flat=True)
            )
            context['search_query'] = search_query
            
        return context

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        role = request.POST.get('role', 'member')
        
        if user_id:
            try:
                user = get_user_model().objects.get(id=user_id)
                ProjectInvitation.objects.create(
                    project=self.project,
                    user=user,
                    inviter=request.user,
                    role=role
                )
                messages.success(request, f"Приглашение отправлено {user.username}")
            except Exception as e:
                messages.error(request, f"Ошибка: {str(e)}")
        
        return redirect('send_invitation', project_id=self.project.id)
    
class InvitationsListView(LoginRequiredMixin, ListView):
    template_name = 'invite_to_project.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        # Получаем только pending-приглашения текущего пользователя
        return self.request.user.project_invitations.filter(status='pending').select_related('project', 'inviter')

    def post(self, request, *args, **kwargs):
        invitation_id = request.POST.get('invitation_id')
        action = request.POST.get('action')
        
        try:
            invitation = request.user.project_invitations.get(
                id=invitation_id,
                status='pending'  # Защита от повторной обработки
            )
            
            if action == 'accept':
                # Создаем членство в проекте
                ProjectMembership.objects.create(
                    project=invitation.project,
                    user=request.user,
                    role=invitation.role
                )
                invitation.status = 'accepted'
                invitation.save()
                messages.success(request, f'Вы присоединились к проекту "{invitation.project.name}"')
                
            elif action == 'reject':
                invitation.status = 'rejected'
                invitation.save()
                messages.info(request, f'Вы отклонили приглашение в проект "{invitation.project.name}"')
                
        except ProjectInvitation.DoesNotExist:
            messages.error(request, 'Приглашение не найдено или уже обработано')
        
        return redirect('invitations_list')

    


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)
    
    return render(request, 'profile.html', {
        'user': user,
        'form': form,
        'is_editing': 'edit' in request.GET
    })