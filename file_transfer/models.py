from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import os

class FileTransfer(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    original_name = models.CharField(max_length=255, verbose_name='原始文件名')
    file_size = models.BigIntegerField(verbose_name='文件大小(字节)')
    file_path = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='文件路径')
    file_type = models.CharField(max_length=100, verbose_name='文件类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='上传用户')
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    description = models.TextField(blank=True, verbose_name='文件描述')
    tags = models.CharField(max_length=500, blank=True, verbose_name='标签')
    
    class Meta:
        verbose_name = '文件传输'
        verbose_name_plural = '文件传输'
        ordering = ['-uploaded_at']
        # 添加权限
        permissions = [
            ("can_upload_file", "可以上传文件"),
            ("can_download_file", "可以下载文件"),
            ("can_delete_file", "可以删除文件"),
            ("can_view_file", "可以查看文件"),
        ]
    
    def __str__(self):
        return f"{self.original_name} - {self.uploaded_by.username}"
    
    def can_access(self, user):
        """检查用户是否可以访问此文件"""
        if not user.is_authenticated:
            return False
        
        # 文件所有者可以访问
        if user == self.uploaded_by:
            return True
        
        # 超级用户可以访问所有文件
        if user.is_superuser:
            return True
        
        # 这里可以添加更多的权限检查逻辑
        # 例如：用户组权限、共享权限等
        
        return False
    
    def can_download(self, user):
        """检查用户是否可以下载此文件"""
        if not self.can_access(user):
            return False
        
        # 检查文件是否存在
        if not os.path.exists(self.file_path.path):
            return False
        
        return True
    
    def can_delete(self, user):
        """检查用户是否可以删除此文件"""
        if not self.can_access(user):
            return False
        
        # 只有文件所有者和管理员可以删除
        if user == self.uploaded_by or user.is_superuser:
            return True
        
        return False
    
    def can_modify(self, user):
        """检查用户是否可以修改此文件"""
        if not self.can_access(user):
            return False
        
        # 只有文件所有者和管理员可以修改
        if user == self.uploaded_by or user.is_superuser:
            return True
        
        return False
    
    def get_file_size_display(self):
        """返回人类可读的文件大小"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_file_extension(self):
        """获取文件扩展名"""
        return os.path.splitext(self.original_name)[1]
    
    def is_image(self):
        """判断是否为图片文件"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return self.get_file_extension().lower() in image_extensions
    
    def get_absolute_url(self):
        """获取文件的绝对URL"""
        from django.urls import reverse
        return reverse('file_transfer:file_detail', args=[str(self.id)])
    
    def get_download_url(self):
        """获取下载URL"""
        from django.urls import reverse
        return reverse('file_transfer:file_download', args=[str(self.id)])
    
    def get_delete_url(self):
        """获取删除URL"""
        from django.urls import reverse
        return reverse('file_transfer:file_delete', args=[str(self.id)])
    
    def safe_delete(self, user):
        """安全删除文件"""
        if not self.can_delete(user):
            raise PermissionDenied("您没有权限删除此文件")
        
        try:
            # 删除物理文件
            if os.path.exists(self.file_path.path):
                os.remove(self.file_path.path)
            
            # 删除数据库记录
            self.delete()
            return True
        except Exception as e:
            raise Exception(f"删除文件失败: {str(e)}")
    
    def safe_download(self, user):
        """安全下载文件"""
        if not self.can_download(user):
            raise PermissionDenied("您没有权限下载此文件")
        
        if not os.path.exists(self.file_path.path):
            raise FileNotFoundError("文件不存在")
        
        return self.file_path.path
