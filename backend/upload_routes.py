from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import models
from utils import verify_token, add_event_history, supabase
from typing import Optional, Dict, Union
from uuid import uuid4
from gcs_upload import upload_blob
import os
from multi_upload import process_multi_upload
import logging_start
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
import tempfile

from post_processing import run_script_master


router = APIRouter()

def update_eeu_record(eeu_id, upload_id):
            eeu_data_dict  = dict()
            eeu_data_dict['id'] = eeu_id
            eeu_data_dict['upload_id'] = upload_id

            try:
                data, count = supabase.table('eeu_data')\
                    .update(eeu_data_dict)\
                    .eq('id', eeu_id)\
                    .execute()
            except Exception as e:
                print(e)
                return "error eeu table"
            return "success"

def upload_report(url, baseline_design, report_type=None, conditioned_area=None, file_extension=None, file_name=None):
    print(f"DEBUG: upload_report called with url={url}, baseline_design={baseline_design}, report_type={report_type}, file_extension={file_extension}")
    
    # Check if this is a multi-project Excel file BEFORE running script master
    if file_extension and file_extension.lower() in ['.xlsx', '.xls']:
        try:
            from parse_reports.parse_multi_project_xlsx import is_multi_project_excel
            if is_multi_project_excel(url):
                logging_start.logger.info(f"Multi-project Excel file detected, skipping report type detection")
                # Return special indicator for multi-project files
                return {
                    'status': 'success',
                    'report_type': 9,
                    'is_multi_project': True,
                    'file_url': url,
                    'message': "Multi-project Excel file detected - use multi-project service"
                }
        except Exception as e:
            logging_start.logger.info(f"Multi-project detection failed: {str(e)}, proceeding with normal parsing")
    
    args = {
        'url': url,
        'conditioned_area': conditioned_area,
        'baseline_design': baseline_design
    }
    if report_type is not None:
        args['report_type'] = report_type

    print(f"DEBUG: Calling run_script_master with args: {args}")
    results = run_script_master(**args)
    print(f"DEBUG: run_script_master returned: {type(results)} - {results}")
    
    # Check if this is a multi-project Excel file (report type 9)
    if (isinstance(results, dict) and 
        results.get('status') == 'success' and 
        results.get('report_type') == 9):
        # Return special indicator for multi-project files
        return {
            'status': 'success',
            'report_type': 9,
            'projects': results.get('projects', []),
            'validation_errors': results.get('validation_errors', []),
            'message': f"Multi-project Excel file detected with {len(results.get('projects', []))} projects"
        }
    
    # Handle both dictionary and list return formats from run_script_master
    if isinstance(results, list):
        print(f"DEBUG: Results is a list: {results}")
        # Legacy format: ["status", errors, warnings] or ["ERROR", errors, warnings]
        status = results[0]
        errors = results[1] if len(results) > 1 else []
        warnings = results[2] if len(results) > 2 else []
        
        if status in ["pending", "ERROR"]:
            print(f"ERROR: Processing failed with status: {status}, errors: {errors}")
            errors_flat = [item for sublist in errors for item in sublist] if errors and len(errors) > 0 and isinstance(errors[0], list) else errors
            warnings_flat = [item for sublist in warnings for item in sublist] if warnings and len(warnings) > 0 and isinstance(warnings[0], list) else warnings
            return {
                'status': 'error',
                'errors': '\n'.join(errors_flat) if errors_flat else '',
                'warnings': '\n'.join(warnings_flat) if warnings_flat else '',
                'message': f'File processing failed with status: {status}'
            }
    else:
        print(f"DEBUG: Results is a dict: {results}")
        # Dictionary format: {"status": "success", "df": df, "errors": [], "warnings": [], "report_type": int}
        if results.get('status') != 'success':
            print(f"ERROR: Results status is not success: {results.get('status')}")
            return {
                'status': 'error',
                'message': 'File processing failed',
                'errors': str(results.get('errors', [])),
                'warnings': str(results.get('warnings', []))
            }
        
        warnings = results['warnings']
        errors = results['errors']
    
    # Ensure we have a dataframe to work with
    if isinstance(results, list) or 'df' not in results:
        print(f"ERROR: No valid dataframe found in results: {results}")
        return {
            'status': 'error',
            'message': 'No valid data found in file',
            'errors': str(errors) if 'errors' in locals() else '',
            'warnings': str(warnings) if 'warnings' in locals() else ''
        }
    
    warnings_flat = [item for sublist in warnings for item in sublist] if warnings and len(warnings) > 0 and isinstance(warnings[0], list) else warnings
    warnings_str = '\n'.join(warnings_flat) if warnings_flat else ''

    errors_flat = [item for sublist in errors for item in sublist] if errors and len(errors) > 0 and isinstance(errors[0], list) else errors
    errors_str = '\n'.join(errors_flat) if errors_flat else ''
    
    print(f"DEBUG: Converting DataFrame to dict. DataFrame shape: {results['df'].shape}")
    print(f"DEBUG: DataFrame columns: {list(results['df'].columns)}")
    print(f"DEBUG: DataFrame dtypes: {results['df'].dtypes}")
    
    # Clean the DataFrame before converting to dict
    df_clean = results['df'].copy()
    
    # Remove invalid column names (like numeric column names)
    invalid_columns = [col for col in df_clean.columns if isinstance(col, (int, float)) or str(col).replace('.', '').isdigit()]
    if invalid_columns:
        print(f"DEBUG: Removing invalid columns: {invalid_columns}")
        df_clean = df_clean.drop(columns=invalid_columns)
    
    # Replace NaN values with None (which becomes null in JSON)
    df_clean = df_clean.where(pd.notnull(df_clean), None)
    
    # Convert to dict
    eeu_data_to_insert = df_clean.to_dict(orient='records')
    print(f"DEBUG: Converted to dict, length: {len(eeu_data_to_insert)}")
    print(f"DEBUG: First record keys: {list(eeu_data_to_insert[0].keys()) if eeu_data_to_insert else 'No records'}")
    
    # Only process the first record (the actual data, not the header row)
    if len(eeu_data_to_insert) > 1:
        eeu_data_to_insert = [eeu_data_to_insert[1]]  # Take the second record (index 1) which has the actual data
    
    eeu_data_to_insert[0]['baseline_design'] = baseline_design
    eeu_data_to_insert[0]['upload_warnings'] = warnings_str
    eeu_data_to_insert[0]['upload_errors'] = errors_str
    eeu_data_to_insert[0]['file_type'] = file_extension
    eeu_data_to_insert[0]['file_name'] = file_name
    eeu_data_to_insert[0]['file_url'] = url
    
    print(f"DEBUG: Final data to insert: {eeu_data_to_insert}")
    
    try:
        data, count = supabase.table('eeu_data')\
            .insert(eeu_data_to_insert)\
            .execute()
        print(f"DEBUG: Successfully inserted data, count: {count}")
    except Exception as e:
        print(f"ERROR: Database insertion failed: {e}")
        print(f"ERROR: Data that failed to insert: {eeu_data_to_insert}")
        return "error"
    avg_energy = float(eeu_data_to_insert[0]['total_energy'])*1000 / float(eeu_data_to_insert[0]['use_type_total_area'])

    return {'status': "success",
            'eeu_id': data[1][0]['id'],
            'conditioned_area': eeu_data_to_insert[0]['use_type_total_area'],
            'climate_zone': eeu_data_to_insert[0]['climate_zone'],
            'total_energy': eeu_data_to_insert[0]['total_energy'],
            'avg_energy': avg_energy,
            'url': url,
            'errors': errors_str,
            'warnings': warnings_str,
            'file_name': file_name,
            'report_type': results.get('report_type')
            }
    
@router.post("/uploadfile/")
async def create_upload_file(item: models.ReportUpload = Depends(), authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    print(f"DEBUG: Upload request received. Authorized: {authorized['is_authorized']}")
    if authorized['is_authorized']:
        print(f"DEBUG: File info - filename: {item.file.filename}, baseline_design: {item.baseline_design}")
        
        BUCKET_NAME = os.environ.get('BUCKET_NAME')

        if BUCKET_NAME is None:
            print("ERROR: BUCKET_NAME environment variable is not set")
            raise ValueError("BUCKET_NAME environment variable is not set")
        #create a unique uuid for the filename
        uuid = uuid4()
        filename_new = 'report_uploads/' + str(uuid) + item.file.filename
        file_name = item.file.filename
        file_extension = os.path.splitext(filename_new)[1]
        print(f"DEBUG: Uploading file to GCS - filename: {filename_new}, extension: {file_extension}")
        url = upload_blob(BUCKET_NAME, filename_new, file_obj = item.file.file,)
        print(f"DEBUG: File uploaded to GCS, URL: {url}")

        

        #if item.report_type == 8:
        if hasattr(item, 'report_type') and item.report_type == 8:
            report_type = item.report_type
            baseline_output = upload_report(url,"baseline",report_type,file_extension=file_extension,file_name = file_name)
            design_output = upload_report(url,"design",report_type,file_extension=file_extension, file_name = file_name)
            return {'report_type':report_type,
                'baseline':baseline_output,
                    'design':design_output}

        else:
            args = {
                'url': url,
                'baseline_design': item.baseline_design,
                'conditioned_area': item.conditioned_area,
                'file_extension': file_extension,
                'file_name': file_name
            }
            if hasattr(item, 'report_type') and item.report_type is not None:
                args['report_type'] = item.report_type

            report_to_upload = upload_report(**args)
            print(f"DEBUG: upload_report returned: {report_to_upload}")
            
            # Check if the parsed report type is PRM (type 8), and if so, process both baseline and design
            if (isinstance(report_to_upload, dict) and 
                'status' in report_to_upload and 
                report_to_upload['status'] == 'success' and 
                report_to_upload.get('report_type') == 8):  # PRM report
                
                # Process both baseline and design for PRM reports
                baseline_output = upload_report(url, "baseline", report_type=8, file_extension=file_extension, file_name=file_name)
                design_output = upload_report(url, "design", report_type=8, file_extension=file_extension, file_name=file_name)
                return {
                    'report_type': 8,
                    'baseline': baseline_output,
                    'design': design_output
                }
            
            # Check if the parsed report type is Multi-Project Excel (type 9)
            if (isinstance(report_to_upload, dict) and 
                'status' in report_to_upload and 
                report_to_upload['status'] == 'success' and 
                report_to_upload.get('report_type') == 9):  # Multi-Project Excel
                
                # Use multi-project service to process the file
                try:
                    from multi_project_service import create_multi_project_service
                    service = create_multi_project_service()
                    result = service.process_multi_project_excel(url, item.company_id)
                    
                    return {
                        'status': result['status'],
                        'report_type': 9,
                        'total_projects': result['total_projects'],
                        'successful_projects': result['successful_projects'],
                        'failed_projects': result['failed_projects'],
                        'validation_errors': result['validation_errors'],
                        'created_project_ids': result.get('created_project_ids', []),
                        'created_projects': result.get('created_projects', []),
                        'message': f"Processed {result['successful_projects']} of {result['total_projects']} projects successfully"
                    }
                except Exception as e:
                    logging_start.logger.error(f"Error processing multi-project Excel: {str(e)}")
                    return {
                        'status': 'error',
                        'message': f"Multi-project processing failed: {str(e)}",
                        'report_type': 9
                    }
            
            print(f"DEBUG: Returning final result: {report_to_upload}")
            return report_to_upload

    else:
        print("ERROR: User not authorized")
        return "not authorized"
@router.post("/submit_multi_upload/")
async def submit_multiupload(item: models.MultiUpload, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    if authorized['is_authorized']:
        company_id = authorized['company_id']
        try:
            multi_upload_response = process_multi_upload(company_id,item.design_files,item.baseline_files)
        except Exception as e:
            print(e)
            return "error multi upload"
        return multi_upload_response
        
    else:
        return "not authorized"

@router.post("/submit_multi_project_excel/")
async def submit_multi_project_excel(item: models.MultiProjectExcelUpload, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    """
    Process multi-project Excel file and create multiple projects
    """
    if not authorized['is_authorized']:
        return {"status": "error", "message": "not authorized"}
    
    try:
        from multi_project_service import create_multi_project_service
        
        service = create_multi_project_service()
        result = service.process_multi_project_excel(item.file_url, item.company_id)
        
        return models.MultiProjectResult(
            status=result['status'],
            total_projects=result['total_projects'],
            successful_projects=result['successful_projects'],
            failed_projects=result['failed_projects'],
            validation_errors=result['validation_errors'],
            created_project_ids=result.get('created_project_ids', []),
            created_projects=result.get('created_projects', [])
        )
        
    except Exception as e:
        logging_start.logger.error(f"Error in multi-project Excel upload: {str(e)}")
        return {
            "status": "error", 
            "message": f"Processing failed: {str(e)}",
            "total_projects": 0,
            "successful_projects": 0,
            "failed_projects": 0,
            "validation_errors": [str(e)],
            "created_project_ids": []
        }

@router.get("/download-multi-project-template/")
async def download_multi_project_template():
    """
    Download the multi-project Excel template with baseline/design energy field columns
    """
    template_path = os.path.join(os.path.dirname(__file__), "dependencies", "d3p-multi-project-template.xlsx")
    
    if not os.path.exists(template_path):
        return {"error": "Template file not found"}

    try:
        # Load template workbook
        wb = load_workbook(template_path)
        ws = wb.active

        # Locate header row by scanning first few rows
        header_row_idx = None
        target_headers = {"project_name", "conditioned_area_sf", "project_use_type"}
        for row_idx in range(1, 6):
            values = [cell.value if cell.value is not None else "" for cell in ws[row_idx]]
            value_set = {str(v).strip() for v in values if str(v).strip() != ""}
            if target_headers.issubset(value_set):
                header_row_idx = row_idx
                break
        if header_row_idx is None:
            header_row_idx = 1

        # Define the EEU energy fields that need baseline/design suffixes
        eeu_energy_fields = [
            'Heating_Electricity', 'Heating_NaturalGas', 'Heating_DistrictHeating', 'Heating_Other',
            'Cooling_Electricity', 'Cooling_DistrictHeating', 'Cooling_Other',
            'DHW_Electricity', 'DHW_NaturalGas', 'DHW_DistrictHeating', 'DHW_Other',
            'Interior Lighting_Electricity', 'Exterior Lighting_Electricity', 'Plug Loads_Electricity',
            'Process Refrigeration_Electricity', 'Fans_Electricity', 'Pumps_Electricity', 'Pumps_NaturalGas',
            'Heat Rejection_Electricity', 'Humidification_Electricity', 'HeatRecovery_Electricity', 'HeatRecovery_Other',
            'ExteriorUsage_Electricity', 'ExteriorUsage_NaturalGas', 'OtherEndUse_Electricity', 'OtherEndUse_NaturalGas', 'OtherEndUse_Other',
            'SolarDHW_On-SiteRenewables', 'SolarPV_On-SiteRenewables', 'Wind_On-SiteRenewables', 'Other_On-SiteRenewables'
        ]

        # Create new headers with baseline/design suffixes for energy fields
        new_headers = []
        
        # First, add all the non-energy fields (shared fields)
        for col_idx, cell in enumerate(ws[header_row_idx], start=1):
            if cell.value:
                header_name = str(cell.value).strip()
                if header_name not in eeu_energy_fields:
                    new_headers.append(header_name)
        
        # Then add all baseline energy fields
        for energy_field in eeu_energy_fields:
            new_headers.append(f"{energy_field}_baseline")
        
        # Finally add all design energy fields
        for energy_field in eeu_energy_fields:
            new_headers.append(f"{energy_field}_design")

        # Clear the existing header row and add new headers
        for col_idx in range(1, ws.max_column + 1):
            ws.cell(row=header_row_idx, column=col_idx).value = None
        
        for col_idx, header in enumerate(new_headers, start=1):
            ws.cell(row=header_row_idx, column=col_idx).value = header
        
        # Apply formatting to the header row
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        # Define border style
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Style the header row
        for col_idx in range(1, len(new_headers) + 1):
            cell = ws.cell(row=header_row_idx, column=col_idx)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border
            
            # Color code the columns
            header_name = new_headers[col_idx - 1]
            if header_name.endswith('_baseline'):
                cell.fill = PatternFill(start_color='E6F3FF', end_color='E6F3FF', fill_type='solid')  # Light blue
            elif header_name.endswith('_design'):
                cell.fill = PatternFill(start_color='E6FFE6', end_color='E6FFE6', fill_type='solid')  # Light green
            else:
                cell.fill = PatternFill(start_color='F0F0F0', end_color='F0F0F0', fill_type='solid')  # Light gray for shared fields

        # Update instruction text to reflect new structure
        ws.cell(row=2, column=1).value = "Include energy data in MBTU. Enter baseline values in blue columns, design values in green columns."
        ws.cell(row=3, column=1).value = "Enter 0.0 for energy types that do not apply to your project."
        
        # Apply borders only to cells with data in instruction rows
        for row_idx in [1, 2, 3]:
            for col_idx in range(1, len(new_headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                # Only apply borders to cells that have data
                if cell.value is not None and str(cell.value).strip() != '':
                    cell.border = thin_border
                    if col_idx == 1:  # Only the first column has text
                        cell.alignment = Alignment(horizontal='left', vertical='center')
                    else:
                        cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Update sample data rows to have clean baseline and design values
        shared_fields_count = len([h for h in new_headers if not h.endswith('_baseline') and not h.endswith('_design')])
        
        for row_idx in range(header_row_idx + 1, ws.max_row + 1):
            # Clear all existing data beyond shared fields
            for col_idx in range(shared_fields_count + 1, ws.max_column + 1):
                ws.cell(row=row_idx, column=col_idx).value = None
            
            # Add clean sample data for baseline energy fields
            baseline_start_col = shared_fields_count + 1
            for i, energy_field in enumerate(eeu_energy_fields):
                col_idx = baseline_start_col + i
                # Use 0.0 for most fields, with a few non-zero examples
                if i < 3:  # First 3 fields get sample values
                    ws.cell(row=row_idx, column=col_idx).value = 100.0 + (i * 50)
                else:
                    ws.cell(row=row_idx, column=col_idx).value = 0.0
            
            # Add clean sample data for design energy fields
            design_start_col = baseline_start_col + len(eeu_energy_fields)
            for i, energy_field in enumerate(eeu_energy_fields):
                col_idx = design_start_col + i
                # Use 0.0 for most fields, with a few non-zero examples
                if i < 3:  # First 3 fields get sample values (typically 20% better than baseline)
                    ws.cell(row=row_idx, column=col_idx).value = 80.0 + (i * 40)
                else:
                    ws.cell(row=row_idx, column=col_idx).value = 0.0
            
            # Apply formatting to data rows
            for col_idx in range(1, len(new_headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = thin_border
                
                # Apply background color to data cells
                header_name = new_headers[col_idx - 1]
                if header_name.endswith('_baseline'):
                    cell.fill = PatternFill(start_color='F0F8FF', end_color='F0F8FF', fill_type='solid')  # Very light blue
                elif header_name.endswith('_design'):
                    cell.fill = PatternFill(start_color='F0FFF0', end_color='F0FFF0', fill_type='solid')  # Very light green

        # Map header names to column letters for validation
        headers = {}
        for col_idx, header in enumerate(new_headers, start=1):
            headers[header] = get_column_letter(col_idx)

        # Prepare allowed values via database and constants
        def fetch_enum_names(table_name: str) -> list:
            try:
                data, _ = supabase.table(table_name).select('name').order('order').execute()
                if data and len(data) > 1:
                    return [row['name'] for row in data[1] if row.get('name')]
            except Exception as e:
                logging_start.logger.warning(f"Failed to fetch {table_name}: {str(e)}")
            return []

        allowed_values_map = {
            'project_use_type': fetch_enum_names('enum_project_use_types'),
            'project_construction_category': fetch_enum_names('enum_project_construction_categories'),
            'project_phase': fetch_enum_names('enum_project_phases'),
            'energy_code': fetch_enum_names('enum_energy_codes'),
            'report_type': fetch_enum_names('enum_report_types'),
            'climate_zone': fetch_enum_names('enum_climate_zones'),
            'area_units': ['sf', 'sm'],
            'energy_units': ['mbtu', 'gj'],
        }

        # Create or replace "Valid Values" sheet
        if 'Valid Values' in wb.sheetnames:
            del wb['Valid Values']
        valid_ws = wb.create_sheet('Valid Values')

        # Write allowed values, one field per column
        field_names = list(allowed_values_map.keys())
        for col_idx, field in enumerate(field_names, start=1):
            col_letter = get_column_letter(col_idx)
            valid_ws[f"{col_letter}1"] = field
            for row_offset, value in enumerate(allowed_values_map[field], start=2):
                valid_ws[f"{col_letter}{row_offset}"] = value

        # Add data validations to first 100 rows after header
        max_rows = 100
        for field, values in allowed_values_map.items():
            if field in headers and values:
                col_letter = headers[field]
                end_row = 1 + len(values)
                formula = f"='Valid Values'!${get_column_letter(field_names.index(field)+1)}$2:${get_column_letter(field_names.index(field)+1)}${end_row}"
                dv = DataValidation(type="list", formula1=formula, allow_blank=True, showErrorMessage=True)
                dv.error = "Select a value from the list."
                dv.errorTitle = "Invalid value"
                ws.add_data_validation(dv)
                for r in range(header_row_idx + 1, header_row_idx + 1 + max_rows):
                    dv.add(f"{col_letter}{r}")

        # Save to a temp file and serve
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp_path = tmp.name
        tmp.close()
        wb.save(tmp_path)

        return FileResponse(
            path=tmp_path,
            filename="d3p-multi-project-template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        logging_start.logger.error(f"Error generating template with validations: {str(e)}")
        # Fall back to static template if dynamic generation fails
        return FileResponse(
            path=template_path,
            filename="d3p-multi-project-template.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

@router.post("/submit_project/")
async def submit_project(item: models.SubmitProject, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    

    if authorized['is_authorized']:
    
        # Convert the item to a dictionary
        item_data = item.model_dump()
        
        item_data.setdefault('design_eeu_id', None)
        item_data.setdefault('energy_code_id', None)

        extract_dict = {}

        if 'baseline_eeu_id' in item_data:
            extract_dict['baseline_eeu_id'] = item_data.pop('baseline_eeu_id')

        if 'design_eeu_id' in item_data:
            extract_dict['design_eeu_id'] = item_data.pop('design_eeu_id')
        

        try:
            data, count = supabase.table('uploads')\
                .insert(item_data)\
                .execute()
        except Exception as e:
            print(e)
            return "error upload table"
        
        def update_eeu_if_exists(key, extract_dict, upload_id):
            if extract_dict.get(key) is not None:
                eeu_data_dict = {
                    'id': extract_dict[key],
                    'upload_id': upload_id
                }
                update_eeu_record(eeu_data_dict['id'], eeu_data_dict['upload_id'])

        # Usage
        update_eeu_if_exists('baseline_eeu_id', extract_dict, data[1][0]['id'])
        update_eeu_if_exists('design_eeu_id', extract_dict, data[1][0]['id'])

        return "success"

    else:
        return "not authorized"