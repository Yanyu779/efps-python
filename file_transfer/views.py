from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import os
from .models import FileTransfer
from .forms import FileUploadForm
from django.db import models

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
    
    try:
        # 使用安全的下载方法
        file_path = file_transfer.safe_download(request.user)
        
        # 打开文件并返回响应
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=file_transfer.file_type)
            response['Content-Disposition'] = f'attachment; filename="{file_transfer.original_name}"'
            return response
    except PermissionDenied:
        messages.error(request, '您没有权限下载此文件。')
        return redirect('file_transfer:file_history')
    except FileNotFoundError:
        messages.error(request, '文件不存在。')
        return redirect('file_transfer:file_history')
    except Exception as e:
        messages.error(request, f'下载失败：{str(e)}')
        return redirect('file_transfer:file_history')

@login_required
def file_history(request):
    """文件传输历史视图"""
    # 获取查询参数
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    file_type_filter = request.GET.get('file_type', '')
    
    # 构建查询 - 只显示用户有权限访问的文件
    if request.user.is_superuser:
        # 超级用户可以查看所有文件
        files = FileTransfer.objects.all()
    else:
        # 普通用户只能查看自己的文件
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
    file_transfer = get_object_or_404(FileTransfer, id=file_id)
    
    # 检查用户权限
    if not file_transfer.can_access(request.user):
        messages.error(request, '您没有权限查看此文件。')
        return redirect('file_transfer:file_history')
    
    return render(request, 'file_transfer/detail.html', {
        'file_transfer': file_transfer,
        'title': '文件详情'
    })

@login_required
def file_delete(request, file_id):
    """文件删除视图"""
    file_transfer = get_object_or_404(FileTransfer, id=file_id)
    
    # 检查用户权限
    if not file_transfer.can_delete(request.user):
        messages.error(request, '您没有权限删除此文件。')
        return redirect('file_transfer:file_history')
    
    if request.method == 'POST':
        try:
            # 使用安全的删除方法
            file_transfer.safe_delete(request.user)
            messages.success(request, f'文件 "{file_transfer.original_name}" 已删除')
            return redirect('file_transfer:file_history')
        except PermissionDenied:
            messages.error(request, '您没有权限删除此文件。')
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
    # 获取统计数据 - 只统计用户有权限访问的文件
    if request.user.is_superuser:
        # 超级用户可以查看所有文件的统计
        total_files = FileTransfer.objects.count()
        total_size = FileTransfer.objects.aggregate(
            total_size=models.Sum('file_size')
        )['total_size'] or 0
        
        # 按状态统计
        status_stats = {}
        for status_code, status_name in FileTransfer.STATUS_CHOICES:
            count = FileTransfer.objects.filter(status=status_code).count()
            status_stats[status_name] = count
        
        # 最近上传的文件
        recent_files = FileTransfer.objects.all().order_by('-uploaded_at')[:5]
        
        # 按文件类型统计
        file_type_stats = FileTransfer.objects.values('file_type').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10]
    else:
        # 普通用户只能查看自己的文件统计
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
