from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FileTransfer

class UserRegistrationForm(UserCreationForm):
    """用户注册表单"""
    email = forms.EmailField(required=True, help_text='必填。请输入有效的邮箱地址。')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定义字段标签
        self.fields['username'].label = '用户名'
        self.fields['email'].label = '邮箱'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        
        # 自定义帮助文本
        self.fields['username'].help_text = '必填。150个字符或更少。只能包含字母、数字和下划线。'
        self.fields['password1'].help_text = '您的密码不能与您的其他个人信息太相似。您的密码必须包含至少8个字符。您的密码不能是常用密码。您的密码不能全是数字。'
        self.fields['password2'].help_text = '请再次输入您的密码进行确认。'

class FileUploadForm(forms.ModelForm):
    file = forms.FileField(
        label='选择文件',
        help_text='支持所有类型的文件',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '*/*'
        })
    )
    
    description = forms.CharField(
        label='文件描述',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': '请输入文件描述（可选）'
        })
    )
    
    tags = forms.CharField(
        label='标签',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '用逗号分隔多个标签'
        })
    )
    
    class Meta:
        model = FileTransfer
        fields = ['file', 'description', 'tags']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 检查文件大小（限制为100MB）
            if file.size > 100 * 1024 * 1024:
                raise forms.ValidationError('文件大小不能超过100MB')
            
            # 检查文件类型（可选的安全检查）
            allowed_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
            file_extension = file.name.lower()
            for ext in allowed_extensions:
                if file_extension.endswith(ext):
                    raise forms.ValidationError('不允许上传可执行文件')
        
        return file
    
    def save(self, user, commit=True):
        instance = super().save(commit=False)
        instance.uploaded_by = user
        instance.original_name = self.cleaned_data['file'].name
        instance.file_name = self.cleaned_data['file'].name
        instance.file_size = self.cleaned_data['file'].size
        instance.file_path = self.cleaned_data['file']
        instance.file_type = self.cleaned_data['file'].content_type
        
        if commit:
            instance.save()
        return instance