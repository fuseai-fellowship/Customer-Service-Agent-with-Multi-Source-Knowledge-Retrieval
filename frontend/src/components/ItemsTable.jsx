// src/components/ItemsTable.jsx
import React from "react";
import { MaterialReactTable, useMaterialReactTable } from "material-react-table";
import { Box, Button, IconButton, Tooltip, Link as MuiLink } from "@mui/material";
import { Edit, Delete, Add, Visibility } from "@mui/icons-material";

export default function ItemsTable({ rows, categories = [], onCrud, onManageVariations, onViewDescription, loading }) {
  const categoryMap = React.useMemo(() => new Map(categories.map(c => [c.id, c.name])), [categories]);

  const COLUMNS = [
    { accessorKey: "id", header: "ID", size: 50 },
    { accessorKey: "name", header: "Name", size: 200 },
    {
      accessorKey: "description",
      header: "Description",
      size: 120,
      Cell: ({ row }) => {
        const { description, name } = row.original;
        if (!description) return "—"; // Show dash if no description
        return (
          <MuiLink
            component="button"
            variant="body2"
            onClick={() => onViewDescription(name, description)}
          >
            View Details
          </MuiLink>
        );
      },
    },
    { accessorFn: (row) => categoryMap.get(row.category_id) || "N/A", header: "Category", size: 150 },
    { accessorKey: "subcategory", header: "Subcategory", size: 150 },
    { accessorKey: "is_available", header: "Available", Cell: ({ cell }) => (cell.getValue() ? "Yes" : "No"), size: 100 },
  ];

  const table = useMaterialReactTable({
    columns: COLUMNS,
    data: rows ?? [],
    state: { isLoading: loading },
    enableRowActions: true,
    renderTopToolbarCustomActions: () => (
      <Button variant="contained" startIcon={<Add />} onClick={() => onCrud("create")}>
        New Item
      </Button>
    ),
    renderRowActions: ({ row }) => (
      <Box sx={{ display: "flex", gap: 1 }}>
        <Tooltip title="Manage Variations">
          <IconButton color="default" onClick={() => onManageVariations(row.original)}>
            <Visibility />
          </IconButton>
        </Tooltip>
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