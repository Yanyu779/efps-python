// 文件传输系统主要JavaScript功能

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initFileUpload();
    initSearchAndFilter();
    initTableInteractions();
    initAnimations();
});

// 文件上传功能
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // 文件选择时显示文件名
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                displayFileInfo(file, this);
            }
        });
        
        // 拖拽上传支持
        const parent = input.closest('.form-group') || input.parentElement;
        if (parent) {
            parent.addEventListener('dragover', handleDragOver);
            parent.addEventListener('drop', handleDrop);
            parent.addEventListener('dragleave', handleDragLeave);
        }
    });
}

// 显示文件信息
function displayFileInfo(file, input) {
    const fileInfo = document.createElement('div');
    fileInfo.className = 'file-info mt-2 p-2 bg-light rounded';
    fileInfo.innerHTML = `
        <small class="text-muted">
            <i class="fas fa-file me-1"></i>
            ${file.name} (${formatFileSize(file.size)})
        </small>
    `;
    
    // 移除之前的文件信息
    const existingInfo = input.parentElement.querySelector('.file-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    input.parentElement.appendChild(fileInfo);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 拖拽上传处理
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-area', 'dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-area', 'dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = e.currentTarget.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.files = files;
            fileInput.dispatchEvent(new Event('change'));
        }
    }
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-area', 'dragover');
}

// 搜索和筛选功能
function initSearchAndFilter() {
    const searchForm = document.querySelector('form[method="get"]');
    if (searchForm) {
        const inputs = searchForm.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                // 自动提交表单
                searchForm.submit();
            });
        });
        
        // 搜索框实时搜索（延迟执行）
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    searchForm.submit();
                }, 500);
            });
        }
    }
}

// 表格交互功能
function initTableInteractions() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // 行选择功能
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('click', function(e) {
                // 如果点击的不是按钮或链接，则选中行
                if (!e.target.closest('a, button, input')) {
                    toggleRowSelection(this);
                }
            });
        });
        
        // 全选功能
        const selectAllCheckbox = table.querySelector('thead input[type="checkbox"]');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', function() {
                const checkboxes = table.querySelectorAll('tbody input[type="checkbox"]');
                checkboxes.forEach(checkbox => {
                    checkbox.checked = this.checked;
                });
                updateBulkActions();
            });
        }
    });
}

// 切换行选择状态
function toggleRowSelection(row) {
    const checkbox = row.querySelector('input[type="checkbox"]');
    if (checkbox) {
        checkbox.checked = !checkbox.checked;
        updateBulkActions();
    }
}

// 更新批量操作按钮
function updateBulkActions() {
    const checkboxes = document.querySelectorAll('tbody input[type="checkbox"]:checked');
    const bulkActions = document.querySelector('.bulk-actions');
    
    if (bulkActions) {
        if (checkboxes.length > 0) {
            bulkActions.style.display = 'block';
            bulkActions.querySelector('.selected-count').textContent = checkboxes.length;
        } else {
            bulkActions.style.display = 'none';
        }
    }
}

// 动画效果
function initAnimations() {
    // 页面加载动画
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // 滚动动画
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .alert').forEach(el => {
        observer.observe(el);
    });
}

// 消息提示功能
function showMessage(message, type = 'info', duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
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

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 文件上传进度
function updateUploadProgress(percent) {
    const progressBar = document.querySelector('.upload-progress .progress-bar');
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }
}

// 表格排序功能
function sortTable(table, columnIndex, type = 'string') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        if (type === 'number') {
            return parseFloat(aValue) - parseFloat(bValue);
        } else if (type === 'date') {
            return new Date(aValue) - new Date(bValue);
        } else {
            return aValue.localeCompare(bValue);
        }
    });
    
    // 重新插入排序后的行
    rows.forEach(row => tbody.appendChild(row));
}

// 导出功能
function exportTableData(format = 'csv') {
    const table = document.querySelector('.table');
    if (!table) return;
    
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => 
        Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
    
    if (format === 'csv') {
        exportToCSV(headers, rows);
    }
}

// 导出为CSV
function exportToCSV(headers, rows) {
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'file_transfer_history.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// 工具函数
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