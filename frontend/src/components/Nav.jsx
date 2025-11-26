import { NavLink } from "react-router-dom"; // Use NavLink for active styling

export default function Nav() {
  const buttonBase =
    "px-3 py-1.5 rounded-lg text-sm transition-colors text-center";
  // Helper to apply classes based on 'isActive' state
  const getLinkClass = ({ isActive }) =>
    `${buttonBase} ${
      isActive
        ? "bg-slate-900 text-white hover:bg-slate-800"
        : "bg-white border border-slate-300 hover:bg-slate-100"
    }`;

  return (
    <nav className="flex items-center gap-2">
      <NavLink to="/restaurant" className={getLinkClass}>
        Restaurant
      </NavLink>
      <NavLink to="/menu" className={getLinkClass}>
        Menu
      </NavLink>
      <button
        onClick={() => {
          localStorage.removeItem("token");
          location.reload();
        }}
        className={`${buttonBase} bg-rose-600 text-white hover:bg-rose-500`}
      >
        Logout
      </button>
    </nav>
  );
}
