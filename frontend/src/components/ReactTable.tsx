"use client";

// material-ui
import {
  Table,
  TableBody,
  TableContainer,
  TableCell,
  TableHead,
  TableRow,
  Stack,
  Box,
  Divider,
  TextField,
  InputAdornment,
  Typography,
  Chip,
  Tooltip,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import { useDataReload } from "contexts/ProjectDataReload";

import SaveIcon from "@mui/icons-material/Save";
import submitEEUUpdate from "app/api/UpdateEnergyFields";
import "./App.css";
// third-party
import {
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
  HeaderGroup,
  flexRender,
  SortingState,
  getSortedRowModel,
} from "@tanstack/react-table";

// react
import { useState, useEffect, useRef } from "react";
// project-import
import ScrollX from "components/ScrollX";
import MainCard from "components/MainCard";
import {
  TablePagination,
  HeaderSort,
} from "components/third-party/react-table";
import { useRouter } from "next/navigation";

// types
import LabelKeyObject from "react-csv";

// ==============================|| REACT TABLE ||============================== //
interface TableProps {
  id: string;
  data: any;
  columns: any;
  pagination: string;
  title: string;
  clickToPage?: string;
  rowsPerPage?: number;
  showColGroups?: boolean;
  fuelTypes?: string[];
  showRowcount?: boolean;
  allowCellEdit?: boolean; // New prop to allow cell editing
  editDetails?: any;
  page_identifier?: any;
  showUnitsDropdown?: boolean;
  selectedUnits?: string;
  onUnitsChange?: (units: string) => void;
  isUnitsLoading?: boolean;
  availableUnits?: string[]; // New prop to control which units are available
}

const ReactTable: React.FC<TableProps> = ({
  id,
  data,
  columns,
  pagination,
  title,
  clickToPage,
  rowsPerPage = 10,
  showColGroups = false,
  fuelTypes,
  showRowcount = true,
  allowCellEdit = false, // Default to false
  editDetails, // Ensure editDetails is passed
  page_identifier,
  showUnitsDropdown = false,
  selectedUnits = 'kbtu',
  onUnitsChange,
  isUnitsLoading = false,
  availableUnits = ['gj', 'kbtu', 'kbtu/sf', 'mbtu'], // Default to all units
}) => {
  // Get the first column's accessor key for sorting
  const firstColumnId = columns && columns.length > 0 ? columns[0].accessorKey || columns[0].id : '';
  
  const [sorting, setSorting] = useState<SortingState>([
    {
      id: firstColumnId,
      desc: false, // ascending order
    },
  ]);
  const router = useRouter();

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    ...(pagination !== "none"
      ? { getPaginationRowModel: getPaginationRowModel() }
      : {}),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
  });
  const { reloadData } = useDataReload();
  useEffect(() => {
    table.setPageSize(rowsPerPage);
  }, [rowsPerPage, table]);

  

  let headers: (typeof LabelKeyObject & { label: string })[] = [];
  table.getAllColumns().map((columns) =>
    headers.push({
      label:
        typeof columns.columnDef.header === "string"
          ? columns.columnDef.header
          : "#",
      // @ts-ignore
      key: columns.columnDef.accessorKey,
    })
  );

  const [editingCell, setEditingCell] = useState<{ rowId: string; cellId: string } | null>(null);
  const [cellValues, setCellValues] = useState<{ [key: string]: any }>({});
  const inputRef = useRef<HTMLDivElement>(null); // Change the type to HTMLDivElement
  

  const handleEditClick = (rowId: string, cellId: string, initialValue: any) => {
    setEditingCell({ rowId, cellId });
    setCellValues((prev) => ({ ...prev, [`${rowId}-${cellId}`]: initialValue }));
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>, rowId: string, cellId: string) => {
    setCellValues((prev) => ({ ...prev, [`${rowId}-${cellId}`]: e.target.value }));
  };

  const handleSaveClick = async (rowId: string, cellId: string,cell_key: string) => {
    console.log("Save clicked for cell:", cell_key, "with value:", cellValues[`${rowId}-${cellId}`]);
    try {
      const result = await submitEEUUpdate({
        updateProps: {
          project_id: page_identifier,
          new_value: cellValues[`${rowId}-${cellId}`],
          cell_key: cell_key,
          current_units: selectedUnits
        }
      });

      console.log("Update result:", result);

      if (result === "success") {
        console.log("Triggering reload in 500ms...");
        // Add a small delay to ensure backend calculations are complete
        setTimeout(() => {
          console.log("Calling reloadData now");
          reloadData();
        }, 500);
      } else {
        console.error("Update failed:", result);
      }
    } catch (error) {
      console.error("Error submitting update:", error);
    }
    setEditingCell(null);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setEditingCell(null); // Exit edit mode
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Define a type for cellData
  interface CellData {
    editable: boolean;
    value: any;
    edited: boolean;
    // Add other properties if needed
  }

  const getUnitDisplayName = (unit: string) => {
    switch (unit) {
      case 'gj': return 'GJ';
      case 'kbtu': return 'kBtu';
      case 'kbtu/sf': return 'kBtu/SF';
      case 'mbtu': return 'MBtu';
      default: return unit;
    }
  };

  const titleContent = showUnitsDropdown ? (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      width: '100%'
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <Typography variant="body2" sx={{ 
          color: 'text.secondary',
          fontSize: '0.875rem'
        }}>
          {showRowcount ? `(${data ? data.length : 0} rows)` : ""}
        </Typography>
      </Box>
      
      {/* Chip-Based Units Selector */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Typography variant="body2" sx={{ color: 'text.secondary', fontWeight: 500 }}>
          Units:
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          {availableUnits.map((unit) => (
            <Chip
              key={unit}
              label={getUnitDisplayName(unit)}
              onClick={() => !isUnitsLoading && onUnitsChange?.(unit)}
              variant={selectedUnits === unit ? 'filled' : 'outlined'}
              color={selectedUnits === unit ? 'primary' : 'default'}
              size="small"
              disabled={isUnitsLoading}
              sx={{
                fontSize: '0.75rem',
                height: 28,
                fontWeight: selectedUnits === unit ? 600 : 400,
                borderWidth: selectedUnits === unit ? 2 : 1,
                transition: 'all 0.2s ease-in-out',
                opacity: isUnitsLoading ? 0.6 : 1,
                cursor: isUnitsLoading ? 'not-allowed' : 'pointer',
                '&:hover': {
                  backgroundColor: !isUnitsLoading && selectedUnits === unit ? 'primary.dark' : 'action.hover',
                  transform: !isUnitsLoading ? 'translateY(-1px)' : 'none',
                  boxShadow: !isUnitsLoading ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                },
                '&:active': {
                  transform: !isUnitsLoading ? 'translateY(0px)' : 'none',
                }
              }}
            />
          ))}
        </Box>
      </Box>
    </Box>
  ) : `${title}${showRowcount ? ` (${data ? data.length : 0})` : ""}`;

  return (
    <div id={id}>
      <MainCard
        title={titleContent}
        content={false}
      >
        <ScrollX>
          <Stack>
            {pagination === "top" && (
              <Box sx={{ p: 2 }}>
                <TablePagination
                  {...{
                    setPageSize: table.setPageSize,
                    setPageIndex: table.setPageIndex,
                    getState: table.getState,
                    getPageCount: table.getPageCount,
                  }}
                />
              </Box>
            )}

            <TableContainer>
              <Table>
                <TableHead>
                  {showColGroups ? (
                    <TableRow>
                      <TableCell></TableCell>
                      {fuelTypes?.map((fuelType) => (
                        <TableCell align="center" colSpan={2}>
                          {fuelType.replace(/_/g, " ")}
                        </TableCell>
                      ))}
                    </TableRow>
                  ) : null}
                  {table
                    .getHeaderGroups()
                    .map((headerGroup: HeaderGroup<any>) => (
                      <TableRow key={`${headerGroup.id}`}>
                        {headerGroup.headers.map((header, index) => (
                          <TableCell
                            key={header.id}
                            {...header.column.columnDef.meta}
                            onClick={header.column.getToggleSortingHandler()}
                            style={{
                              ...(index === 0 ? { width: "300px" } : {}),
                              textAlign: "center",
                              width: `${100 / headerGroup.headers.length}%`, // divide the width evenly
                            }}
                          >
                            {header.isPlaceholder ? null : (
                              <Stack
                                direction="row"
                                spacing={1}
                                alignItems="center"
                              >
                                <Box>
                                  {flexRender(
                                    header.column.columnDef.header,
                                    header.getContext()
                                  )}
                                </Box>
                                {header.column.getCanSort() && (
                                  <HeaderSort column={header.column} />
                                )}
                              </Stack>
                            )}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                </TableHead>

                <TableBody>
                  {table &&
                  typeof table.getRowModel === "function" &&
                  table.getRowModel() &&
                  table.getRowModel().rows
                    ? table.getRowModel().rows.map((row, index) => (
                        <TableRow
                          key={row.id}
                          onClick={
                            clickToPage
                              ? () => {
                                  console.log("=== TABLE ROW CLICK DEBUG ===");
                                  console.log("Row index:", index);
                                  console.log("Row.id:", row.id);
                                  console.log("Row.original:", row.original);
                                  console.log("data[index]:", data[index]);
                                  const rowData = row.original as any;
                                  console.log("Using ID:", rowData.id);
                                  router.push(
                                    `/${clickToPage}/${rowData.id}`
                                  );
                                }
                              : undefined
                          }
                        >
                          {row.getVisibleCells().map((cell) => {
                            const cellData = cell.getValue() as CellData;
                            const isBaseEditable = editDetails && cellData !== null && cellData?.editable as boolean;
                            const isEditingDisabled = selectedUnits === 'kbtu/sf';
                            const isEditable = isBaseEditable && !isEditingDisabled;
                            let displayValue = cellData?.value;

                            // Check if cellData is null or displayValue is undefined or NaN
                            if (cellData === null || displayValue === undefined || isNaN(Number(displayValue))) {
                              displayValue = 0;
                            }
                            if (typeof cellData === 'string') {
                              displayValue = cellData;
                            }
                            
                            if (typeof displayValue === 'number') {
                                displayValue = new Intl.NumberFormat('en-US', {
                                    minimumFractionDigits: 2,
                                    maximumFractionDigits: 2
                                }).format(displayValue);
                            } 

                            // Custom label for the first column's Total row
                            const isUseTypeColumn = (cell.column.columnDef as any)?.accessorKey === 'use_type' || cell.column.id === 'use_type';
                            if (isUseTypeColumn) {
                              const rawUseType = data[index]?.use_type;
                              const rawStr = typeof rawUseType === 'string' ? rawUseType : (typeof displayValue === 'string' ? displayValue : '');
                              const trimmed = rawStr.trim().toLowerCase();
                              if (trimmed === 'total' || trimmed.startsWith('total')) {
                                const unitsLower = (selectedUnits || '').toLowerCase();
                                const isEUI = unitsLower === 'kbtu/sf';
                                displayValue = isEUI ? 'Total: EUI' : 'Total: Gross Energy';
                              }
                            }

                            // Add safe handling for use_type
                            const use_type = data[index]?.use_type 
                              ? data[index].use_type.replace(/ /g, '_')
                              : '';
                            const cell_id = allowCellEdit ? `${cell.id}-${use_type}` : cell.id;

                            return (
                              <TableCell
                                key={allowCellEdit ? `${cell.id}-${use_type}` : cell.id}
                                {...cell.column.columnDef.meta}
                                style={{ position: 'relative' }}
                                className={isBaseEditable ? "editable-cell" : ""}
                              >
                                {editingCell?.rowId === row.id && editingCell?.cellId === cell.id ? (
                                  <>
                                    <TextField
                                      type="text"
                                      //value={displayValue}
                                      value={cellValues[`${row.id}-${cell.id}`]}
                                      onChange={(e) => handleInputChange(e, row.id, cell.id)}
                                      data-rowid={row.id}
                                      data-cellid={cell.id}
                                      InputProps={{
                                        endAdornment: (
                                          <InputAdornment position="end">
                                            <SaveIcon
                                              onClick={() => handleSaveClick(row.id,cell.id, cell_id)}
                                              sx={{
                                                cursor: 'pointer',
                                              }}
                                              className="save-icon"
                                              data-rowid={row.id}
                                              data-cellid={cell.id}
                                            />
                                          </InputAdornment>
                                        ),
                                      }}
                                      ref={inputRef}
                                      onFocus={() => setEditingCell({ rowId: row.id, cellId: cell.id })}
                                    />
                                  </>
                                ) : (
                                  <>
                                    {editDetails ? (
                                      displayValue
                                    ) : (
                                      flexRender(
                                        cell.column.columnDef.cell,
                                        cell.getContext()
                                      )
                                    )}
                                    {isEditable && (
                                      <EditIcon
                                        onClick={() => handleEditClick(row.id, cell.id, cellData.value)}
                                        sx={{
                                          position: 'absolute',
                                          right: 8,
                                          top: '50%',
                                          transform: 'translateY(-50%)',
                                          cursor: 'pointer',
                                        }}
                                        className="edit-icon"
                                      />
                                    )}
                                    {(isBaseEditable && isEditingDisabled) && (
                                      <Tooltip
                                        title="Change to other unit type to edit value"
                                        arrow
                                        placement="top"
                                      >
                                        <EditIcon
                                          sx={{
                                            position: 'absolute',
                                            right: 8,
                                            top: '50%',
                                            transform: 'translateY(-50%)',
                                            cursor: 'not-allowed',
                                            color: 'action.disabled',
                                            opacity: 0.5,
                                            display: 'none',
                                            '.editable-cell:hover &': {
                                              display: 'block',
                                            },
                                          }}
                                          className="edit-icon-disabled"
                                        />
                                      </Tooltip>
                                    )}
                                  </>
                                )}
                              </TableCell>
                            );
                          })}
                        </TableRow>
                      ))
                    : null}
                </TableBody>
              </Table>
            </TableContainer>

            {pagination === "bottom" && (
              <>
                <Divider />
                <Box sx={{ p: 2 }}>
                  <TablePagination
                    {...{
                      setPageSize: table.setPageSize,
                      setPageIndex: table.setPageIndex,
                      getState: table.getState,
                      getPageCount: table.getPageCount,
                    }}
                  />
                </Box>
              </>
            )}
          </Stack>
        </ScrollX>
      </MainCard>
    </div>
  );
};

export default ReactTable;
