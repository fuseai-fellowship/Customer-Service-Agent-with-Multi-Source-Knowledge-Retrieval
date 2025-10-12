// src/components/VariationFormModal.jsx
import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Stack, Checkbox, FormControlLabel } from "@mui/material";

const getInitialState = (data) => ({
  label: data?.label || "",
  final_price: data?.final_price || "",
  is_available: data?.is_available ?? true,
});

export default function VariationFormModal({ open, onClose, onSubmit, initialData }) {
  const [form, setForm] = useState(getInitialState(initialData));

  useEffect(() => {
    if (open) setForm(getInitialState(initialData));
  }, [open, initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(p => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSubmit = () => {
    onSubmit({ ...form, final_price: parseFloat(form.final_price) });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{initialData ? "Edit Variation" : "New Variation"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField autoFocus name="label" label="Label (e.g., Steam, Fried, Large)" value={form.label} onChange={handleChange} required />
          <TextField name="final_price" label="Final Price (NPR)" value={form.final_price} onChange={handleChange} type="number" required />
          <FormControlLabel
            control={<Checkbox name="is_available" checked={form.is_available} onChange={handleChange} />}
            label="Is Available"
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained">Save</Button>
      </DialogActions>
    </Dialog>
  );
}