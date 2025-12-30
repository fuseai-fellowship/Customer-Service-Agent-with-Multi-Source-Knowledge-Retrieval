import React, { useState, useEffect, useCallback } from "react";
import { Box, Tab, Tabs } from "@mui/material";
import CategoriesTable from "../components/CategoriesTable";
import ItemsTable from "../components/ItemsTable";
import CategoryFormModal from "../components/CategoryFormModal";
import ItemFormModal from "../components/ItemFormModal";
import ManageVariationsModal from "../components/ManageVariationsModal";
import DescriptionViewModal from "../components/DescriptionViewModal";
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  getItems,
  createItem,
  updateItem,
  deleteItem,
} from "../lib/api";

export default function MenuPage() {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);

  // State for all modals
  const [categories, setCategories] = useState([]);
  const [isCategoryModalOpen, setCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);

  const [items, setItems] = useState([]);
  const [isItemModalOpen, setItemModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  // This state now controls the variations modal and the auto-create flag
  const [variationsModalState, setVariationsModalState] = useState({
    open: false,
    item: null,
    autoCreate: false,
  });

  const [isDescriptionModalOpen, setDescriptionModalOpen] = useState(false);
  const [viewingDescription, setViewingDescription] = useState({
    title: "",
    content: "",
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [catData, itemData] = await Promise.all([
        getCategories(),
        getItems(),
      ]);
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

  // --- Handlers ---
  const handleCategoryCrud = (action, data) => {
    if (action === "create") setEditingCategory(null);
    else setEditingCategory(data);
    setCategoryModalOpen(true);
  };

  const handleItemCrud = (action, data) => {
    if (action === "create") setEditingItem(null);
    else setEditingItem(data);
    setItemModalOpen(true);
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

  const handleItemSubmit = async (formData) => {
    if (editingItem) {
      await updateItem(editingItem.id, formData);
      setItemModalOpen(false);
    } else {
      const newItem = await createItem(formData);
      setItemModalOpen(false);
      // **KEY CHANGE**: Open variations modal with auto-create flag set to true
      setVariationsModalState({ open: true, item: newItem, autoCreate: true });
    }
    loadData();
  };

  const handleViewDescription = (title, content) => {
    setViewingDescription({ title: `Description for ${title}`, content });
    setDescriptionModalOpen(true);
  };

  return (
    <>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="Menu Items" />
          <Tab label="Categories" />
          {/* <Tab label="Specials" disabled /> */}
        </Tabs>
      </Box>

      {tab === 0 && (
        <ItemsTable
          rows={items}
          categories={categories}
          onCrud={handleItemCrud}
          onManageVariations={(item) =>
            setVariationsModalState({
              open: true,
              item: item,
              autoCreate: false,
            })
          }
          onViewDescription={handleViewDescription}
          loading={loading}
        />
      )}
      {tab === 1 && (
        <CategoriesTable
          rows={categories}
          onCrud={handleCategoryCrud}
          loading={loading}
        />
      )}

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
      {variationsModalState.open && (
        <ManageVariationsModal
          item={variationsModalState.item}
          startWithCreate={variationsModalState.autoCreate}
          onClose={() => {
            setVariationsModalState({
              open: false,
              item: null,
              autoCreate: false,
            });
            loadData();
          }}
        />
      )}
      <DescriptionViewModal
        open={isDescriptionModalOpen}
        onClose={() => setDescriptionModalOpen(false)}
        title={viewingDescription.title}
        description={viewingDescription.content}
      />
    </>
  );
}
