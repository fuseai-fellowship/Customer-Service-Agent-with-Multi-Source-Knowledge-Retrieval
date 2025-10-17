// src/components/ManageVariationsModal.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, IconButton, Tooltip } from "@mui/material";
import { MaterialReactTable, useMaterialReactTable } from "material-react-table";
import { Edit, Delete, Add } from "@mui/icons-material";
import VariationFormModal from "./VariationFormModal";
import { getVariations, createVariation, updateVariation, deleteVariation } from "../lib/api";

const COLUMNS = [
  { accessorKey: "id", header: "ID", size: 60 },
  { accessorKey: "label", header: "Label" },
  { accessorKey: "final_price", header: "Price (NPR)", size: 120 },
  { accessorKey: "is_available", header: "Available", Cell: ({ cell }) => (cell.getValue() ? "Yes" : "No"), size: 100 },
];

export default function ManageVariationsModal({ item, onClose, startWithCreate = false }) {
  const [variations, setVariations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isFormOpen, setFormOpen] = useState(false);
  const [editingVariation, setEditingVariation] = useState(null);

  const loadVariations = useCallback(async () => {
    if (!item?.id) return;
    setLoading(true);
    try {
      const data = await getVariations(item.id);
      setVariations(data);
    } catch (error) {
      console.error("Failed to load variations", error);
    } finally {
      setLoading(false);
    }
  }, [item]);

  useEffect(() => {
    loadVariations();
  }, [loadVariations]);

  // **KEY CHANGE**: This effect runs when the modal opens.
  // If the 'startWithCreate' flag is true, it immediately opens the 'New Variation' form.
  useEffect(() => {
    if (startWithCreate) {
      handleCrud('create');
    }
  }, [startWithCreate]);

  const handleCrud = (action, data) => {
    if (action === "create") {
      setEditingVariation(null);
      setFormOpen(true);
    } else if (action === "edit") {
      setEditingVariation(data);
      setFormOpen(true);
    } else if (action === "delete") {
      if (window.confirm(`Delete variation "${data.label}"?`)) {
        deleteVariation(data.id).then(loadVariations);
      }
    }
  };

  const handleFormSubmit = (formData) => {
    const payload = { ...formData, item_id: item.id };
    const promise = editingVariation
      ? updateVariation(editingVariation.id, payload)
      : createVariation(payload);
    promise.then(() => {
      setFormOpen(false);
      loadVariations();
    });
  };

  const table = useMaterialReactTable({
    columns: COLUMNS,
    data: variations,
    state: { isLoading: loading },
    enableRowActions: true,
    renderTopToolbarCustomActions: () => (
      <Button variant="contained" startIcon={<Add />} onClick={() => handleCrud("create")}>
        New Variation
      </Button>
    ),
    renderRowActions: ({ row }) => (
      <Box sx={{ display: "flex", gap: 1 }}>
        <Tooltip title="Edit">
          <IconButton color="primary" onClick={() => handleCrud("edit", row.original)}>
            <Edit />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton color="error" onClick={() => handleCrud("delete", row.original)}>
            <Delete />
          </IconButton>
        </Tooltip>
      </Box>
    ),
  });

  if (!item) return null;

  return (
    <>
      <Dialog open={true} onClose={onClose} maxWidth="md" fullWidth>
        <DialogTitle>Manage Variations for "{item.name}"</DialogTitle>
        <DialogContent>
          <MaterialReactTable table={table} />
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>

      <VariationFormModal
        open={isFormOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        initialData={editingVariation}
      />
    </>
  );
}