// src/pages/Menu.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, Tab, Tabs } from "@mui/material";
import CategoriesTable from "../components/CategoriesTable";
import ItemsTable from "../components/ItemsTable";
import CategoryFormModal from "../components/CategoryFormModal";
import ItemFormModal from "../components/ItemFormModal";
import ManageVariationsModal from "../components/ManageVariationsModal"; // Import the new modal
import { getCategories, createCategory, updateCategory, deleteCategory, getItems, createItem, updateItem, deleteItem } from "../lib/api";

export default function MenuPage() {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);

  // Categories state
  const [categories, setCategories] = useState([]);
  const [isCategoryModalOpen, setCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  // Items state
  const [items, setItems] = useState([]);
  const [isItemModalOpen, setItemModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // Variations state
  const [managingVariationsForItem, setManagingVariationsForItem] = useState(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [catData, itemData] = await Promise.all([getCategories(), getItems()]);
      setCategories(catData);
      setItems(itemData);
    } catch (error) {
      console.error("Failed to load data", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // --- Category CRUD Handling ---
  const handleCategoryCrud = (action, data) => {
    if (action === "create") {
      setEditingCategory(null);
      setCategoryModalOpen(true);
    } else if (action === "edit") {
      setEditingCategory(data);
      setCategoryModalOpen(true);
    } else if (action === "delete") {
      if (window.confirm(`Delete "${data.name}"?`)) {
        deleteCategory(data.id).then(loadData);
      }
    }
  };

  const handleCategorySubmit = (formData) => {
    const promise = editingCategory
      ? updateCategory(editingCategory.id, formData)
      : createCategory(formData);
    promise.then(() => {
      setCategoryModalOpen(false);
      loadData();
    });
  };

  // --- Item CRUD Handling ---
  const handleItemCrud = (action, data) => {
    if (action === "create") {
      setEditingItem(null);
      setItemModalOpen(true);
    } else if (action === "edit") {
      setEditingItem(data);
      setItemModalOpen(true);
    } else if (action === "delete") {
      if (window.confirm(`Delete "${data.name}"?`)) {
        deleteItem(data.id).then(loadData);
      }
    }
  };

  const handleItemSubmit = (formData) => {
    const promise = editingItem
      ? updateItem(editingItem.id, formData)
      : createItem(formData);
    promise.then(() => {
      setItemModalOpen(false);
      loadData();
    });
  };

  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="Menu Items" />
          <Tab label="Categories" />
          <Tab label="Specials" disabled />
        </Tabs>
      </Box>

      {tab === 0 && (
        <ItemsTable
          rows={items}
          categories={categories}
          onCrud={handleItemCrud}
          onManageVariations={setManagingVariationsForItem} // Connect the handler
          loading={loading}
        />
      )}
      {tab === 1 && <CategoriesTable rows={categories} onCrud={handleCategoryCrud} loading={loading} />}

      {/* --- Modals --- */}
      <CategoryFormModal
        open={isCategoryModalOpen}
        onClose={() => setCategoryModalOpen(false)}
        onSubmit={handleCategorySubmit}
        initialData={editingCategory}
      />
      <ItemFormModal
        open={isItemModalOpen}
        onClose={() => setItemModalOpen(false)}
        onSubmit={handleItemSubmit}
        initialData={editingItem}
        categories={categories}
      />
      {managingVariationsForItem && (
        <ManageVariationsModal
          item={managingVariationsForItem}
          onClose={() => setManagingVariationsForItem(null)}
        />
      )}
    </>
  );
}