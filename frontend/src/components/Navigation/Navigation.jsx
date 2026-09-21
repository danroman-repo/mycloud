import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout, forceLogout } from '../../store/slices/authSlice';
import styles from './Navigation.module.css';

const Navigation = () => {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const { isAuthenticated, user } = useSelector((state) => state.auth);

    const handleLogout = async () => {
        try {
            await dispatch(logout());
            navigate('/');
        } catch (error) {
            dispatch(forceLogout());
            navigate('/');
        }
    };

    return (
        <nav className={styles.navigation}>
            <div className={styles.container}>
                <Link to="/" className={styles.logo}>
                    ☁️ My Cloud
                </Link>

                <ul className={styles.menu}>
                    {!isAuthenticated ? (
                        <>
                            <li className={styles.item}>
                                <Link to="/login" className={styles.link}>
                                    Вход
                                </Link>
                            </li>
                            <li className={styles.item}>
                                <Link to="/register" className={styles.link}>
                                    Регистрация
                                </Link>
                            </li>
                        </>
                    ) : (
                        <>
                            <li className={styles.item}>
                                <Link to="/dashboard" className={styles.link}>
                                    Мои файлы
                                </Link>
                            </li>
                            {user?.is_admin && (
                                <li className={styles.item}>
                                    <Link to="/admin" className={styles.link}>
                                        Админ-панель
                                    </Link>
                                </li>
                            )}
                            <li className={styles.item}>
                                <span className={styles.user}>
                                    👤 {user?.username}
                                </span>
                            </li>
                            <li className={styles.item}>
                                <button
                                    onClick={handleLogout}
                                    className={`${styles.link} ${styles.logoutBtn}`}
                                >
                                    Выход
                                </button>
                            </li>
                        </>
                    )}
                </ul>
            </div>
        </nav>
    );
};

export default Navigation;