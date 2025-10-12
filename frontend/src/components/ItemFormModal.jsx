// src/components/ItemFormModal.jsx
import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Stack, Checkbox, FormControlLabel, Select, MenuItem, InputLabel, FormControl } from "@mui/material";

const getInitialState = (data, categories) => ({
  name: data?.name || "",
  description: data?.description || "",
  subcategory: data?.subcategory || "",
  category_id: data?.category_id || categories[0]?.id || "",
  is_available: data?.is_available ?? true,
});

export default function ItemFormModal({ open, onClose, onSubmit, initialData, categories = [] }) {
  const [form, setForm] = useState(getInitialState(initialData, categories));

  useEffect(() => {
    if (open) setForm(getInitialState(initialData, categories));
  }, [open, initialData, categories]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(p => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{initialData ? "Edit Item" : "New Item"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField autoFocus name="name" label="Item Name" value={form.name} onChange={handleChange} required />
          <FormControl>
            <InputLabel>Category</InputLabel>
            <Select name="category_id" label="Category" value={form.category_id} onChange={handleChange}>
              {categories.map(c => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
            </Select>
          </FormControl>
          <TextField name="subcategory" label="Subcategory (e.g., Non-Veg)" value={form.subcategory} onChange={handleChange} />
          <TextField name="description" label="Description" value={form.description} onChange={handleChange} multiline rows={3} />
          <FormControlLabel
            control={<Checkbox name="is_available" checked={form.is_available} onChange={handleChange} />}
            label="Is Available"
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={() => onSubmit(form)} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );
}