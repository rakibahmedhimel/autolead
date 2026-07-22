import { NavLink, Outlet } from "react-router-dom";
import "../style/Layout.css";

function Layout() {
  return (
    <div className="app-shell">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">◈</div>
          <span>AutoLead</span>
        </div>

        <nav className="main-navigation">

          <NavLink to="/" className="nav-item">
            <span>◈</span>
            Dashboard
          </NavLink>

          <NavLink to="/tools" className="nav-item">
            <span>⚡</span>
            Tools
          </NavLink>

          <NavLink to="/jobs" className="nav-item">
            <span>◉</span>
            Jobs
          </NavLink>

          <NavLink to="/projects" className="nav-item">
            <span>▣</span>
            Projects
          </NavLink>

        </nav>

        <div className="sidebar-divider"></div>

        <nav className="secondary-navigation">

          <NavLink to="/contact" className="nav-item">
            <span>✉</span>
            Contact
          </NavLink>

          <NavLink to="/request-tool" className="nav-item">
            <span>＋</span>
            Request Tool
          </NavLink>

          <NavLink to="/about" className="nav-item">
            <span>ℹ</span>
            About
          </NavLink>

        </nav>

        <div className="sidebar-bottom">

          <NavLink to="/settings" className="nav-item">
            <span>⚙</span>
            Settings
          </NavLink>

          <div className="user-profile">

            <div className="user-avatar">
              R
            </div>

            <div className="user-info">
              <strong>Rakib</strong>
              <span>Administrator</span>
            </div>

          </div>

        </div>

      </aside>


      {/* Main Area */}
      <main className="main-area">

        {/* Top Header */}
        <header className="top-header">

          <div className="breadcrumb">
            AutoLead
          </div>

          <div className="header-actions">

            <button className="icon-button">
              🔔
            </button>

            <div className="header-user">
              <div className="small-avatar">
                R
              </div>

              <span>Rakib</span>
            </div>

          </div>

        </header>


        {/* Page Content */}
        <section className="page-content">

          <Outlet />

        </section>

      </main>

    </div>
  );
}

export default Layout;