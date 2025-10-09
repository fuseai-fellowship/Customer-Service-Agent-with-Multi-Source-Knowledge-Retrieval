import React, { useEffect } from "react";
import Login from "./pages/Login.jsx";
import Restaurant from "./pages/Restaurant.jsx";
import Menu from "./pages/Menu.jsx";
import Nav from "./components/Nav.jsx";
import { setToken } from "./lib/api";

export default function App() {
  const [token, setTok] = React.useState(localStorage.getItem("token"));
  const [page, setPage] = React.useState("menu");

  useEffect(() => {
    setToken(token);
  }, [token]);

  if (!token) return <Login onLogin={(t) => setTok(t)} />;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="bg-white/70 backdrop-blur border-b border-slate-200 sticky top-0 z-10">
        <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold">AIF Resto Admin</h1>
          <Nav onNavigate={setPage} />
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-6">
        {page === "restaurant" ? <Restaurant /> : <Menu />}
      </main>
    </div>
  );
}
