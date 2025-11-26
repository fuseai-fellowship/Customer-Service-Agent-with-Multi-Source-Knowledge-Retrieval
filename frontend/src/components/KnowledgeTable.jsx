import React from "react";
import { MaterialReactTable, useMaterialReactTable } from "material-react-table";
import { Box, Button, IconButton, Tooltip } from "@mui/material";
import { Edit, Delete, Add } from "@mui/icons-material";

const COLUMNS = [
  { accessorKey: "id", header: "ID", size: 60 },
  { accessorKey: "topic", header: "Topic", size: 200 },
  { 
    accessorKey: "content", 
    header: "Content", 
    size: 500,
    Cell: ({ cell }) => (
      <span title={cell.getValue()} className="line-clamp-2">
        {cell.getValue()}
      </span>
    )
  },
];

export default function KnowledgeTable({ rows, onCrud, loading }) {
  const table = useMaterialReactTable({
    columns: COLUMNS,
    data: rows ?? [],
    state: { isLoading: loading },
    enableRowActions: true,
    renderTopToolbarCustomActions: () => (
      <Button variant="contained" startIcon={<Add />} onClick={() => onCrud("create")}>
        New Topic
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