import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
} from "@mui/material";

export default function KnowledgeFormModal({
  open,
  onClose,
  onSubmit,
  initialData,
}) {
  const [form, setForm] = useState({ topic: "", content: "" });

  useEffect(() => {
    if (open) {
      setForm({
        topic: initialData?.topic || "",
        content: initialData?.content || "",
      });
    }
  }, [open, initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((p) => ({ ...p, [name]: value }));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {initialData ? "Edit Knowledge" : "New Knowledge"}
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            autoFocus
            name="topic"
            label="Topic (e.g., 'Opening Hours')"
            value={form.topic}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            name="content"
            label="Content / Answer"
            value={form.content}
            onChange={handleChange}
            fullWidth
            required
            multiline
            rows={6}
            helperText="This text will be embedded for semantic search."
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={() => onSubmit(form)}
          variant="contained"
          disabled={!form.content.trim()}
        >
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
