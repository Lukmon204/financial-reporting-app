// Получение токена из localStorage
function getToken() {
    return localStorage.getItem('access_token');
}

// Проверка аутентификации
function checkAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
    }
}

// Форматирование чисел
function formatNumber(num) {
    return num.toLocaleString('ru-RU', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + '₽';
}

// Отображение предварительного просмотра
function showPreview(data) {
    const previewContent = document.getElementById('preview-content');
    previewContent.innerHTML = `
        <p><strong>🏢 База:</strong> ${data.base_name || 'Не указана'}</p>
        <p><strong>💵 Наличка:</strong> ${formatNumber(data.cash_sales)}</p>
        <p><strong>📦 Реализация:</strong> ${formatNumber(data.realization)}</p>
        <p><strong>📥 Поступления:</strong> ${formatNumber(data.incoming)}</p>
        <p><strong>🛒 Закупки:</strong> ${formatNumber(data.purchases)}</p>
        <p><strong>💰 Приход:</strong> ${formatNumber(data.income)}</p>
        <p><strong>💳 Оплата поставщикам:</strong> ${formatNumber(data.payment)}</p>
        <p><strong>💸 Расход:</strong> ${formatNumber(data.expenses)}</p>
        <p><strong>📊 Остаток:</strong> ${formatNumber(data.balance)}</p>
    `;
    
    document.getElementById('preview').classList.remove('hidden');
    document.getElementById('report-form').classList.add('hidden');
}

// Отправка отчета
async function submitReport(data) {
    try {
        const response = await fetch('/api/reports/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Отчет успешно отправлен!');
            document.getElementById('report-form').reset();
            document.getElementById('preview').classList.add('hidden');
            document.getElementById('report-form').classList.remove('hidden');
        } else {
            const errorData = await response.json();
            alert(`Ошибка: ${errorData.detail || 'Не удалось отправить отчет'}`);
        }
    } catch (error) {
        console.error('Ошибка при отправке:', error);
        alert('Произошла ошибка при отправке отчета');
    }
}

// Обработчики событий
document.addEventListener('DOMContentLoaded', function() {
    // Проверка аутентификации
    checkAuth();

    // Обработчик формы
    const form = document.getElementById('report-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Сбор данных формы
            const formData = new FormData(form);
            const reportData = {};
            
            for (let [key, value] of formData.entries()) {
                reportData[key] = parseFloat(value);
                
                // Проверка, что значение не отрицательное
                if (reportData[key] < 0) {
                    alert(`Значение ${key} не может быть отрицательным`);
                    return;
                }
            }
            
            // Показываем предварительный просмотр
            showPreview({
                ...reportData,
                base_name: 'Основная база' // В реальном приложении нужно получать из профиля
            });
        });
    }

    // Подтверждение отправки
    const confirmBtn = document.getElementById('confirm-send');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            const formData = new FormData(document.getElementById('report-form'));
            const reportData = {};
            
            for (let [key, value] of formData.entries()) {
                reportData[key] = parseFloat(value);
            }
            
            submitReport(reportData);
        });
    }

    // Отмена предварительного просмотра
    const cancelBtn = document.getElementById('cancel-preview');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            document.getElementById('preview').classList.add('hidden');
            document.getElementById('report-form').classList.remove('hidden');
        });
    }

    // Выход
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${getToken()}`
                    }
                });
            } catch (error) {
                console.error('Ошибка при выходе:', error);
            } finally {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        });
    }

    // Регистрация Service Worker для PWA
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/service-worker.js')
                .then(function(registration) {
                    console.log('SW зарегистрирован: ', registration);
                })
                .catch(function(registrationError) {
                    console.log('SW ошибка: ', registrationError);
                });
        });
    }
});