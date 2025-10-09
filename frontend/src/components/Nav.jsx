export default function Nav({ onNavigate }) {
  return (
    <nav className="flex items-center gap-2">
      <button
        onClick={() => onNavigate("menu")}
        className="px-3 py-1.5 rounded-lg bg-slate-900 text-white hover:bg-slate-800 text-sm"
      >
        Menu
      </button>
      <button
        onClick={() => onNavigate("restaurant")}
        className="px-3 py-1.5 rounded-lg bg-white border border-slate-300 hover:bg-slate-100 text-sm"
      >
        Restaurant
      </button>
      <button
        onClick={() => {
          localStorage.removeItem("token");
          location.reload();
        }}
        className="px-3 py-1.5 rounded-lg bg-rose-600 text-white hover:bg-rose-500 text-sm"
      >
        Logout
      </button>
    </nav>
  );
}
