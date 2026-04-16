// API базовый URL
const API_BASE_URL = 'http://localhost:8000/api';

// Проверка: если уже залогинен - редирект на dashboard
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (token && (window.location.pathname.includes('login.html') || window.location.pathname.includes('register.html'))) {
        window.location.href = 'dashboard.html';
    }
}

// Проверка авторизации при загрузке
checkAuth();

// Логин форма
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');
        
        try {
            // Формируем formData для OAuth2
            const formData = new URLSearchParams();
            formData.append('username', email);  // OAuth2 использует username для email
            formData.append('password', password);
            
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка входа');
            }
            
            // Сохраняем токен и данные пользователя
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('user_name', data.user_name);
            localStorage.setItem('user_role', data.user_role);
            
            // Редирект на dashboard
            window.location.href = 'dashboard.html';
            
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    });
}

// Регистрация форма
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const errorMessage = document.getElementById('errorMessage');
        
        // Проверка совпадения паролей
        if (password !== confirmPassword) {
            errorMessage.textContent = 'Пароли не совпадают';
            errorMessage.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password,
                    role: 'user'
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка регистрации');
            }
            
            // Успешная регистрация - редирект на login
            alert('Регистрация успешна! Теперь войдите в систему.');
            window.location.href = 'login.html';
            
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    });
}

// Выход из системы
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    window.location.href = 'login.html';
}
