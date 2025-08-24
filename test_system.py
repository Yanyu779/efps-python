#!/usr/bin/env python3
"""
文件传输系统测试脚本
用于测试系统的基本功能
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
from file_transfer.models import FileTransfer
from django.test import Client
from django.urls import reverse

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        user_count = User.objects.count()
        file_count = FileTransfer.objects.count()
        print(f"✅ 数据库连接成功")
        print(f"   用户数量: {user_count}")
        print(f"   文件记录: {file_count}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_user_creation():
    """测试用户创建"""
    print("\n👤 测试用户创建...")
    try:
        # 检查是否已有测试用户
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print(f"✅ 测试用户创建成功: {test_user.username}")
        else:
            print(f"✅ 测试用户已存在: {test_user.username}")
        return True
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")
        return False

def test_urls():
    """测试URL配置"""
    print("\n🌐 测试URL配置...")
    try:
        client = Client()
        
        # 测试主页
        response = client.get('/')
        if response.status_code == 302:  # 重定向到登录页面
            print("✅ 主页URL正常 (需要登录)")
        else:
            print(f"⚠️  主页状态码: {response.status_code}")
        
        # 测试上传页面
        response = client.get('/upload/')
        if response.status_code == 302:
            print("✅ 上传页面URL正常 (需要登录)")
        else:
            print(f"⚠️  上传页面状态码: {response.status_code}")
        
        # 测试历史页面
        response = client.get('/history/')
        if response.status_code == 302:
            print("✅ 历史页面URL正常 (需要登录)")
        else:
            print(f"⚠️  历史页面状态码: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ URL测试失败: {e}")
        return False

def test_models():
    """测试数据模型"""
    print("\n📊 测试数据模型...")
    try:
        # 测试FileTransfer模型
        file_transfer = FileTransfer(
            file_name='test.txt',
            original_name='test.txt',
            file_size=1024,
            file_type='text/plain',
            status='pending',
            uploaded_by=User.objects.first()
        )
        
        # 测试模型方法
        size_display = file_transfer.get_file_size_display()
        extension = file_transfer.get_file_extension()
        is_image = file_transfer.is_image()
        
        print(f"✅ 模型方法测试成功")
        print(f"   文件大小显示: {size_display}")
        print(f"   文件扩展名: {extension}")
        print(f"   是否为图片: {is_image}")
        
        return True
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def test_static_files():
    """测试静态文件"""
    print("\n📁 测试静态文件...")
    try:
        css_file = Path('static/css/style.css')
        js_file = Path('static/js/main.js')
        
        if css_file.exists():
            print(f"✅ CSS文件存在: {css_file}")
        else:
            print(f"❌ CSS文件不存在: {css_file}")
        
        if js_file.exists():
            print(f"✅ JS文件存在: {js_file}")
        else:
            print(f"❌ JS文件不存在: {js_file}")
        
        return css_file.exists() and js_file.exists()
    except Exception as e:
        print(f"❌ 静态文件测试失败: {e}")
        return False

def test_templates():
    """测试模板文件"""
    print("\n📝 测试模板文件...")
    try:
        template_dir = Path('file_transfer/templates/file_transfer')
        templates = [
            'base.html',
            'dashboard.html',
            'upload.html',
            'history.html',
            'detail.html',
            'delete_confirm.html'
        ]
        
        missing_templates = []
        for template in templates:
            template_path = template_dir / template
            if template_path.exists():
                print(f"✅ 模板存在: {template}")
            else:
                print(f"❌ 模板缺失: {template}")
                missing_templates.append(template)
        
        return len(missing_templates) == 0
    except Exception as e:
        print(f"❌ 模板测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试文件传输系统...")
    print("=" * 50)
    
    tests = [
        test_database_connection,
        test_user_creation,
        test_urls,
        test_models,
        test_static_files,
        test_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统配置正确。")
        print("\n📋 下一步操作:")
        print("1. 运行 ./start.sh 启动系统")
        print("2. 访问 http://localhost:8001")
        print("3. 使用 admin/admin123 登录管理后台")
    else:
        print("⚠️  部分测试失败，请检查配置。")
    
    return passed == total

if __name__ == '__main__':
    main()