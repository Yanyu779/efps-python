# 文件传输系统

一个基于Django构建的现代化文件传输系统，具有文件上传、下载、历史记录查看等功能。

## 功能特性

### 核心功能
- 📁 **文件上传**: 支持拖拽上传，文件大小限制100MB
- 📥 **文件下载**: 安全的文件下载服务
- 📊 **传输历史**: 完整的文件传输记录和统计
- 🔍 **搜索筛选**: 支持文件名、描述、标签搜索
- 📱 **响应式设计**: 支持移动端和桌面端

### 高级功能
- 🎨 **图片预览**: 自动识别图片文件并提供预览
- 🏷️ **标签系统**: 支持文件分类和标签管理
- 📈 **数据统计**: 文件数量、存储空间等统计信息
- 🔐 **用户认证**: 基于Django内置的用户系统
- ⚡ **实时搜索**: 搜索框实时筛选功能

## 技术栈

- **后端**: Django 5.2.5
- **前端**: Bootstrap 5, Font Awesome
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **文件存储**: 本地文件系统
- **认证**: Django内置用户系统

## 快速开始

### 环境要求
- Python 3.8+
- pip
- 虚拟环境支持

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd file_transfer_system
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **创建超级用户**
```bash
python manage.py createsuperuser
```

6. **启动开发服务器**
```bash
python manage.py runserver
```

7. **访问系统**
- 主页: http://127.0.0.1:8000/
- 管理后台: http://127.0.0.1:8000/admin/

## 项目结构

```
file_transfer_system/
├── file_transfer/                 # 主应用
│   ├── models.py                 # 数据模型
│   ├── views.py                  # 视图函数
│   ├── forms.py                  # 表单类
│   ├── urls.py                   # URL配置
│   ├── admin.py                  # 管理后台配置
│   └── templates/                # 模板文件
│       └── file_transfer/
│           ├── base.html         # 基础模板
│           ├── dashboard.html    # 仪表板
│           ├── upload.html       # 文件上传
│           ├── history.html      # 传输历史
│           ├── detail.html       # 文件详情
│           └── delete_confirm.html # 删除确认
├── static/                       # 静态文件
│   ├── css/style.css            # 自定义样式
│   └── js/main.js               # 自定义脚本
├── media/                        # 上传文件存储
├── manage.py                     # Django管理脚本
├── requirements.txt              # 项目依赖
└── README.md                     # 项目说明
```

## 使用说明

### 文件上传
1. 点击"上传文件"菜单
2. 选择要上传的文件
3. 添加文件描述和标签（可选）
4. 点击"开始上传"

### 查看历史
1. 点击"传输历史"菜单
2. 使用搜索和筛选功能
3. 查看文件详细信息
4. 下载或删除文件

### 管理后台
1. 访问 `/admin/` 路径
2. 使用超级用户账号登录
3. 管理文件传输记录
4. 批量操作文件状态

## 配置说明

### 文件上传设置
- 最大文件大小: 100MB
- 支持的文件类型: 所有类型
- 存储路径: `media/uploads/YYYY/MM/DD/`

### 安全设置
- 禁止上传可执行文件
- 用户认证和权限控制
- CSRF保护

## 部署说明

### 生产环境配置
1. 修改 `settings.py` 中的 `DEBUG = False`
2. 配置生产数据库（PostgreSQL推荐）
3. 配置静态文件和媒体文件服务
4. 设置 `SECRET_KEY` 环境变量
5. 配置日志系统

### 使用Nginx + Gunicorn
```bash
pip install gunicorn
gunicorn file_transfer_system.wsgi:application
```

## 开发计划

### 近期功能
- [ ] 文件分享链接
- [ ] 批量文件操作
- [ ] 文件版本管理
- [ ] 在线文件预览

### 长期规划
- [ ] 云存储集成
- [ ] 文件加密传输
- [ ] 多用户权限管理
- [ ] API接口开发

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 项目讨论区

---

**注意**: 这是一个开发版本，请勿在生产环境中直接使用。建议在生产环境中进行充分测试和配置。