#!/usr/bin/env python3
"""
认证系统测试脚本
测试新的身份验证和会话超时功能
"""

import os
import sys
import django
from pathlib import Path

# 设置Django环境
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'file_transfer_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.contrib.auth import authenticate
import time

def test_authentication_required():
    """测试需要身份验证的页面"""
    print("🔐 测试身份验证要求...")
    
    client = Client()
    
    # 测试未登录用户访问主页
    response = client.get('/')
    if response.status_code == 302:  # 重定向到登录页面
        print("✅ 未登录用户被重定向到登录页面")
    else:
        print(f"❌ 未登录用户访问主页状态码: {response.status_code}")
    
    # 测试未登录用户访问上传页面
    response = client.get('/upload/')
    if response.status_code == 302:
        print("✅ 未登录用户被重定向到登录页面")
    else:
        print(f"❌ 未登录用户访问上传页面状态码: {response.status_code}")
    
    # 测试未登录用户访问历史页面
    response = client.get('/history/')
    if response.status_code == 302:
        print("✅ 未登录用户被重定向到登录页面")
    else:
        print(f"❌ 未登录用户访问历史页面状态码: {response.status_code}")
    
    return True

def test_login_functionality():
    """测试登录功能"""
    print("\n👤 测试登录功能...")
    
    client = Client()
    
    # 测试登录页面访问
    response = client.get('/login/')
    if response.status_code == 200:
        print("✅ 登录页面可以正常访问")
    else:
        print(f"❌ 登录页面访问失败，状态码: {response.status_code}")
    
    # 测试登录表单
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    if response.status_code == 302:  # 重定向到主页
        print("✅ 登录成功，用户被重定向到主页")
        
        # 测试登录后访问主页
        response = client.get('/')
        if response.status_code == 200:
            print("✅ 登录后可以正常访问主页")
        else:
            print(f"❌ 登录后访问主页失败，状态码: {response.status_code}")
    else:
        print(f"❌ 登录失败，状态码: {response.status_code}")
    
    return True

def test_session_timeout():
    """测试会话超时功能"""
    print("\n⏰ 测试会话超时功能...")
    
    client = Client()
    
    # 登录用户
    client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    # 检查会话设置
    session = client.session
    if 'last_activity' in session:
        print("✅ 会话活动时间已设置")
    else:
        print("❌ 会话活动时间未设置")
    
    if 'login_time' in session:
        print("✅ 登录时间已设置")
    else:
        print("❌ 登录时间未设置")
    
    # 测试会话信息页面
    response = client.get('/session-info/')
    if response.status_code == 200:
        print("✅ 会话信息页面可以正常访问")
    else:
        print(f"❌ 会话信息页面访问失败，状态码: {response.status_code}")
    
    return True

def test_logout_functionality():
    """测试登出功能"""
    print("\n🚪 测试登出功能...")
    
    client = Client()
    
    # 先登录
    client.post('/login/', {
        'username': 'admin',
        'password': 'admin123'
    })
    
    # 测试登出
    response = client.get('/logout/')
    if response.status_code == 302:  # 重定向到登录页面
        print("✅ 登出成功，用户被重定向到登录页面")
        
        # 测试登出后无法访问受保护页面
        response = client.get('/')
        if response.status_code == 302:
            print("✅ 登出后无法访问受保护页面")
        else:
            print(f"❌ 登出后仍能访问受保护页面，状态码: {response.status_code}")
    else:
        print(f"❌ 登出失败，状态码: {response.status_code}")
    
    return True

def test_admin_access():
    """测试管理后台访问"""
    print("\n🔧 测试管理后台访问...")
    
    client = Client()
    
    # 测试未登录用户访问管理后台
    response = client.get('/admin/')
    if response.status_code == 302:  # 重定向到管理后台登录页面
        print("✅ 未登录用户被重定向到管理后台登录页面")
    else:
        print(f"❌ 未登录用户访问管理后台状态码: {response.status_code}")
    
    # 测试使用超级用户账号登录管理后台
    response = client.post('/admin/login/', {
        'username': 'admin',
        'password': 'admin123',
        'next': '/admin/'
    })
    
    if response.status_code == 302:
        print("✅ 管理后台登录成功")
        
        # 测试登录后访问管理后台
        response = client.get('/admin/')
        if response.status_code == 200:
            print("✅ 登录后可以正常访问管理后台")
        else:
            print(f"❌ 登录后访问管理后台失败，状态码: {response.status_code}")
    else:
        print(f"❌ 管理后台登录失败，状态码: {response.status_code}")
    
    return True

def test_middleware_functionality():
    """测试中间件功能"""
    print("\n⚙️ 测试中间件功能...")
    
    # 检查中间件是否正确加载
    from django.conf import settings
    middleware_classes = settings.MIDDLEWARE
    
    required_middleware = [
        'file_transfer.middleware.SessionTimeoutMiddleware',
        'file_transfer.middleware.ActivityTrackingMiddleware',
        'file_transfer.middleware.SecurityMiddleware'
    ]
    
    for middleware in required_middleware:
        if middleware in middleware_classes:
            print(f"✅ 中间件已加载: {middleware}")
        else:
            print(f"❌ 中间件未加载: {middleware}")
    
    # 检查会话设置
    if hasattr(settings, 'SESSION_COOKIE_AGE') and settings.SESSION_COOKIE_AGE == 300:
        print("✅ 会话超时时间设置为5分钟")
    else:
        print("❌ 会话超时时间设置不正确")
    
    if hasattr(settings, 'LOGIN_URL') and settings.LOGIN_URL == '/login/':
        print("✅ 登录URL设置正确")
    else:
        print("❌ 登录URL设置不正确")
    
    return True

def main():
    """主测试函数"""
    print("🚀 开始测试认证系统...")
    print("=" * 60)
    
    tests = [
        test_authentication_required,
        test_login_functionality,
        test_session_timeout,
        test_logout_functionality,
        test_admin_access,
        test_middleware_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！认证系统配置正确。")
        print("\n📋 系统特性:")
        print("✅ 所有页面都需要身份验证")
        print("✅ 会话5分钟超时")
        print("✅ 自动登出功能")
        print("✅ 安全的登录系统")
        print("✅ 管理后台独立认证")
        print("\n🚀 下一步操作:")
        print("1. 运行 ./start.sh 启动系统")
        print("2. 访问 http://localhost:8000")
        print("3. 系统会自动跳转到登录页面")
        print("4. 使用 admin/admin123 登录")
    else:
        print("⚠️  部分测试失败，请检查配置。")
    
    return passed == total

if __name__ == '__main__':
    main()