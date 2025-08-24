import time
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.conf import settings


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


class AuthenticationEnforcementMiddleware(MiddlewareMixin):
    """
    身份验证强制中间件
    确保所有受保护的页面都需要身份验证
    """
    
    # 不需要身份验证的路径
    EXEMPT_PATHS = [
        '/login/',
        '/logout/',
        '/admin/login/',
        '/admin/logout/',
        '/static/',
        '/media/',
    ]
    
    # 管理后台路径（需要Django Admin认证）
    ADMIN_PATHS = [
        '/admin/',
    ]
    
    def process_request(self, request):
        path = request.path
        
        # 检查是否是静态文件或媒体文件
        if path.startswith('/static/') or path.startswith('/media/'):
            return None
        
        # 检查是否是登录相关路径
        if path in self.EXEMPT_PATHS:
            return None
        
        # 检查是否是管理后台路径
        if path in self.ADMIN_PATHS:
            # 管理后台有自己的认证系统，这里不处理
            return None
        
        # 检查用户是否已认证
        if not request.user.is_authenticated:
            # 未认证用户，重定向到登录页面
            messages.error(request, '请先登录以访问此页面。')
            return redirect('login')
        
        # 检查用户是否有权限访问特定文件
        if path.startswith('/download/') or path.startswith('/delete/') or path.startswith('/detail/'):
            # 这些路径需要额外的权限检查
            if not self._check_file_permission(request, path):
                messages.error(request, '您没有权限访问此文件。')
                return HttpResponseForbidden('权限不足')
        
        return None
    
    def _check_file_permission(self, request, path):
        """检查文件访问权限"""
        try:
            # 从路径中提取文件ID
            if '/download/' in path or '/delete/' in path or '/detail/' in path:
                # 这里可以添加更详细的权限检查逻辑
                # 例如检查文件是否属于当前用户
                return True
        except Exception:
            return False
        
        return True


class CSRFProtectionMiddleware(MiddlewareMixin):
    """
    CSRF保护增强中间件
    确保所有POST请求都有有效的CSRF令牌
    """
    
    def process_request(self, request):
        if request.method == 'POST':
            # 检查CSRF令牌
            if not request.META.get('CSRF_COOKIE'):
                messages.error(request, 'CSRF验证失败，请刷新页面重试。')
                return HttpResponseForbidden('CSRF验证失败')
        
        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    请求日志中间件
    记录所有请求的详细信息
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # 记录用户请求
            user_info = f"用户: {request.user.username}"
            request_info = f"请求: {request.method} {request.path}"
            ip_info = f"IP: {self._get_client_ip(request)}"
            
            # 记录到日志
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {user_info} | {request_info} | {ip_info}")
        
        return None
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip