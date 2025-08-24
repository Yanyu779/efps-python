from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
import time


def login_view(request):
    """用户登录视图"""
    if request.user.is_authenticated:
        return redirect('file_transfer:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # 设置会话信息
                request.session['last_activity'] = time.time()
                request.session['login_time'] = time.time()
                request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
                
                # 记录登录日志
                print(f"用户 {username} 登录成功 - {timezone.now()}")
                
                messages.success(request, f'欢迎回来，{username}！')
                return redirect('file_transfer:dashboard')
            else:
                messages.error(request, '用户名或密码错误。')
        else:
            messages.error(request, '请检查输入信息。')
    else:
        form = AuthenticationForm()
    
    return render(request, 'file_transfer/login.html', {
        'form': form,
        'title': '用户登录'
    })


@login_required
def logout_view(request):
    """用户登出视图"""
    username = request.user.username
    
    # 记录登出日志
    print(f"用户 {username} 登出 - {timezone.now()}")
    
    logout(request)
    messages.success(request, '您已成功登出。')
    return redirect('login')


@login_required
def session_info(request):
    """会话信息视图"""
    current_time = time.time()
    login_time = request.session.get('login_time', 0)
    last_activity = request.session.get('last_activity', 0)
    
    session_data = {
        'username': request.user.username,
        'login_time': timezone.datetime.fromtimestamp(login_time) if login_time else None,
        'last_activity': timezone.datetime.fromtimestamp(last_activity) if last_activity else None,
        'session_age': current_time - login_time if login_time else 0,
        'idle_time': current_time - last_activity if last_activity else 0,
        'session_expires_in': 300 - (current_time - last_activity) if last_activity else 300,
    }
    
    return render(request, 'file_transfer/session_info.html', {
        'session_data': session_data,
        'title': '会话信息'
    })


@login_required
def extend_session(request):
    """延长会话时间"""
    if request.method == 'POST':
        # 更新最后活动时间
        request.session['last_activity'] = time.time()
        request.session.set_expiry(300)  # 5分钟
        
        messages.success(request, '会话已延长。')
        return redirect('file_transfer:dashboard')
    
    return redirect('file_transfer:dashboard')