from django.urls import path
from . import views
from . import auth_views

app_name = 'file_transfer'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.file_upload, name='file_upload'),
    path('history/', views.file_history, name='file_history'),
    path('detail/<int:file_id>/', views.file_detail, name='file_detail'),
    path('download/<int:file_id>/', views.file_download, name='file_download'),
    path('delete/<int:file_id>/', views.file_delete, name='file_delete'),
    
    # 认证相关路由
    path('session-info/', auth_views.session_info, name='session_info'),
    path('extend-session/', auth_views.extend_session, name='extend_session'),
]