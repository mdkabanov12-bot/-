// API базовый URL
const API_BASE_URL = 'http://localhost:8000/api';

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend initialized');
    loadUsers();
    loadServices();
    loadAppointments();
    loadNotifications();
});

// Загрузка пользователей
async function loadUsers() {
    const container = document.getElementById('users-content');
    try {
        const response = await fetch(`${API_BASE_URL}/users/`);
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="success">${JSON.stringify(data)}</p>`;
        } else {
            container.innerHTML = `<p class="error">Ошибка загрузки пользователей</p>`;
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Загрузка услуг
async function loadServices() {
    const container = document.getElementById('services-content');
    try {
        const response = await fetch(`${API_BASE_URL}/services/`);
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="success">${JSON.stringify(data)}</p>`;
        } else {
            container.innerHTML = `<p class="error">Ошибка загрузки услуг</p>`;
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Загрузка записей
async function loadAppointments() {
    const container = document.getElementById('appointments-content');
    try {
        const response = await fetch(`${API_BASE_URL}/appointments/`);
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="success">${JSON.stringify(data)}</p>`;
        } else {
            container.innerHTML = `<p class="error">Ошибка загрузки записей</p>`;
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// Загрузка уведомлений
async function loadNotifications() {
    const container = document.getElementById('notifications-content');
    try {
        const response = await fetch(`${API_BASE_URL}/notifications/`);
        if (response.ok) {
            const data = await response.json();
            container.innerHTML = `<p class="success">${JSON.stringify(data)}</p>`;
        } else {
            container.innerHTML = `<p class="error">Ошибка загрузки уведомлений</p>`;
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Ошибка: ${error.message}</p>`;
    }
}

// TODO: Добавить функции для CRUD операций
