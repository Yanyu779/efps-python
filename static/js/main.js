// 文件传输系统主要JavaScript文件

// 全局变量
let sessionWarningShown = false;
let sessionTimeoutId = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeSystem();
});

// 系统初始化
function initializeSystem() {
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化确认对话框
    initializeConfirmDialogs();
    
    // 初始化文件上传拖拽
    initializeFileDragAndDrop();
    
    // 初始化搜索功能
    initializeSearch();
    
    // 初始化分页
    initializePagination();
}

// 初始化Bootstrap工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化确认对话框
function initializeConfirmDialogs() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// 初始化文件拖拽上传
function initializeFileDragAndDrop() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const container = input.closest('.file-upload-container') || input.parentElement;
        
        if (container) {
            container.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('dragover');
            });
            
            container.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
            });
            
            container.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    input.files = files;
                    // 触发change事件
                    const event = new Event('change', { bubbles: true });
                    input.dispatchEvent(event);
                }
            });
        }
    });
}

// 初始化搜索功能
function initializeSearch() {
    const searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(form => {
        const searchInput = form.querySelector('input[type="search"]');
        const clearButton = form.querySelector('.search-clear');
        
        if (searchInput && clearButton) {
            // 实时搜索
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    if (this.value.length >= 2 || this.value.length === 0) {
                        form.submit();
                    }
                }, 500);
            });
            
            // 清除搜索
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                form.submit();
            });
        }
    });
}

// 初始化分页
function initializePagination() {
    const paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                return false;
            }
        });
    });
}

// 显示消息提示
function showMessage(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 插入到页面顶部
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // 自动隐藏
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
}

// 显示加载状态
function showLoading(element, text = '加载中...') {
    if (element) {
        element.disabled = true;
        element.innerHTML = `<span class="loading-spinner me-2"></span>${text}`;
    }
}

// 隐藏加载状态
function hideLoading(element, originalText) {
    if (element) {
        element.disabled = false;
        element.innerHTML = originalText;
    }
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showMessage('已复制到剪贴板', 'success');
        }).catch(() => {
            showMessage('复制失败', 'danger');
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showMessage('已复制到剪贴板', 'success');
        } catch (err) {
            showMessage('复制失败', 'danger');
        }
        document.body.removeChild(textArea);
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出函数到全局作用域
window.FileTransferSystem = {
    showMessage,
    showLoading,
    hideLoading,
    formatFileSize,
    formatDateTime,
    copyToClipboard,
    debounce,
    throttle
};