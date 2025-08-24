from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import json
from .models import FileTransfer
from .forms import FileUploadForm, UserRegistrationForm
from django.db import models

def custom_login(request):
    """自定义登录视图"""
    if request.user.is_authenticated:
        return redirect('file_transfer:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # 设置会话最后活动时间
            request.session['last_activity'] = timezone.now().isoformat()
            messages.success(request, f'欢迎回来，{user.username}！')
            return redirect('file_transfer:dashboard')
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'file_transfer/login.html', {
        'title': '用户登录'
    })

def custom_logout(request):
    """自定义登出视图"""
    logout(request)
    messages.success(request, '您已成功退出登录')
    return redirect('file_transfer:custom_login')

@csrf_exempt
def check_session(request):
    """检查会话状态的API端点"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'heartbeat':
                # 更新最后活动时间
                request.session['last_activity'] = timezone.now().isoformat()
                return JsonResponse({'status': 'ok', 'message': 'Session updated'})
            
            elif action == 'check':
                # 检查会话是否有效
                if request.user.is_authenticated:
                    last_activity = request.session.get('last_activity')
                    if last_activity:
                        last_activity = timezone.datetime.fromisoformat(last_activity)
                        time_diff = timezone.now() - last_activity
                        
                        if time_diff.total_seconds() > 300:  # 5分钟
                            logout(request)
                            return JsonResponse({
                                'status': 'expired', 
                                'message': 'Session expired due to inactivity'
                            })
                    
                    return JsonResponse({'status': 'valid', 'message': 'Session is valid'})
                else:
                    return JsonResponse({'status': 'invalid', 'message': 'User not authenticated'})
                    
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def file_upload(request):
    """文件上传视图"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file_transfer = form.save(user=request.user)
                messages.success(request, f'文件 "{file_transfer.original_name}" 上传成功！')
                return redirect('file_transfer:file_history')
            except Exception as e:
                messages.error(request, f'文件上传失败：{str(e)}')
    else:
        form = FileUploadForm()
    
    return render(request, 'file_transfer/upload.html', {
        'form': form,
        'title': '文件上传'
    })

@login_required
def file_download(request, file_id):
    """文件下载视图"""
    file_transfer = get_object_or_404(FileTransfer, id=file_id)
    
    # 检查文件是否存在
    if not os.path.exists(file_transfer.file_path.path):
        raise Http404("文件不存在")
    
    # 打开文件并返回响应
    with open(file_transfer.file_path.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type=file_transfer.file_type)
        response['Content-Disposition'] = f'attachment; filename="{file_transfer.original_name}"'
        return response

@login_required
def file_history(request):
    """文件传输历史视图"""
    # 获取查询参数
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    file_type_filter = request.GET.get('file_type', '')
    
    # 构建查询
    files = FileTransfer.objects.filter(uploaded_by=request.user)
    
    if search_query:
        files = files.filter(
            Q(original_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if status_filter:
        files = files.filter(status=status_filter)
    
    if file_type_filter:
        files = files.filter(file_type__icontains=file_type_filter)
    
    # 分页
    paginator = Paginator(files, 20)  # 每页显示20个文件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取状态选项用于筛选
    status_choices = FileTransfer.STATUS_CHOICES
    
    return render(request, 'file_transfer/history.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'file_type_filter': file_type_filter,
        'status_choices': status_choices,
        'title': '传输历史'
    })

@login_required
def file_detail(request, file_id):
    """文件详情视图"""
    file_transfer = get_object_or_404(FileTransfer, id=file_id, uploaded_by=request.user)
    
    return render(request, 'file_transfer/detail.html', {
        'file_transfer': file_transfer,
        'title': '文件详情'
    })

@login_required
def file_delete(request, file_id):
    """文件删除视图"""
    file_transfer = get_object_or_404(FileTransfer, id=file_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        try:
            # 删除物理文件
            if os.path.exists(file_transfer.file_path.path):
                os.remove(file_transfer.file_path.path)
            
            # 删除数据库记录
            file_transfer.delete()
            messages.success(request, f'文件 "{file_transfer.original_name}" 已删除')
            return redirect('file_transfer:file_history')
        except Exception as e:
            messages.error(request, f'删除失败：{str(e)}')
    
    return render(request, 'file_transfer/delete_confirm.html', {
        'file_transfer': file_transfer,
        'title': '确认删除'
    })

@login_required
def dashboard(request):
    """仪表板视图"""
    # 获取统计数据
    total_files = FileTransfer.objects.filter(uploaded_by=request.user).count()
    total_size = FileTransfer.objects.filter(uploaded_by=request.user).aggregate(
        total_size=models.Sum('file_size')
    )['total_size'] or 0
    
    # 按状态统计
    status_stats = {}
    for status_code, status_name in FileTransfer.STATUS_CHOICES:
        count = FileTransfer.objects.filter(
            uploaded_by=request.user, 
            status=status_code
        ).count()
        status_stats[status_name] = count
    
    # 最近上传的文件
    recent_files = FileTransfer.objects.filter(
        uploaded_by=request.user
    ).order_by('-uploaded_at')[:5]
    
    # 按文件类型统计
    file_type_stats = FileTransfer.objects.filter(
        uploaded_by=request.user
    ).values('file_type').annotate(
        count=models.Count('id')
    ).order_by('-count')[:10]
    
    return render(request, 'file_transfer/dashboard.html', {
        'total_files': total_files,
        'total_size': total_size,
        'status_stats': status_stats,
        'recent_files': recent_files,
        'file_type_stats': file_type_stats,
        'title': '仪表板'
    })

def user_register(request):
    """用户注册视图"""
    if request.user.is_authenticated:
        return redirect('file_transfer:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'账户 {user.username} 创建成功！请登录。')
            return redirect('file_transfer:custom_login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'file_transfer/register.html', {
        'form': form,
        'title': '用户注册'
    })
