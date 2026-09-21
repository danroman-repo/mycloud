import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true, // Важно для отправки cookies
    headers: {
        'Content-Type': 'application/json',
    },
});

const getCsrfToken = async () => {
    try {
        const response = await axios.get('/api/auth/csrf/', {  // ← измените здесь
            withCredentials: true,
        });
        return response.data.csrfToken;
    } catch (error) {
        console.error('Ошибка получения CSRF токена:', error);
        throw error;
    }
};

apiClient.interceptors.request.use(
    async (config) => {
        if (['post', 'put', 'delete', 'patch'].includes(config.method.toLowerCase())) {
            const csrfToken = await getCsrfToken();
            config.headers['X-CSRFToken'] = csrfToken;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            console.error('API Error:', error.response.data);

            if (error.response.status === 401) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    register: (data) => apiClient.post('/auth/register/', data),
    login: (data) => apiClient.post('/auth/login/', data),
    logout: () => apiClient.post('/auth/logout/'),
    getCurrentUser: () => apiClient.get('/auth/me/'),
};

export const usersAPI = {
    getAll: () => apiClient.get('/auth/admin/users/'),
    getById: (id) => apiClient.get(`/auth/admin/users/${id}/`),
    update: (id, data) => apiClient.patch(`/auth/admin/users/${id}/`, data),
    delete: (id) => apiClient.delete(`/auth/admin/users/${id}/`),
};

export const filesAPI = {
    getAll: (userId = null) => {
        const url = userId ? `/files/?user_id=${userId}` : '/files/';
        return apiClient.get(url);
    },
    upload: (formData) => apiClient.post('/files/upload/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    }),
    getById: (id) => apiClient.get(`/files/${id}/`),
    updateComment: (id, comment) => apiClient.patch(`/files/${id}/`, { comment }),
    rename: (id, displayName) => apiClient.put(`/files/${id}/rename/`, { display_name: displayName }),
    delete: (id) => apiClient.delete(`/files/${id}/`),
    share: (id) => apiClient.post(`/files/${id}/share/`),
    getDownloadUrl: (id) => `/api/files/${id}/download/`,
    getViewUrl: (id) => `/api/files/${id}/download/?view=1`,
    getPublicDownloadUrl: (publicHash) => `/api/public/files/${publicHash}/download/`,
    getPublicViewUrl: (publicHash) => `/api/public/files/${publicHash}/view/`,
};

export default apiClient;