// src/components/Nav.jsx
export default function Nav({ currentPage, onNavigate }) {
  const buttonBase = "px-3 py-1.5 rounded-lg text-sm transition-colors";
  const activeClass = "bg-slate-900 text-white hover:bg-slate-800";
  const inactiveClass = "bg-white border border-slate-300 hover:bg-slate-100";

  return (
    <nav className="flex items-center gap-2">
      <button
        onClick={() => onNavigate("menu")}
        className={`${buttonBase} ${currentPage === 'menu' ? activeClass : inactiveClass}`}
      >
        Menu
      </button>
      <button
        onClick={() => onNavigate("restaurant")}
        className={`${buttonBase} ${currentPage === 'restaurant' ? activeClass : inactiveClass}`}
      >
        Restaurant
      </button>
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