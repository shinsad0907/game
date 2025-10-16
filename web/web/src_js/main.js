// Global variables
let selectedPorts = [];
let multipleAccounts = [];

// Generate port checkboxes
function initializePorts() {
    const portGrid = document.getElementById('port-grid');
    
    const ports = [
        { id: 1, name: 'sasa2.君8866' },
        { id: 2, name: '78win9.pro' },
        { id: 3, name: 'shbet800.com' },
    ];
    
    ports.forEach(port => {
        const portItem = document.createElement('div');
        portItem.className = 'port-item';
        portItem.innerHTML = `
            <input type="checkbox" class="port-checkbox" id="port-${port.id}" value="${port.name}">
            <label class="port-label" for="port-${port.id}">${port.name}</label>
        `;
        portGrid.appendChild(portItem);
    });

    document.querySelectorAll('.port-checkbox').forEach(cb => {
        cb.addEventListener('change', updatePortCount);
    });
}

function updatePortCount() {
    const count = document.querySelectorAll('.port-checkbox:checked').length;
    document.getElementById('modal-selected-count').textContent = count;
}

// Settings Modal
function openSettingsModal() {
    document.getElementById('settings-modal').classList.add('show');
    loadPathConfig();
}

function closeSettingsModal() {
    document.getElementById('settings-modal').classList.remove('show');
}

async function saveSettings() {
    const pathConfig = {
        tesseractPath: document.getElementById('tesseract-path').value,
        // firefoxPath: document.getElementById('firefox-path').value,
        // geckodriverPath: document.getElementById('geckodriver-path').value
    };
    
    try {
        const result = await eel.save_path_config(pathConfig)();
        if (result.status === 'success') {
            closeSettingsModal();
            alert('✓ Đã lưu cấu hình đường dẫn!');
        } else {
            alert('✗ Lỗi khi lưu cấu hình: ' + result.message);
        }
    } catch (error) {
        console.error('Error saving config:', error);
        alert('✗ Lỗi khi lưu cấu hình!');
    }
}

async function loadPathConfig() {
    try {
        const config = await eel.load_path_config()();
        if (config) {
            if (config.tesseractPath) {
                document.getElementById('tesseract-path').value = config.tesseractPath;
            }
            // if (config.firefoxPath) {
            //     document.getElementById('firefox-path').value = config.firefoxPath;
            // }
            // if (config.geckodriverPath) {
            //     document.getElementById('geckodriver-path').value = config.geckodriverPath;
            // }
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Port Modal
function openPortModal() {
    document.getElementById('port-modal').classList.add('show');
}

function closePortModal() {
    document.getElementById('port-modal').classList.remove('show');
}

function savePortSelection() {
    selectedPorts = Array.from(document.querySelectorAll('.port-checkbox:checked')).map(cb => cb.value);
    document.getElementById('selected-ports-count').textContent = selectedPorts.length;
    closePortModal();
}

// Update account count
function updateAccountPreview() {
    const textarea = document.getElementById('multiple-accounts-textarea');
    const lines = textarea.value.trim().split('\n').filter(line => line.trim());
    document.getElementById('account-count').textContent = lines.length;
}

// Parse account data with proxy
function parseAccountData(line, index) {
    const parts = line.split('|').map(p => p.trim());
    
    const errors = [];
    if (parts.length !== 9) {
        errors.push(`Không đúng 9 trường (hiện tại: ${parts.length})`);
    }
    
    const [username, password, fullname, phone, email, bankAccount, accountNumber, withdrawCode, proxy] = parts;
    
    // Validate từng trường
    if (!username) errors.push('Thiếu username');
    if (!password) errors.push('Thiếu password');
    if (!fullname) errors.push('Thiếu họ tên');
    
    if (!phone) {
        errors.push('Thiếu SĐT');
    } else if (!/^[0-9]{10,11}$/.test(phone)) {
        errors.push('SĐT không hợp lệ (10-11 số)');
    }
    
    if (!email) {
        errors.push('Thiếu email');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errors.push('Email không hợp lệ');
    }
    
    if (!bankAccount) errors.push('Thiếu tên ngân hàng');
    if (!accountNumber) errors.push('Thiếu số tài khoản');
    if (!withdrawCode) errors.push('Thiếu mã rút tiền');
    
    if (!proxy) {
        errors.push('Thiếu proxy');
    } else {
        // Validate proxy format: host:port:user:pass
        const proxyParts = proxy.split(':');
        if (proxyParts.length !== 4) {
            errors.push('Proxy không đúng định dạng (host:port:user:pass)');
        }
    }
    
    return {
        username,
        password,
        fullname,
        phone,
        email,
        bankAccount,
        accountNumber,
        withdrawCode,
        proxy,
        valid: errors.length === 0,
        errors: errors
    };
}

// Preview accounts
function previewAccounts() {
    const textarea = document.getElementById('multiple-accounts-textarea');
    const lines = textarea.value.trim().split('\n').filter(line => line.trim());
    
    if (lines.length === 0) {
        alert('⚠️ Chưa nhập tài khoản nào!');
        return;
    }
    
    multipleAccounts = [];
    const tbody = document.getElementById('account-preview-tbody');
    tbody.innerHTML = '';
    
    let validCount = 0;
    let invalidCount = 0;
    
    lines.forEach((line, index) => {
        const account = parseAccountData(line, index);
        multipleAccounts.push(account);
        
        if (account.valid) validCount++;
        else invalidCount++;
        
        const row = tbody.insertRow();
        const statusClass = account.valid ? 'badge-success' : 'badge-error';
        const statusText = account.valid ? '✓ Hợp lệ' : '✗ Lỗi';
        const statusTitle = account.valid ? 'Tất cả trường đều hợp lệ' : account.errors.join(', ');
        
        // Hàm hiển thị field với màu đỏ nếu trống/lỗi
        const displayField = (value, fieldName) => {
            if (!value) return '<span style="color: #ef4444; font-weight: 600;">Trống</span>';
            
            // Validate specific fields
            if (fieldName === 'phone' && !/^[0-9]{10,11}$/.test(value)) {
                return `<span style="color: #ef4444;" title="SĐT không hợp lệ">${value}</span>`;
            }
            if (fieldName === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                return `<span style="color: #ef4444;" title="Email không hợp lệ">${value}</span>`;
            }
            if (fieldName === 'proxy' && value.split(':').length !== 4) {
                return `<span style="color: #ef4444;" title="Proxy không đúng định dạng">${value}</span>`;
            }
            
            return value;
        };
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${displayField(account.username, 'username')}</td>
            <td>${displayField(account.password, 'password')}</td>
            <td>${displayField(account.fullname, 'fullname')}</td>
            <td>${displayField(account.phone, 'phone')}</td>
            <td style="font-size: 11px;">${displayField(account.email, 'email')}</td>
            <td>${displayField(account.bankAccount, 'bank')}</td>
            <td>${displayField(account.accountNumber, 'accountNumber')}</td>
            <td>${displayField(account.withdrawCode, 'withdrawCode')}</td>
            <td style="font-size: 10px;">${displayField(account.proxy, 'proxy')}</td>
            <td>
                <span class="badge ${statusClass}" title="${statusTitle}" style="cursor: help;">
                    ${statusText}
                </span>
            </td>
        `;
    });
    
    // Update counters
    document.getElementById('valid-account-count').textContent = validCount;
    document.getElementById('invalid-account-count').textContent = invalidCount;
    document.getElementById('account-preview-container').style.display = 'block';
    
    // Show summary alert
    if (invalidCount > 0) {
        alert(`⚠️ KẾT QUẢ KIỂM TRA:\n\n✓ Hợp lệ: ${validCount} tài khoản\n✗ Lỗi: ${invalidCount} tài khoản\n\n⚠️ Vui lòng sửa các tài khoản lỗi trước khi đăng ký!`);
    } else {
        alert(`✓ HOÀN HẢO!\n\nTất cả ${validCount} tài khoản đều hợp lệ và sẵn sàng đăng ký!`);
    }
}

// File selection functions
async function selectTesseractPath() {
    try {
        const path = await eel.select_file('Tesseract')();
        if (path) {
            document.getElementById('tesseract-path').value = path;
        }
    } catch (error) {
        console.error('Error selecting Tesseract path:', error);
        alert('Lỗi khi chọn file tesseract.exe');
    }
}

async function selectFirefoxPath() {
    try {
        const path = await eel.select_file('Firefox')();
        if (path) {
            document.getElementById('firefox-path').value = path;
        }
    } catch (error) {
        console.error('Error selecting Firefox path:', error);
        alert('Lỗi khi chọn file firefox.exe');
    }
}

async function selectGeckodriverPath() {
    try {
        const path = await eel.select_file('Geckodriver')();
        if (path) {
            document.getElementById('geckodriver-path').value = path;
        }
    } catch (error) {
        console.error('Error selecting Geckodriver path:', error);
        alert('Lỗi khi chọn file geckodriver.exe');
    }
}

// Registration functions
// Registration functions
async function startRegistration() {
    // Validate ports
    if (selectedPorts.length === 0) {
        alert('⚠️ Vui lòng chọn ít nhất 1 cổng game!');
        return;
    }
    
    // Validate accounts
    if (multipleAccounts.length === 0) {
        alert('⚠️ Vui lòng nhập tài khoản và nhấn "Xem trước & Kiểm tra"!');
        return;
    }
    
    const invalidAccounts = multipleAccounts.filter(a => !a.valid);
    if (invalidAccounts.length > 0) {
        alert(`⚠️ Có ${invalidAccounts.length} tài khoản không hợp lệ!\n\nVui lòng kiểm tra lại bảng xem trước.`);
        return;
    }
    
    // LOGIC MỚI: Cho phép nhiều tài khoản hơn số cổng
    // Mỗi cổng sẽ tạo nhiều tài khoản
    const accountsPerPort = Math.ceil(multipleAccounts.length / selectedPorts.length);
    
    // Hiển thị thông tin sẽ đăng ký
    const confirmMessage = `📋 XÁC NHẬN ĐĂNG KÝ:\n\n` +
        `• Số cổng: ${selectedPorts.length}\n` +
        `• Số tài khoản: ${multipleAccounts.length}\n` +
        `• Mỗi cổng: ~${accountsPerPort} tài khoản\n\n` +
        `Bạn có muốn tiếp tục?`;
    
    if (!confirm(confirmMessage)) {
        return;
    }

    const config = {
        ports: selectedPorts,
        accounts: multipleAccounts, // GỬI TẤT CẢ TÀI KHOẢN
        tesseractPath: document.getElementById('tesseract-path').value,
        // firefoxPath: document.getElementById('firefox-path').value,
        // geckodriverPath: document.getElementById('geckodriver-path').value
    };

    try {
        const result = await eel.start_registration(config)();
        if (result.status === 'success') {
            console.log('✓ Đã bắt đầu đăng ký!');
        } else {
            alert('✗ ' + result.message);
        }
    } catch (error) {
        console.error('Error starting registration:', error);
        alert('✗ Lỗi khi bắt đầu đăng ký!');
    }
}

function stopRegistration() {
    eel.stop_registration();
    alert('⏹️ Đã dừng quá trình đăng ký!');
}

function exportResults() {
    const tbody = document.getElementById('results-tbody');
    if (tbody.children[0]?.children.length === 1) {
        alert('⚠️ Không có dữ liệu để export!');
        return;
    }
    alert('📊 Chức năng export đang được phát triển!');
}

function clearTable() {
    if (confirm('⚠️ Bạn có chắc muốn xóa toàn bộ dữ liệu?')) {
        document.getElementById('results-tbody').innerHTML = `
            <tr>
                <td colspan="12">
                    <div class="empty-state">
                        <i class="fas fa-inbox"></i>
                        <div>Chưa có dữ liệu. Nhấn "Bắt đầu đăng ký" để bắt đầu.</div>
                    </div>
                </td>
            </tr>
        `;
        document.getElementById('success-count').textContent = '0';
        document.getElementById('failed-count').textContent = '0';
        document.getElementById('total-count').textContent = '0';
    }
}

eel.expose(addResultRow);
function addResultRow(data) {
    const tbody = document.getElementById('results-tbody');
    
    // Xóa empty state nếu có
    if (tbody.children[0]?.children.length === 1) {
        tbody.innerHTML = '';
    }

    const row = tbody.insertRow();
    const statusClass = data.status === 'success' ? 'badge-success' : 
                        data.status === 'pending' ? 'badge-pending' : 'badge-error';
    const statusText = data.status === 'success' ? 'Thành công' :
                        data.status === 'pending' ? 'Đang xử lý' : 'Thất bại';

    row.id = `row-${data.stt}`;
    row.innerHTML = `
        <td>${data.stt}</td>
        <td>${data.port}</td>
        <td>${data.username}</td>
        <td>${data.password}</td>
        <td>${data.phone}</td>
        <td>${data.email}</td>
        <td>${data.fullname}</td>
        <td>${data.bankAccount}</td>
        <td>${data.withdrawCode}</td>
        <td style="font-size: 11px;">${data.proxy}</td>
        <td><span class="badge ${statusClass}" id="status-${data.stt}">${statusText}</span></td>
        <td>
            <button class="btn btn-secondary btn-icon" onclick="viewDetail(${data.stt})">
                <i class="fas fa-eye"></i>
            </button>
        </td>
    `;

    // Cập nhật counter
    const total = parseInt(document.getElementById('total-count').textContent) + 1;
    document.getElementById('total-count').textContent = total;

    // Scroll xuống dòng mới
    row.scrollIntoView({ behavior: 'smooth', block: 'end' });
}
eel.expose(updateResultRow);
function updateResultRow(stt, status) {
    const row = document.getElementById(`row-${stt}`);
    if (!row) return;

    const statusSpan = document.getElementById(`status-${stt}`);
    if (!statusSpan) return;

    // Xóa class cũ
    statusSpan.classList.remove('badge-success', 'badge-pending', 'badge-error');

    // Thêm class mới và text
    if (status === 'success') {
        statusSpan.classList.add('badge-success');
        statusSpan.textContent = 'Thành công';
        
        // Cập nhật counter
        const success = parseInt(document.getElementById('success-count').textContent) + 1;
        document.getElementById('success-count').textContent = success;
    } else if (status === 'error') {
        statusSpan.classList.add('badge-error');
        statusSpan.textContent = 'Thất bại';
        
        // Cập nhật counter
        const failed = parseInt(document.getElementById('failed-count').textContent) + 1;
        document.getElementById('failed-count').textContent = failed;
    }

    // Highlight dòng vừa cập nhật
    row.style.backgroundColor = status === 'success' ? '#d4edda' : '#f8d7da';
    setTimeout(() => {
        row.style.backgroundColor = '';
    }, 2000);
}
function viewDetail(stt) {
    alert(`📋 Chi tiết tài khoản #${stt}`);
}

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initializePorts();
    loadPathConfig();
    
    const accountTextarea = document.getElementById('multiple-accounts-textarea');
    if (accountTextarea) {
        accountTextarea.addEventListener('input', updateAccountPreview);
    }
});