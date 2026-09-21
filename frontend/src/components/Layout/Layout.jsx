import { Outlet } from 'react-router-dom';
import Navigation from '../Navigation/Navigation';
import styles from './Layout.module.css';

const Layout = () => {
    return (
        <div className={styles.layout}>
            <Navigation />
            <main className={styles.mainContent}>
                <Outlet />
            </main>
        </div>
    );
};

export default Layout;