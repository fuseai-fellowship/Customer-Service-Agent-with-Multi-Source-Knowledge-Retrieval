// src/components/CategoryFormModal.jsx
import React, { useState, useEffect } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Stack } from "@mui/material";

export default function CategoryFormModal({ open, onClose, onSubmit, initialData }) {
  const [name, setName] = useState("");

  useEffect(() => {
    if (open) setName(initialData?.name || "");
  }, [open, initialData]);

  const handleSubmit = () => onSubmit({ name });

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{initialData ? "Edit Category" : "New Category"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            autoFocus
            label="Category Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            fullWidth
            required
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" disabled={!name.trim()}>Save</Button>
      </DialogActions>
    </Dialog>
  );
}