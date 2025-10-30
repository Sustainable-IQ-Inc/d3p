"use client";

import { Fragment, useEffect, useMemo, useState } from "react";

// material-ui
import { alpha, useTheme } from "@mui/material/styles";
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableContainer,
  TableCell,
  TableFooter,
  TableHead,
  TableRow,
  Stack,
  Divider,
  useMediaQuery,
} from "@mui/material";

// third-party
import { DndProvider } from "react-dnd";
import { isMobile } from "react-device-detect";
import { HTML5Backend } from "react-dnd-html5-backend";
import { TouchBackend } from "react-dnd-touch-backend";
import {
  getCoreRowModel,
  getFilteredRowModel,
  getFacetedRowModel,
  getFacetedMinMaxValues,
  getFacetedUniqueValues,
  getPaginationRowModel,
  getSortedRowModel,
  getGroupedRowModel,
  getExpandedRowModel,
  flexRender,
  useReactTable,
  ColumnDef,
  ColumnFiltersState,
  ColumnOrderState,
  HeaderGroup,
  SortingState,
  GroupingState,
  FilterFn,
  SortingFn,
  sortingFns,
} from "@tanstack/react-table";
import {
  compareItems,
  rankItem,
  RankingInfo,
} from "@tanstack/match-sorter-utils";

// project import
import MainCard from "components/MainCard";
import ScrollX from "components/ScrollX";
import {
  DebouncedInput,
  EmptyTable,
  Filter,
  HeaderSort,
  IndeterminateCheckbox,
  RowSelection,
  TablePagination,
  RowEditable,
  DraggableColumnHeader,
  SelectColumnVisibility,
} from "components/third-party/react-table";

import ProjectDetailSection from "./ProjectDetailSection";

// types
import { TableDataProps } from "types/table";
import LabelKeyObject from "react-csv";
import IconButton from "components/@extended/IconButton";
import { DownOutlined, RightOutlined, StopOutlined } from "@ant-design/icons";

export const fuzzyFilter: FilterFn<TableDataProps> = (
  row,
  columnId,
  value,
  addMeta
) => {
  // rank the item
  const itemRank = rankItem(row.getValue(columnId), value);

  // store the ranking info
  addMeta(itemRank);

  // return if the item should be filtered in/out
  return itemRank.passed;
};

export const fuzzySort: SortingFn<TableDataProps> = (rowA, rowB, columnId) => {
  let dir = 0;

  // only sort by rank if the column has ranking information
  if (rowA.columnFiltersMeta[columnId]) {
    dir = compareItems(
      rowA.columnFiltersMeta[columnId]! as RankingInfo,
      rowB.columnFiltersMeta[columnId]! as RankingInfo
    );
  }

  // provide an alphanumeric fallback for when the item ranks are equal
  return dir === 0 ? sortingFns.alphanumeric(rowA, rowB, columnId) : dir;
};

// ==============================|| REACT TABLE - EDIT ACTION ||============================== //

interface ReactTableProps {
  defaultColumns: ColumnDef<TableDataProps>[];
  data: TableDataProps[];
}

// ==============================|| REACT TABLE ||============================== //

function ReactTable({ defaultColumns, data }: ReactTableProps) {
  const theme = useTheme();
  const matchDownSM = useMediaQuery(theme.breakpoints.down("sm"));

  const [rowSelection, setRowSelection] = useState({});
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [grouping, setGrouping] = useState<GroupingState>([]);

  const [columns] = useState(() => [...defaultColumns]);
  
  const [columnOrder, setColumnOrder] = useState<ColumnOrderState>(
    columns.map((column) => column.id as string) // must start out with populated columnOrder so we can splice
  );

  const [columnVisibility, setColumnVisibility] = useState({});

  const table = useReactTable({
    data,
    columns,
    defaultColumn: {
      cell: RowEditable,
    },
    state: {
      rowSelection,
      columnFilters,
      globalFilter,
      sorting,
      grouping,
      columnOrder,
      columnVisibility,
    },
    enableRowSelection: true,
    onRowSelectionChange: setRowSelection,
    onSortingChange: setSorting,
    onGroupingChange: setGrouping,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onColumnOrderChange: setColumnOrder,
    onColumnVisibilityChange: setColumnVisibility,
    getRowCanExpand: () => true,
    getExpandedRowModel: getExpandedRowModel(),
    getGroupedRowModel: getGroupedRowModel(),
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    globalFilterFn: fuzzyFilter,
    getRowId: (row) => (row.id ? row.id.toString() : ""),
    debugTable: true,
    debugHeaders: true,
    debugColumns: true,
  });

  useEffect(() => {
    // Ensure this effect only runs after the component is mounted
    const setInitialColumnVisibility = () => {
      setColumnVisibility({
        id: false,
        role: false,
        contact: false,
        country: false,
        progress: false,
      });
    };

    setInitialColumnVisibility();
  }, []); // Empty dependency array ensures this runs once after mount

  const backColor = alpha(theme.palette.primary.lighter, 0.1);

  let headers: (typeof LabelKeyObject & { label: string })[] = [];
  table.getVisibleLeafColumns().map(
    (columns) =>
      // @ts-ignore
      columns.columnDef.accessorKey &&
      headers.push({
        label:
          typeof columns.columnDef.header === "string"
            ? columns.columnDef.header
            : "#",
        // @ts-ignore
        key: columns.columnDef.accessorKey,
      })
  );

  return (
    <MainCard content={false}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        justifyContent="space-between"
        sx={{
          padding: 2,
          ...(matchDownSM && {
            "& .MuiOutlinedInput-root, & .MuiFormControl-root": {
              width: "100%",
            },
          }),
        }}
      >
        <DebouncedInput
          value={globalFilter ?? ""}
          onFilterChange={(value) => setGlobalFilter(String(value))}
          placeholder={`Search ${data.length} records...`}
        />
        <Stack
          direction="row"
          spacing={2}
          alignItems="center"
          sx={{ width: { xs: "100%", sm: "auto" } }}
        >
          <SelectColumnVisibility
            {...{
              getVisibleLeafColumns: table.getVisibleLeafColumns,
              getIsAllColumnsVisible: table.getIsAllColumnsVisible,
              getToggleAllColumnsVisibilityHandler:
                table.getToggleAllColumnsVisibilityHandler,
              getAllColumns: table.getAllColumns,
            }}
          />
          {/*           <CSVExport
            {...{
              data:
                table.getSelectedRowModel().flatRows.map((row) => row.original)
                  .length === 0
                  ? data
                  : table
                      .getSelectedRowModel()
                      .flatRows.map((row) => row.original),
              headers,
              filename: "umbrella.csv",
            }}
          /> */}
        </Stack>
      </Stack>

      <ScrollX>
        <RowSelection selected={Object.keys(rowSelection).length} />
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              {table.getHeaderGroups().map((headerGroup: HeaderGroup<any>) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    if (
                      header.column.columnDef.meta !== undefined &&
                      header.column.getCanSort()
                    ) {
                      Object.assign(header.column.columnDef.meta, {
                        className:
                          header.column.columnDef.meta.className +
                          " cursor-pointer prevent-select",
                      });
                    }

                    return (
                      <DraggableColumnHeader
                        key={header.id}
                        header={header}
                        table={table}
                      >
                        <>
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
                                <HeaderSort column={header.column} sort />
                              )}
                            </Stack>
                          )}
                        </>
                      </DraggableColumnHeader>
                    );
                  })}
                </TableRow>
              ))}
            </TableHead>
            <TableHead>
              {table.getHeaderGroups().map((headerGroup: HeaderGroup<any>) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableCell
                      key={header.id}
                      {...header.column.columnDef.meta}
                    >
                      {header.column.getCanFilter() && (
                        <Filter column={header.column} table={table} />
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableHead>
            <TableBody>
              {table.getRowModel().rows.length > 0 ? (
                table.getRowModel().rows.map((row) => (
                  <Fragment key={row.id}>
                    <TableRow key={row.id}>
                      <>
                        {row.getVisibleCells().map((cell) => {
                          let bgcolor = "background.paper";
                          if (cell.getIsGrouped()) bgcolor = "primary.lighter";
                          if (cell.getIsAggregated())
                            bgcolor = "warning.lighter";
                          if (cell.getIsPlaceholder())
                            bgcolor = "error.lighter";

                          if (
                            cell.column.columnDef.meta !== undefined &&
                            cell.column.getCanSort()
                          ) {
                            Object.assign(cell.column.columnDef.meta, {
                              style: { backgroundColor: bgcolor },
                            });
                          }

                          return (
                            <TableCell
                              key={cell.id}
                              {...cell.column.columnDef.meta}
                              sx={{ bgcolor }}
                              {...(cell.getIsGrouped() &&
                                cell.column.columnDef.meta === undefined && {
                                  style: { backgroundColor: bgcolor },
                                })}
                            >
                              {cell.getIsGrouped() ? (
                                <Stack
                                  direction="row"
                                  alignItems="center"
                                  spacing={0.5}
                                >
                                  <IconButton
                                    color="secondary"
                                    onClick={row.getToggleExpandedHandler()}
                                    size="small"
                                    sx={{ p: 0, width: 24, height: 24 }}
                                  >
                                    {row.getIsExpanded() ? (
                                      <DownOutlined />
                                    ) : (
                                      <RightOutlined />
                                    )}
                                  </IconButton>
                                  <Box>
                                    {flexRender(
                                      cell.column.columnDef.cell,
                                      cell.getContext()
                                    )}
                                  </Box>{" "}
                                  <Box>({row.subRows.length})</Box>
                                </Stack>
                              ) : cell.getIsAggregated() ? (
                                flexRender(
                                  cell.column.columnDef.aggregatedCell ??
                                    cell.column.columnDef.cell,
                                  cell.getContext()
                                )
                              ) : cell.getIsPlaceholder() ? null : (
                                flexRender(
                                  cell.column.columnDef.cell,
                                  cell.getContext()
                                )
                              )}
                            </TableCell>
                          );
                        })}
                      </>
                    </TableRow>
                    {row.getIsExpanded() && !row.getIsGrouped() && (
                      <TableRow
                        sx={{
                          bgcolor: backColor,
                          "&:hover": { bgcolor: `${backColor} !important` },
                        }}
                      >
                        <TableCell colSpan={row.getVisibleCells().length + 2}>
                          <ProjectDetailSection data={row.original} />
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={table.getAllColumns().length}>
                    <EmptyTable msg="No Data" />
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
            <TableFooter>
              {table.getFooterGroups().map((footerGroup) => (
                <TableRow key={footerGroup.id}>
                  {footerGroup.headers.map((footer) => (
                    <TableCell
                      key={footer.id}
                      {...footer.column.columnDef.meta}
                    >
                      {footer.isPlaceholder
                        ? null
                        : flexRender(
                            footer.column.columnDef.header,
                            footer.getContext()
                          )}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableFooter>
          </Table>
        </TableContainer>
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
      </ScrollX>
    </MainCard>
  );
}

// ==============================|| REACT TABLE - UMBRELLA ||============================== //
interface TableProps<T> {
  options?: any;
  data: any;
  columnsNew: any;
  pagination: string;
  title: string;
  clickToPage?: string;
}
const UmbrellaTable: React.FC<TableProps<any>> = ({
  data,
  columnsNew,
  pagination,
  title,
  clickToPage,
}) => {
  const theme = useTheme();

  const columns = useMemo(() => {
    return [
      {
        id: "expander",
        enableGrouping: false,
        header: () => null,
        cell: ({ row }: { row: any }) => {
          return row.getCanExpand() ? (
            <IconButton
              color={row.getIsExpanded() ? "primary" : "secondary"}
              onClick={row.getToggleExpandedHandler()}
              size="small"
            >
              {row.getIsExpanded() ? <DownOutlined /> : <RightOutlined />}
            </IconButton>
          ) : (
            <StopOutlined style={{ color: theme.palette.text.secondary }} />
          );
        },
      },
      {
        id: "select",
        enableGrouping: false,
        header: ({ table }: { table: any }) => (
          <IndeterminateCheckbox
            {...{
              checked: table.getIsAllRowsSelected(),
              indeterminate: table.getIsSomeRowsSelected(),
              onChange: table.getToggleAllRowsSelectedHandler(),
            }}
          />
        ),
        cell: ({ row }: { row: any }) => (
          <IndeterminateCheckbox
            {...{
              checked: row.getIsSelected(),
              disabled: !row.getCanSelect(),
              indeterminate: row.getIsSomeSelected(),
              onChange: row.getToggleSelectedHandler(),
            }}
          />
        ),
      },

      ...columnsNew, // Add the new columns here
    ];
  }, [columnsNew]);

  return (
    <DndProvider backend={isMobile ? TouchBackend : HTML5Backend}>
      <ReactTable {...{ data, defaultColumns: columns }} />
    </DndProvider>
  );
};

export default UmbrellaTable;
