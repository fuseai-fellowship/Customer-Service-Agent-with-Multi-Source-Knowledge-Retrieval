// src/App.jsx
import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"; // Import Router components
import Login from "./pages/Login.jsx";
import Restaurant from "./pages/Restaurant.jsx";
import Menu from "./pages/Menu.jsx";
import Nav from "./components/Nav.jsx";
import { setToken } from "./lib/api";

export default function App() {
  const [token, setTok] = useState(localStorage.getItem("token"));

  useEffect(() => {
    setToken(token);
  }, [token]);

  return (
    <BrowserRouter>
      {!token ? (
        <Login onLogin={(t) => setTok(t)} />
      ) : (
        <div className="min-h-screen bg-slate-50 text-slate-900">
          <header className="bg-white/70 backdrop-blur border-b border-slate-200 sticky top-0 z-10">
            <div className="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
              <h1 className="text-lg font-semibold">AIF Resto Admin</h1>
              <Nav />
            </div>
          </header>

          <main className="mx-auto max-w-5xl px-4 py-6">
            <Routes>
              {/* Default route redirects to menu */}
              <Route path="/" element={<Navigate to="/restaurant" replace />} />
              <Route path="/menu" element={<Menu />} />
              <Route path="/restaurant" element={<Restaurant />} />
            </Routes>
          </main>
        </div>
      )}
    </BrowserRouter>
  );
}
