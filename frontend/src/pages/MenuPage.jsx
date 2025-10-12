// src/pages/Menu.jsx
import React, { useState, useEffect, useCallback } from "react";
import MenuJournalTable from "../components/MenuJournalTable";
import MenuItemFormModal from "../components/MenuItemFormModal";
import { getMenu, createMenuItem, updateMenuItem, deleteMenuItem } from "../lib/api";

export default function MenuPage() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRow, setEditingRow] = useState(null);
  const [isPosting, setIsPosting] = useState(false);
  const [postError, setPostError] = useState(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMenu();
      setRows(data);
    } catch (err) {
      setError("Failed to load menu items.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleCreate = () => {
    setEditingRow(null);
    setPostError(null);
    setIsModalOpen(true);
  };

  const handleEdit = (row) => {
    setEditingRow(row);
    setPostError(null);
    setIsModalOpen(true);
  };

  const handleDelete = async (row) => {
    if (window.confirm(`Are you sure you want to delete "${row.name}"?`)) {
      try {
        await deleteMenuItem(row.id);
        await loadData(); // Refresh data
      } catch (err) {
        alert("Failed to delete item.");
      }
    }
  };

  const handleModalSubmit = async (formData) => {
    try {
      setIsPosting(true);
      setPostError(null);
      if (editingRow) {
        await updateMenuItem(editingRow.id, formData);
      } else {
        await createMenuItem(formData);
      }
      await loadData();
      return true; // Indicates success
    } catch (err) {
      setPostError("Operation failed. Please check your data and try again.");
      return false; // Indicates failure
    } finally {
      setIsPosting(false);
    }
  };

  return (
    <>
      <MenuJournalTable
        rows={rows}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
        error={error}
      />
      <MenuItemFormModal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleModalSubmit}
        initialData={editingRow}
        isPosting={isPosting}
        postError={postError}
      />
    </>
  );
}