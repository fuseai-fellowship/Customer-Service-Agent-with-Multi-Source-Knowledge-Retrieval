// src/components/MenuJournalTable.jsx
import React from "react";
import {
  MaterialReactTable,
  useMaterialReactTable,
} from "material-react-table";
import { Box, Button, IconButton, Tooltip } from "@mui/material";
import { Edit, Delete, Add } from "@mui/icons-material";

// ⚠️ column keys EXACTLY match your backend: menu_items
// id, name, description, tags, price_npr, availability
const COLUMNS = [
  {
    accessorKey: "id",
    header: "ID",
    size: 60,
    enableSorting: true,
    enableResizing: true,
  },
  { accessorKey: "name", header: "Name", size: 220 },
  { accessorKey: "description", header: "Description", size: 320 },
  { accessorKey: "tags", header: "Tags", size: 180 },
  {
    accessorKey: "price_npr",
    header: "Price (NPR)",
    size: 130,
    Cell: ({ cell }) =>
      new Intl.NumberFormat(undefined, {
        style: "currency",
        currency: "NPR",
      }).format(Number(cell.getValue() ?? 0)),
  },
  {
    accessorKey: "availability",
    header: "Available",
    size: 110,
    Cell: ({ cell }) => (cell.getValue() ? "Yes" : "No"),
  },
];

export default function MenuJournalTable({
  rows,
  onCreate, // () => void
  onEdit, // (row) => void
  onDelete, // (row) => void
  loading = false,
  error = null,
}) {
  const table = useMaterialReactTable({
    columns: COLUMNS,
    data: rows ?? [],
    state: { isLoading: loading, showAlertBanner: !!error },
    enablePagination: true,
    enableSorting: true,
    enableColumnResizing: true,
    initialState: {
      pagination: { pageSize: 10 },
      density: "comfortable",
    },
    muiToolbarAlertBannerProps: error
      ? { color: "error", children: error }
      : undefined,
    renderTopToolbarCustomActions: () => (
      <Button variant="contained" startIcon={<Add />} onClick={onCreate}>
        New Item
      </Button>
    ),
    renderRowActions: ({ row }) => (
      <Box sx={{ display: "flex", gap: 1 }}>
        <Tooltip title="Edit">
          <IconButton color="primary" onClick={() => onEdit?.(row.original)}>
            <Edit />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton color="error" onClick={() => onDelete?.(row.original)}>
            <Delete />
          </IconButton>
        </Tooltip>
      </Box>
    ),
  });

  return <MaterialReactTable table={table} />;
}
