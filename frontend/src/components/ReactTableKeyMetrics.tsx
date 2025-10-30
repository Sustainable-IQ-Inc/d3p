'use client';


// material-ui
import { Table, TableBody, TableContainer, TableCell, TableHead, TableRow, Stack, Box, Divider } from '@mui/material';

// third-party
import { useReactTable, getCoreRowModel, getPaginationRowModel, HeaderGroup, flexRender } from '@tanstack/react-table';

// project-import
import ScrollX from 'components/ScrollX';
import MainCard from 'components/MainCard'
import {  TablePagination } from 'components/third-party/react-table';


// types
import LabelKeyObject from 'react-csv';

// ==============================|| REACT TABLE ||============================== //
interface TableProps {
    data: any
    columns: any
    top?: boolean;
  };
  
const ReactTable: React.FC<TableProps> = ({ data, columns, top }) => {
        const table = useReactTable({
            data,
            columns,
            getCoreRowModel: getCoreRowModel(),
            getPaginationRowModel: getPaginationRowModel(),
            debugTable: true
        });

        let headers: (typeof LabelKeyObject & { label: string })[] = [];
        table.getAllColumns().map((columns) =>
          headers.push({
          label: typeof columns.columnDef.header === 'string' ? columns.columnDef.header : '#',
          // @ts-ignore
          key: columns.columnDef.accessorKey
          })
        );

        return (
            <MainCard
            title={'Key Metrics'}
            content={false}
            //secondary={<CSVExport {...{ data, headers, filename: top ? 'pagination-top.csv' : 'pagination-bottom.csv' }} />}
            >
            <ScrollX>
                <Stack>
                {top && (
                    <Box sx={{ p: 2 }}>
                    <TablePagination
                        {...{
                        setPageSize: table.setPageSize,
                        setPageIndex: table.setPageIndex,
                        getState: table.getState,
                        getPageCount: table.getPageCount
                        }}
                    />
                    </Box>
                )}

                <TableContainer>
                    <Table>
                    <TableHead>
                        {table.getHeaderGroups().map((headerGroup: HeaderGroup<any>) => (
                        <TableRow key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                            <TableCell key={header.id} {...header.column.columnDef.meta}>
                                {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                            </TableCell>
                            ))}
                        </TableRow>
                        ))}
                    </TableHead>
                    <TableBody>
                        {table.getRowModel().rows.map((row) => (
                        <TableRow key={row.id}>
                            {row.getVisibleCells().map((cell) => (
                            <TableCell key={cell.id} {...cell.column.columnDef.meta}>
                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </TableCell>
                            ))}
                        </TableRow>
                        ))}
                    </TableBody>
                    </Table>
                </TableContainer>

                {!top && (
                    <>
                    <Divider />
                    <Box sx={{ p: 2 }}>
                        <TablePagination
                        {...{
                            setPageSize: table.setPageSize,
                            setPageIndex: table.setPageIndex,
                            getState: table.getState,
                            getPageCount: table.getPageCount
                        }}
                        />
                    </Box>
                    </>
                )}
                </Stack>
            </ScrollX>
            </MainCard>
        );
        }

export default ReactTable;
/* 
// ==============================|| REACT TABLE - PAGINATION ||============================== //

const PaginationTable = () => {
  const data: TableDataProps[] = makeData(100);

  const columns = useMemo<ColumnDef<TableDataProps>[]>(
    () => [
      {
        header: 'Project Name',
        accessorKey: 'projectName'
      },
      {
        header: 'Company',
        accessorKey: 'companyName'
      },
      {
        header: 'Report Type',
        accessorKey: 'reportType',

      },
      {
        header: 'Average EEU',
        accessorKey: 'avgEEU',

      },
   
    ],
    []
  );

  return (
    <Grid container spacing={3}>

      <Grid item xs={12}>
        <ReactTable {...{ data, columns }} />
      </Grid>
    </Grid>
  );
};

export default PaginationTable; */
