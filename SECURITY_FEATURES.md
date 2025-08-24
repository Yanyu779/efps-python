# 文件传输系统安全特性说明

## 概述

本文件传输系统已经实现了完整的用户认证和会话管理功能，确保所有操作都需要用户登录后才能执行，并且具有5分钟无操作自动断开的安全机制。

## 主要安全特性

### 1. 用户认证系统

#### 登录保护
- 所有主要页面都使用 `@login_required` 装饰器保护
- 未登录用户访问任何受保护页面都会自动重定向到登录页面
- 支持用户注册和登录功能

#### 自定义登录页面
- 美观的登录界面，支持用户名/密码认证
- 登录成功后自动重定向到仪表板
- 登录失败时显示错误提示

### 2. 会话管理

#### 会话超时控制
- **5分钟无操作自动断开**：这是系统的核心安全特性
- 会话超时设置在 `settings.py` 中配置：`SESSION_COOKIE_AGE = 300`
- 浏览器关闭时自动清除会话：`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`

#### 活动监控
- 实时监控用户活动（鼠标移动、键盘输入、点击等）
- 每次用户活动都会重置超时计时器
- 定期发送心跳包保持会话活跃

### 3. 中间件安全

#### SessionTimeoutMiddleware
- 在每个请求前检查会话是否超时
- 自动处理超时会话的登出逻辑
- 支持AJAX和普通请求的不同处理方式

#### ActivityTrackingMiddleware
- 跟踪用户的所有操作活动
- 排除静态文件和媒体文件的访问记录
- 实时更新最后活动时间

### 4. 前端安全监控

#### JavaScript会话监控
- 监听用户活动事件（mousedown, mousemove, keypress, scroll, touchstart, click）
- 30秒发送一次心跳包到服务器
- 每分钟检查一次会话状态
- 超时时自动跳转到登录页面

#### 实时警告系统
- 会话即将超时时显示警告提示
- 自动断开后显示友好提示信息
- 支持移动端触摸事件

## 技术实现

### 后端实现

#### 设置配置
```python
# 会话配置
SESSION_COOKIE_AGE = 300  # 5分钟 = 300秒
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# 登录配置
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
```

#### 中间件
```python
MIDDLEWARE = [
    # ... 其他中间件
    'file_transfer.middleware.SessionTimeoutMiddleware',
    'file_transfer.middleware.ActivityTrackingMiddleware',
]
```

#### 视图保护
```python
@login_required
def protected_view(request):
    # 只有登录用户才能访问
    pass
```

### 前端实现

#### 会话监控脚本
```javascript
// 监听用户活动
const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
events.forEach(event => {
    document.addEventListener(event, resetTimeout, true);
});

// 定期发送心跳
setInterval(updateLastActivity, 30000); // 30秒

// 定期检查会话状态
setInterval(checkSession, 60000); // 1分钟
```

## 使用方法

### 1. 启动系统
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 2. 访问系统
- 系统地址：http://localhost:8000
- 默认会重定向到登录页面：http://localhost:8000/login/

### 3. 用户管理
- 新用户可以通过注册页面创建账户
- 使用用户名和密码登录系统
- 登录后可以访问所有功能

### 4. 安全测试
- 登录后，5分钟内不进行任何操作
- 系统会自动断开会话并跳转到登录页面
- 重新登录后可以继续使用

## 安全建议

### 1. 生产环境部署
- 修改 `SECRET_KEY` 为强随机字符串
- 设置 `DEBUG = False`
- 配置 HTTPS 和安全的 Cookie 设置
- 使用环境变量管理敏感配置

### 2. 密码策略
- 实施强密码策略
- 定期要求用户更改密码
- 考虑添加双因素认证

### 3. 日志监控
- 记录所有登录尝试
- 监控异常活动模式
- 设置安全告警

### 4. 定期安全审查
- 定期检查系统日志
- 更新依赖包版本
- 进行安全漏洞扫描

## 故障排除

### 常见问题

#### 1. 会话频繁断开
- 检查浏览器是否支持JavaScript
- 确认网络连接稳定
- 检查服务器时间设置

#### 2. 登录后立即断开
- 检查中间件配置
- 确认数据库连接正常
- 查看服务器错误日志

#### 3. 心跳包失败
- 检查网络连接
- 确认API端点可访问
- 查看浏览器控制台错误

### 调试模式
```python
# 在settings.py中启用调试
DEBUG = True

# 查看详细的错误信息
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 总结

本文件传输系统实现了企业级的安全特性，确保：

1. **访问控制**：所有操作都需要用户认证
2. **会话安全**：5分钟无操作自动断开
3. **实时监控**：持续监控用户活动
4. **自动保护**：超时自动登出和重定向
5. **用户友好**：清晰的提示和警告信息

这些安全特性确保了系统的安全性和可用性，适合在生产环境中使用。