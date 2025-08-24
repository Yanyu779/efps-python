from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
    
    def __str__(self):
        return f"{self.original_name} - {self.uploaded_by.username}"
    
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
