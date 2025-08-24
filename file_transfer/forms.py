from django import forms
from .models import FileTransfer

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