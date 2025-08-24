from django.contrib import admin
from .models import FileTransfer

@admin.register(FileTransfer)
class FileTransferAdmin(admin.ModelAdmin):
    list_display = [
        'original_name', 
        'uploaded_by', 
        'file_size_display', 
        'status', 
        'uploaded_at',
        'file_type'
    ]
    list_filter = [
        'status', 
        'uploaded_at', 
        'file_type', 
        'uploaded_by'
    ]
    search_fields = [
        'original_name', 
        'description', 
        'tags', 
        'uploaded_by__username'
    ]
    readonly_fields = [
        'file_name', 
        'file_size', 
        'uploaded_by', 
        'uploaded_at'
    ]
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('文件信息', {
            'fields': ('original_name', 'file_path', 'file_size', 'file_type')
        }),
        ('状态信息', {
            'fields': ('status', 'uploaded_at', 'completed_at')
        }),
        ('用户信息', {
            'fields': ('uploaded_by',)
        }),
        ('描述信息', {
            'fields': ('description', 'tags'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = '文件大小'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')
    
    def has_add_permission(self, request):
        # 不允许通过管理后台添加文件
        return False
    
    def has_change_permission(self, request, obj=None):
        # 只允许修改状态和描述信息
        if obj:
            return request.user.is_superuser
        return True
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_processing']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f'{updated} 个文件已标记为完成')
    mark_as_completed.short_description = '标记为已完成'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} 个文件已标记为失败')
    mark_as_failed.short_description = '标记为失败'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} 个文件已标记为处理中')
    mark_as_processing.short_description = '标记为处理中'
