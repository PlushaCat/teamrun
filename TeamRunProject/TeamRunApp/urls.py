from django.urls import path

from . import views
from .views import TaskListCreateView, TaskCreateView, UpdateTaskOrderView, ProjectCreateView



urlpatterns = [
 path('index/', views.index, name='index'),
 path('register/', views.register_view, name='register'),
 path('', views.login_view, name='login'),
 path('menu/', views.menu, name='menu'),
 # страницы
 path('menu/create/', ProjectCreateView.as_view(), name='project_create'),
 path("menu/invites", views.InvitationsView.as_view(), name="invites"),
 path("menu/my-projects", views.MyProjectsView.as_view(), name="my-projects"),
 path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
 path('project/<int:project_id>/add-list/', TaskListCreateView.as_view(), name='add_task_list'),
 path('project/<int:project_id>/list/<int:list_id>/add-task/', TaskCreateView.as_view(), name='add_task'),
 path('project/<int:project_id>/update-task-order/', UpdateTaskOrderView.as_view(), name='update_task_order'),
 path('project/<int:project_id>/get-list-form/', views.get_list_form, name='get_list_form'),
# участники проекта
 path('project/<int:project_id>/team/', views.ProjectTeamView.as_view(), name='project_team'),
 path('project/<int:project_id>/team/<int:pk>/remove/', views.RemoveProjectMemberView.as_view(), name='remove_project_member'),
 path('project/<int:project_id>/invite/', views.InviteMemberView.as_view(), name='send_invitation'),
 path('menu/invites/', views.InvitationsListView.as_view(), name='invitations_list'),
 path('profile/', views.profile_view, name='profile'),
 # Назначение задач
 path('tasks/<int:pk>/assign/', views.TaskAssignmentView.as_view(), name='task_assign'),
 path('tasks/<int:pk>/assign/process/', views.ProcessAssignmentView.as_view(), name='process_assignment'),
]