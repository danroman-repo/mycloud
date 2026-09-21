import { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { usersAPI } from '../../api/client';
import styles from './Admin.module.css';

const Admin = () => {
    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useSelector((state) => state.auth);

    useEffect(() => {
        console.log('Текущий пользователь:', user);
        console.log('is_admin:', user?.is_admin);
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await usersAPI.getAll();
            console.log('Получены пользователи:', response.data);
            setUsers(response.data);
        } catch (err) {
            console.error('Ошибка загрузки пользователей:', err);
            const errorMsg = err.response?.data?.detail?.detail
                || err.response?.data?.detail
                || err.message
                || 'Ошибка загрузки пользователей';
            setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
        } finally {
            setIsLoading(false);
        }
    };

    const handleToggleAdmin = async (userId, currentStatus) => {
        try {
            await usersAPI.update(userId, { is_admin: !currentStatus });
            await fetchUsers();
        } catch (err) {
            console.error('Ошибка обновления:', err);
            setError('Ошибка обновления пользователя');
        }
    };

    const handleDeleteUser = async (userId, username) => {
        if (window.confirm(`Удалить пользователя ${username}?`)) {
            try {
                await usersAPI.delete(userId);
                await fetchUsers();
            } catch (err) {
                console.error('Ошибка удаления:', err);
                setError('Ошибка удаления пользователя');
            }
        }
    };

    if (isLoading) {
        return <div className={styles.loading}>Загрузка...</div>;
    }

    return (
        <div className={styles.page}>
            <h1 className={styles.title}>Админ-панель</h1>

            <div className={styles.info}>
                <p>
                    Ваш статус: <strong>{user?.is_admin ?
                        'Администратор' : 'Обычный пользователь'}</strong>
                </p>
            </div>

            {error && <div className={styles.errorMessage}>{error}</div>}

            <div className={styles.tableWrapper}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th className={styles.th}>ID</th>
                            <th className={styles.th}>Логин</th>
                            <th className={styles.th}>Полное имя</th>
                            <th className={styles.th}>Email</th>
                            <th className={styles.th}>Админ</th>
                            <th className={styles.th}>Файлов</th>
                            <th className={styles.th}>Размер</th>
                            <th className={styles.th}>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((u) => (
                            <tr key={u.id} className={styles.tr}>
                                <td className={styles.td}>{u.id}</td>
                                <td className={styles.td}>{u.username}</td>
                                <td className={styles.td}>{u.full_name}</td>
                                <td className={styles.td}>{u.email}</td>
                                <td className={styles.td}>
                                    <input
                                        type="checkbox"
                                        checked={u.is_admin}
                                        onChange={() => handleToggleAdmin(u.id, u.is_admin)}
                                    />
                                </td>
                                <td className={styles.td}>{u.files_count}</td>
                                <td className={styles.td}>{formatFileSize(u.files_total_size)}</td>
                                <td className={styles.td}>
                                    <div className={styles.actionButtons}>
                                        <a
                                            href={`/dashboard?user_id=${u.id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="btn btn-small btn-info"
                                            style={{ marginLeft: '5px' }}
                                        >
                                            📂 Файлы
                                        </a>
                                        <button
                                            className="btn btn-small btn-danger"
                                            onClick={() => handleDeleteUser(u.id, u.username)}
                                            disabled={u.id === user?.id}
                                            title={u.id === user?.id ? 'Нельзя удалить себя' : ''}
                                        >
                                            Удалить
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {users.length === 0 && !error && (
                    <p className={styles.emptyState}>Пользователи не найдены</p>
                )}
            </div>
        </div>
    );
};

const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

export default Admin;