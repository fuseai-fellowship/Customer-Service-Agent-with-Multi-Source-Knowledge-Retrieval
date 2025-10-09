import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export function setToken(token) {
  api.defaults.headers.common["Authorization"] = token ? `Bearer ${token}` : "";
}

export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  setToken(data.access_token);
  localStorage.setItem("token", data.access_token);
  return data;
}

export async function getRestaurant() {
  const { data } = await api.get("/restaurant");
  return data;
}

export async function getMenu(params = {}) {
  const { data } = await api.get("/menu", { params });
  return data;
}

export default api;
