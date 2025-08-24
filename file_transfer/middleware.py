import time
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    会话超时中间件
    检测用户活动，如果5分钟内没有操作则自动登出
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # 获取当前时间戳
            current_time = time.time()
            
            # 获取最后活动时间
            last_activity = request.session.get('last_activity', 0)
            
            # 检查是否超时（5分钟 = 300秒）
            if current_time - last_activity > 300:
                # 超时，登出用户
                logout(request)
                messages.warning(request, '由于长时间无操作，您已被自动登出。请重新登录。')
                return redirect('login')
            
            # 更新最后活动时间
            request.session['last_activity'] = current_time
            
            # 延长会话时间
            request.session.set_expiry(300)  # 5分钟
        
        return None


class ActivityTrackingMiddleware(MiddlewareMixin):
    """
    活动跟踪中间件
    记录用户的页面访问和操作
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # 记录用户访问的页面
            current_path = request.path
            if current_path not in ['/login/', '/logout/', '/admin/login/']:
                request.session['last_page'] = current_path
                
                # 记录访问时间
                request.session['last_visit'] = time.time()
        
        return None


class SecurityMiddleware(MiddlewareMixin):
    """
    安全中间件
    添加额外的安全头和安全检查
    """
    
    def process_response(self, request, response):
        # 添加安全头
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # 如果用户已认证，添加活动检测的JavaScript
        if request.user.is_authenticated and hasattr(response, 'content'):
            # 这里可以添加JavaScript代码来检测用户活动
            pass
        
        return response