// src/components/MenuItemFormModal.jsx
import React, { useState, useEffect } from "react";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Stack,
  CircularProgress,
  Typography,
  Checkbox,
  FormControlLabel,
} from "@mui/material";

const getInitialFormState = (initialData) => ({
  name: initialData?.name || "",
  description: initialData?.description || "",
  tags: initialData?.tags || "",
  price_npr: initialData?.price_npr || "",
  availability: initialData?.availability ?? true,
});

export default function MenuItemFormModal({
  open,
  onClose,
  onSubmit,
  initialData,
  isPosting,
  postError,
}) {
  const [formData, setFormData] = useState(getInitialFormState(initialData));

  useEffect(() => {
    if (open) {
      setFormData(getInitialFormState(initialData));
    }
  }, [open, initialData]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async () => {
    const dataToSubmit = {
      ...formData,
      price_npr: parseFloat(formData.price_npr) || 0,
    };
    const success = await onSubmit(dataToSubmit);
    if (success) {
      onClose();
    }
  };

  const isEditing = initialData?.id != null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{isEditing ? "Edit Menu Item" : "Add New Item"}</DialogTitle>
      <DialogContent>
        <Stack spacing={2.5} sx={{ width: "100%", marginTop: 1 }}>
          <TextField
            name="name"
            label="Name"
            value={formData.name}
            onChange={handleInputChange}
            fullWidth
            required
            disabled={isPosting}
            autoFocus
          />
          <TextField
            name="description"
            label="Description"
            value={formData.description}
            onChange={handleInputChange}
            fullWidth
            multiline
            rows={3}
            disabled={isPosting}
          />
          <TextField
            name="tags"
            label="Tags (comma-separated)"
            value={formData.tags}
            onChange={handleInputChange}
            fullWidth
            disabled={isPosting}
          />
          <TextField
            name="price_npr"
            label="Price (NPR)"
            value={formData.price_npr}
            onChange={handleInputChange}
            fullWidth
            required
            type="number"
            disabled={isPosting}
          />
          <FormControlLabel
            control={
              <Checkbox
                name="availability"
                checked={formData.availability}
                onChange={handleInputChange}
                disabled={isPosting}
              />
            }
            label="Available"
          />
          {postError && (
            <Typography color="error" variant="body2" sx={{ mt: 1 }}>
              {postError}
            </Typography>
          )}
        </Stack>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={onClose} color="inherit" disabled={isPosting}>
          Cancel
        </Button>
        <Button onClick={handleSubmit} variant="contained" disabled={isPosting}>
          {isPosting ? (
            <CircularProgress size={24} color="inherit" />
          ) : isEditing ? (
            "Save Changes"
          ) : (
            "Add Item"
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
}