from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
import json

class SessionTimeoutMiddleware:
    """会话超时中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 处理请求前
        if request.user.is_authenticated:
            # 检查会话是否超时
            last_activity = request.session.get('last_activity')
            if last_activity:
                try:
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                    time_diff = timezone.now() - last_activity
                    
                    # 如果超过5分钟，自动登出
                    if time_diff.total_seconds() > 300:
                        # 确保彻底登出并清理会话
                        request.session.flush()
                        logout(request)
                        # 对于AJAX请求，返回JSON响应
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            from django.http import JsonResponse
                            return JsonResponse({
                                'status': 'expired',
                                'message': 'Session expired due to inactivity',
                                'redirect_url': reverse('file_transfer:custom_login')
                            }, status=401)
                        # 对于普通请求，重定向到登录页
                        return redirect('file_transfer:custom_login')
                except (ValueError, TypeError):
                    # 如果时间格式错误，清除会话
                    request.session.flush()
                    logout(request)
                    return redirect('file_transfer:custom_login')
            
            # 更新最后活动时间
            request.session['last_activity'] = timezone.now().isoformat()
        
        response = self.get_response(request)
        return response

class ActivityTrackingMiddleware:
    """用户活动跟踪中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # 如果用户已认证，记录活动
        if request.user.is_authenticated and request.method in ['GET', 'POST', 'PUT', 'DELETE']:
            # 排除静态文件和媒体文件
            if not any(path in request.path for path in ['/static/', '/media/', '/admin/']):
                request.session['last_activity'] = timezone.now().isoformat()
        
        return response