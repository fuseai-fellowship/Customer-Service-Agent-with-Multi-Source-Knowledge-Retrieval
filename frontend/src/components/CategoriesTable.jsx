// src/components/CategoriesTable.jsx
import React from "react";
import { MaterialReactTable, useMaterialReactTable } from "material-react-table";
import { Box, Button, IconButton, Tooltip } from "@mui/material";
import { Edit, Delete, Add } from "@mui/icons-material";

const COLUMNS = [
  { accessorKey: "id", header: "ID", size: 60 },
  { accessorKey: "name", header: "Name" },
];

export default function CategoriesTable({ rows, onCrud, loading }) {
  const table = useMaterialReactTable({
    columns: COLUMNS,
    data: rows ?? [],
    state: { isLoading: loading },
    enableRowActions: true,
    renderTopToolbarCustomActions: () => (
      <Button variant="contained" startIcon={<Add />} onClick={() => onCrud("create")}>
        New Category
      </Button>
    ),
    renderRowActions: ({ row }) => (
      <Box sx={{ display: "flex", gap: 1 }}>
        <Tooltip title="Edit">
          <IconButton color="primary" onClick={() => onCrud("edit", row.original)}>
            <Edit />
          </IconButton>
        </Tooltip>
        <Tooltip title="Delete">
          <IconButton color="error" onClick={() => onCrud("delete", row.original)}>
            <Delete />
          </IconButton>
        </Tooltip>
      </Box>
    ),
  });

  return <MaterialReactTable table={table} />;
}