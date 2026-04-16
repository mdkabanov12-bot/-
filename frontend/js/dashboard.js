// API базовый URL
const API_BASE_URL = 'http://localhost:8000/api';

// Проверка авторизации
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Проверка при загрузке
if (!checkAuth()) {
    // Редирект выполнится в checkAuth
}

// Глобальные переменные
let currentUser = null;

// Загрузка данных при инициализации
document.addEventListener('DOMContentLoaded', () => {
    loadUserInfo();
    loadNotifications();
    loadAppointments();
    loadServices();
    cleanupCompletedServices();
    
    // Кнопка выхода
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
    
    // Кнопка удаления всех уведомлений
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    if (deleteAllBtn) {
        deleteAllBtn.addEventListener('click', deleteAllNotifications);
    }
    
    // Модальные окна
    setupModal();
    setupChangeTimeModal();
});

// Выход
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    window.location.href = 'login.html';
}

// Загрузка информации о пользователе
async function loadUserInfo() {
    const userName = localStorage.getItem('user_name');
    const userRole = localStorage.getItem('user_role');
    
    document.getElementById('userName').textContent = userName || 'Пользователь';
    
    const roleElement = document.getElementById('userRole');
    roleElement.textContent = userRole === 'admin' ? 'Администратор' : 'Пользователь';
    roleElement.className = 'user-role ' + (userRole === 'admin' ? 'admin' : '');
    
    // Показываем админ панель только для админов
    if (userRole === 'admin') {
        document.getElementById('adminSection').style.display = 'block';
        document.getElementById('servicesSection').style.display = 'none';
        loadAdminServices();
    }
}

// Загрузка уведомлений
async function loadNotifications() {
    const userId = localStorage.getItem('user_id');
    const container = document.getElementById('notificationsList');
    console.log(userId);
    
    try {
        const response = await fetch(`${API_BASE_URL}/notifications/unread?user_id=${userId}`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки уведомлений');
        }
        
        const notifications = await response.json();
        
        if (notifications.length === 0) {
            container.innerHTML = '<p class="loading">Нет непрочитанных уведомлений</p>';
            if (document.getElementById('deleteAllBtn')) {
                document.getElementById('deleteAllBtn').style.display = 'none';
            }
            return;
        }
        
        if (document.getElementById('deleteAllBtn')) {
            document.getElementById('deleteAllBtn').style.display = 'block';
        }
        
        container.innerHTML = notifications.map(n => `
            <div class="notification-item unread">
                <div class="notification-content">
                    <p class="message">${n.message}</p>
                    <p class="time">${new Date(n.created_at).toLocaleString('ru-RU')}</p>
                </div>
                <button class="btn btn-delete" onclick="deleteNotification(${n.id})" title="Удалить уведомление">
                    ✕
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Удалить одно уведомление
async function deleteNotification(notificationId) {
    const userId = localStorage.getItem('user_id');
    
    if (!confirm('Вы уверены, что хотите удалить это уведомление?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}?user_id=${userId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка удаления уведомления');
        }
        
        // Перезагружаем список
        loadNotifications();
        
    } catch (error) {
        alert(error.message);
    }
}

// Удалить все уведомления
async function deleteAllNotifications() {
    const userId = localStorage.getItem('user_id');
    
    if (!confirm('Вы уверены, что хотите удалить все уведомления?')) {
        return;
    }
    
    try {
        // Получаем все уведомления
        const response = await fetch(`${API_BASE_URL}/notifications/unread?user_id=${userId}`);
        
        if (!response.ok) {
            throw new Error('Ошибка получения уведомлений');
        }
        
        const notifications = await response.json();
        
        if (notifications.length === 0) {
            alert('Нет уведомлений для удаления');
            return;
        }
        
        // Удаляем каждое уведомление
        for (const notification of notifications) {
            await fetch(`${API_BASE_URL}/notifications/${notification.id}?user_id=${userId}`, {
                method: 'DELETE'
            });
        }
        
        // Перезагружаем список
        loadNotifications();
        
    } catch (error) {
        alert(error.message);
    }
}

// Загрузка моих записей
async function loadAppointments() {
    const userId = localStorage.getItem('user_id');
    const container = document.getElementById('appointmentsList');
    
    try {
        const response = await fetch(`${API_BASE_URL}/my/appointments?user_id=${userId}`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки записей');
        }
        
        const appointments = await response.json();
        
        if (appointments.length === 0) {
            container.innerHTML = '<p class="loading">У вас нет активных записей</p>';
            return;
        }
        
        container.innerHTML = appointments.map(apt => `
            <div class="appointment-card">
                <h3>${apt.service_name}</h3>
                <span class="status ${apt.status}">${getStatusText(apt.status)}</span>
                <p class="info">📅 ${new Date(apt.service_start_time).toLocaleString('ru-RU')}</p>
                <p class="info">⏱️ ${apt.service_duration_minutes} мин</p>
                ${apt.status === 'upcoming' ? `
                    <button class="btn btn-secondary" onclick="cancelAppointment(${apt.service_id})" style="margin-top: 10px;">
                        Отменить запись
                    </button>
                ` : ''}
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Отмена записи
async function cancelAppointment(serviceId) {
    const userId = localStorage.getItem('user_id');
    
    if (!confirm('Вы уверены, что хотите отменить запись?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/my/appointments/${serviceId}?user_id=${userId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка отмены записи');
        }
        
        alert('Запись отменена');
        loadAppointments();
        
    } catch (error) {
        alert(error.message);
    }
}

// Загрузка услуг
async function loadServices() {
    const container = document.getElementById('servicesList');
    const userId = localStorage.getItem('user_id');
    
    try {
        const response = await fetch(`${API_BASE_URL}/services`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки услуг');
        }
        
        const services = await response.json();
        
        // Фильтруем только будущие услуги (не завершённые)
        const now = new Date();
        const futureServices = services.filter(service => {
            const serviceEnd = new Date(service.start_time);
            serviceEnd.setMinutes(serviceEnd.getMinutes() + service.duration_minutes);
            return serviceEnd > now;
        });
        
        if (futureServices.length === 0) {
            container.innerHTML = '<p class="loading">Нет доступных услуг</p>';
            return;
        }
        
        container.innerHTML = futureServices.map(service => {
            const isBooked = service.booked_users.includes(parseInt(userId));
            const startTime = new Date(service.start_time);
            const isPast = startTime < new Date();
            
            return `
                <div class="service-card">
                    <h3>${service.name}</h3>
                    <p class="info">📅 ${startTime.toLocaleString('ru-RU')}</p>
                    <p class="info">⏱️ ${service.duration_minutes} мин</p>
                    <p class="booked">Записано пользователей: ${service.booked_users.length}</p>
                    ${isBooked 
                        ? '<span class="status ongoing">Вы записаны</span>' 
                        : isPast 
                            ? '<span class="status completed">Запись закончилась</span>'
                            : `<button class="btn btn-primary" onclick="bookService(${service.id})">Записаться</button>`
                    }
                </div>
            `;
        }).join('');
        
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Запись на услугу
async function bookService(serviceId) {
    const userId = localStorage.getItem('user_id');
    
    try {
        const response = await fetch(`${API_BASE_URL}/services/${serviceId}/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: parseInt(userId)
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка записи');
        }
        
        alert('Вы успешно записаны на услугу!');
        loadServices();
        loadAppointments();
        
    } catch (error) {
        alert(error.message);
    }
}

// Загрузка услуг для админа
async function loadAdminServices() {
    const userId = localStorage.getItem('user_id');
    const container = document.getElementById('adminServicesList');
    
    try {
        const response = await fetch(`${API_BASE_URL}/services`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки услуг');
        }
        
        const services = await response.json();
        
        // Фильтруем только будущие услуги (не завершённые)
        const now = new Date();
        const futureServices = services.filter(service => {
            const serviceEnd = new Date(service.start_time);
            serviceEnd.setMinutes(serviceEnd.getMinutes() + service.duration_minutes);
            return serviceEnd > now;
        });
        
        if (futureServices.length === 0) {
            container.innerHTML = '<p class="loading">Нет услуг</p>';
            return;
        }
        
        container.innerHTML = futureServices.map(service => `
            <div class="admin-service-item">
                <div class="service-info">
                    <strong>${service.name}</strong>
                    <p>📅 ${new Date(service.start_time).toLocaleString('ru-RU')} | ⏱️ ${service.duration_minutes} мин</p>
                    <p>Записано: ${service.booked_users.length}</p>
                </div>
                <div class="service-actions">
                    <button class="btn btn-secondary" onclick="showServiceUsers(${service.id})">
                        Пользователи
                    </button>
                    <button class="btn btn-secondary" onclick="changeServiceTime(${service.id})">
                        Изменить время
                    </button>
                    <button class="btn btn-secondary" style="background: #e74c3c; color: white;" onclick="deleteService(${service.id})">
                        Удалить
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Показать пользователей на услуге
async function showServiceUsers(serviceId) {
    const userId = localStorage.getItem('user_id');
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/services/${serviceId}/users?user_id=${userId}`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки пользователей');
        }
        
        const users = await response.json();
        
        if (users.length === 0) {
            alert('На эту услугу нет записей');
            return;
        }
        
        const userList = users.map(u => 
            `${u.user_name} (${u.user_email}) - ${u.cancelled ? 'Отменено' : 'Активно'}`
        ).join('\n');
        
        alert(`Пользователи на услуге:\n\n${userList}`);
        
    } catch (error) {
        alert(error.message);
    }
}

// Изменить время услуги - открыть модальное окно
function changeServiceTime(serviceId) {
    const modal = document.getElementById('changeTimeModal');
    document.getElementById('changeServiceId').value = serviceId;
    
    // Установим текущее время по умолчанию
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('newServiceStartTime').value = now.toISOString().slice(0, 16);
    
    modal.style.display = 'flex';
}

// Настройка модального окна изменения времени
function setupChangeTimeModal() {
    const modal = document.getElementById('changeTimeModal');
    const closeBtn = modal.querySelector('.modal-close');
    const form = document.getElementById('changeTimeForm');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const serviceId = document.getElementById('changeServiceId').value;
        const newTime = document.getElementById('newServiceStartTime').value;
        const userId = localStorage.getItem('user_id');
        
        try {
            const response = await fetch(`${API_BASE_URL}/admin/services/${serviceId}/time?user_id=${userId}&new_start_time=${encodeURIComponent(newTime)}`, {
                method: 'PUT'
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Ошибка изменения времени');
            }
            
            alert('Время услуги изменено!');
            modal.style.display = 'none';
            loadAdminServices();
            
        } catch (error) {
            alert(error.message);
        }
    });
}

// Удалить услугу
async function deleteService(serviceId) {
    const userId = localStorage.getItem('user_id');
    
    if (!confirm('Вы уверены, что хотите удалить эту услугу? Все записи будут отменены.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/admin/services/${serviceId}?user_id=${userId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Ошибка удаления услуги');
        }
        
        alert('Услуга удалена');
        loadAdminServices();
        
    } catch (error) {
        alert(error.message);
    }
}

// Показать форму создания услуги
function showCreateServiceForm() {
    const modal = document.getElementById('createServiceModal');
    modal.style.display = 'flex';
}

// Настройка модального окна
function setupModal() {
    const modal = document.getElementById('createServiceModal');
    const closeBtn = modal.querySelector('.modal-close');
    const form = document.getElementById('createServiceForm');
    
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('serviceName').value;
        const duration = document.getElementById('serviceDuration').value;
        const startTime = document.getElementById('serviceStartTime').value;
        const userId = localStorage.getItem('user_id');
        
        try {
            const response = await fetch(`${API_BASE_URL}/admin/services?user_id=${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    duration_minutes: parseInt(duration),
                    start_time: startTime
                })
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Ошибка создания услуги');
            }
            
            alert('Услуга создана!');
            modal.style.display = 'none';
            form.reset();
            loadAdminServices();
            
        } catch (error) {
            alert(error.message);
        }
    });
}

// Текст статуса
function getStatusText(status) {
    const texts = {
        'upcoming': 'Предстоящая',
        'ongoing': 'Идёт сейчас',
        'cancelled': 'Отменена',
        'completed': 'Завершена'
    };
    return texts[status] || status;
}

// Очистка завершённых услуг
async function cleanupCompletedServices() {
    const userId = localStorage.getItem('user_id');
    const userRole = localStorage.getItem('user_role');
    
    // Только админ может запускать очистку
    if (userRole !== 'admin') {
        return;
    }
    
    try {
        await fetch(`${API_BASE_URL}/admin/services/cleanup-completed?user_id=${userId}`, {
            method: 'POST'
        });
    } catch (error) {
        console.error('Ошибка очистки завершённых услуг:', error);
    }
}
