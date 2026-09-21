import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import styles from './Home.module.css';

const Home = () => {
    const { isAuthenticated } = useSelector((state) => state.auth);

    return (
        <div className={styles.home}>
            <div className={styles.content}>
                <h1 className={styles.title}>Добро пожаловать в My Cloud</h1>
                <p className={styles.description}>
                    Безопасное облачное хранилище для ваших файлов.
                    Загружайте, управляйте и делитесь файлами легко.
                </p>

                {!isAuthenticated && (
                    <div className={styles.actions}>
                        <Link to="/register" className="btn btn-primary">
                            Начать работу
                        </Link>
                        <Link to="/login" className="btn btn-secondary">
                            Войти
                        </Link>
                    </div>
                )}

                {isAuthenticated && (
                    <div className={styles.actions}>
                        <Link to="/dashboard" className="btn btn-primary">
                            Перейти к файлам
                        </Link>
                    </div>
                )}

                <div className={styles.features}>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>🔒</div>
                        <h3 className={styles.featureTitle}>Безопасность</h3>
                        <p>Ваши файлы защищены современными технологиями шифрования</p>
                    </div>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>⚡</div>
                        <h3 className={styles.featureTitle}>Быстрый доступ</h3>
                        <p>Загружайте и скачивайте файлы с высокой скоростью</p>
                    </div>
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>🔗</div>
                        <h3 className={styles.featureTitle}>Общий доступ</h3>
                        <p>Делитесь файлами с помощью уникальных ссылок</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Home;