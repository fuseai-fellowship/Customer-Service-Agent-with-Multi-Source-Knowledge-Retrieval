// src/lib/api.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export function setToken(token) {
  api.defaults.headers.common["Authorization"] = token ? `Bearer ${token}` : "";
}

// --- Auth ---
export async function login(email, password) {
  const { data } = await api.post("/auth/login", { email, password });
  setToken(data.access_token);
  localStorage.setItem("token", data.access_token);
  return data;
}

// --- Restaurant ---
export async function getRestaurant() {
  const { data } = await api.get("/restaurant");
  return data;
}

// --- Categories ---
export async function getCategories() {
  const { data } = await api.get("/categories");
  return data;
}
export async function createCategory(payload) {
  const { data } = await api.post("/categories", payload);
  return data;
}
export async function updateCategory(id, payload) {
  const { data } = await api.patch(`/categories/${id}`, payload);
  return data;
}
export async function deleteCategory(id) {
  await api.delete(`/categories/${id}`);
}

// --- Items ---
export async function getItems() {
  const { data } = await api.get("/items");
  return data;
}
export async function createItem(payload) {
  const { data } = await api.post("/items", payload);
  return data;
}
export async function updateItem(id, payload) {
  const { data } = await api.patch(`/items/${id}`, payload);
  return data;
}
export async function deleteItem(id) {
  await api.delete(`/items/${id}`);
}

// --- Variations ---
export async function getVariations(itemId) {
  const params = itemId ? { item_id: itemId } : {};
  const { data } = await api.get("/variations", { params });
  return data;
}
export async function createVariation(payload) {
  const { data } = await api.post("/variations", payload);
  return data;
}
export async function updateVariation(id, payload) {
  const { data } = await api.patch(`/variations/${id}`, payload);
  return data;
}
export async function deleteVariation(id) {
  await api.delete(`/variations/${id}`);
}

// --- Knowledge Base ---
export async function getKnowledge() {
  const { data } = await api.get("/knowledge");
  return data;
}
export async function createKnowledge(payload) {
  const { data } = await api.post("/knowledge", payload);
  return data;
}
export async function updateKnowledge(id, payload) {
  const { data } = await api.patch(`/knowledge/${id}`, payload);
  return data;
}
export async function deleteKnowledge(id) {
  await api.delete(`/knowledge/${id}`);
}

export default api;
