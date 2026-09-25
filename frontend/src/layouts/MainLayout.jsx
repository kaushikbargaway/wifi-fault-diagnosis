import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertTriangle,
  Network,
  Wrench,
  BookOpen,
  Activity,
  Wifi,
} from 'lucide-react';
import styles from './MainLayout.module.css';

const NAV_LINKS = [
  { to: '/',           label: 'Dashboard',    icon: LayoutDashboard },
  { to: '/diagnosis',  label: 'Diagnosis',    icon: AlertTriangle   },
  { to: '/digital-twin', label: 'Digital Twin', icon: Network        },
  { to: '/recovery',   label: 'Recovery',     icon: Wrench          },
  { to: '/explanation', label: 'Explanation', icon: BookOpen        },
  { to: '/monitoring', label: 'Monitoring',   icon: Activity        },
];

function MainLayout() {
  return (
    <div className={styles.shell}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <Wifi size={22} />
          <span>TwinNet</span>
        </div>
        <nav className={styles.nav}>
          {NAV_LINKS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                isActive ? `${styles.link} ${styles.active}` : styles.link
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  );
}

export default MainLayout;
