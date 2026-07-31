import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  FaFolderOpen,
  FaHome,
  FaFilePdf,
  FaSignOutAlt,
  FaGraduationCap,
  FaUserGraduate,
} from "react-icons/fa";
import { getSessionUser, logout } from "../api";

function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getSessionUser();

  const links = [
    { to: "/dashboard", label: "Dashboard", icon: <FaHome /> },
    { to: "/mentor", label: "Mentor", icon: <FaUserGraduate /> },
    { to: "/organizer", label: "Organizer", icon: <FaFolderOpen /> },
    { to: "/viewer/1", label: "Viewer", icon: <FaFilePdf /> },
  ];

  function isActive(to) {
    if (to.startsWith("/viewer")) return location.pathname.startsWith("/viewer");
    return location.pathname === to;
  }

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const initial = user?.name ? user.name.charAt(0).toUpperCase() : "?";

  return (
    <div className="sidebar">
      <Link to="/" className="sidebar-logo flex" style={{ alignItems: "center", gap: 8 }}>
        <FaGraduationCap />
        CourseMate
      </Link>

      <div className="sidebar-nav">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className={`sidebar-link${isActive(link.to) ? " active" : ""}`}
          >
            {link.icon} {link.label}
          </Link>
        ))}
      </div>

      <div className="sidebar-footer">
        {user && (
          <div className="sidebar-user">
            <div className="avatar">{initial}</div>
            <div>
              <div className="sidebar-username">{user.name}</div>
              <div className="sidebar-email">{user.email}</div>
            </div>
          </div>
        )}

        <button
          className="sidebar-link"
          style={{ width: "100%", background: "none" }}
          onClick={handleLogout}
        >
          <FaSignOutAlt /> Log out
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
