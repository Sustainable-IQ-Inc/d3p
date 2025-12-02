from pathlib import Path
import pandas as pd
import requests
import pdfplumber
import io
import re
##Script 1 Parsing for IESVE Report


#creates a function to parse the IESVE report
def parse_report_iesve(url):
 
  #sets the path to save the file to
  #filename = Path('temp/report.pdf')

  #takes URL from Airatble and stores that PDF to the path, above
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    pdf_file = io.BytesIO(response.content)


    pdf = pdfplumber.open(pdf_file)
    
    # Validate PDF has pages
    if len(pdf.pages) == 0:
        raise ValueError("PDF file has no pages")
    
    first_page = pdf.pages[0]

    #parameters for how to parse the PDF
    table_settings = {
        "vertical_strategy": "text",
        "horizontal_strategy": "text",
        "min_words_vertical": 5,
        
    }

    page1=pdf.pages[0]

    ##print details of words to find locations of tables to extract
    #print(page1.extract_words(x_tolerance=4, y_tolerance=3, keep_blank_chars=False, use_text_flow=False, horizontal_ltr=True, vertical_ttb=True, extra_attrs=[]))

    #set bounding box for EEU (main) table to extract

    eeu_table = page1.crop((43,140,400,350),relative=True)

    eeu_table=eeu_table.extract_table(table_settings)
    
    # Validate that we extracted the EEU table
    if not eeu_table or len(eeu_table) == 0:
        raise ValueError("Could not extract energy end use table from PDF")
    
    if len(eeu_table) < 2:
        raise ValueError("Energy end use table is empty or has no data rows")
    
    if len(eeu_table[0]) == 0:
        raise ValueError("Energy end use table has no column headers")
    
    # Clean column headers - handle split headers and normalize whitespace
    raw_headers = eeu_table[0]
    cleaned_headers = []
    for header in raw_headers:
        if header:
            # Clean whitespace and newlines
            cleaned = str(header).strip().replace('\n', ' ').replace('\r', ' ')
            # Normalize multiple spaces to single space
            cleaned = ' '.join(cleaned.split())
            cleaned_headers.append(cleaned)
        else:
            cleaned_headers.append('')
    
    # Try to merge split headers by looking for patterns
    # Common pattern: "Site Energy" might be split as "Site Energy   So" and "urce Energy CO2"
    merged_headers = []
    i = 0
    while i < len(cleaned_headers):
        current = cleaned_headers[i]
        
        # Check if this looks like a split header that should be merged with next
        if i < len(cleaned_headers) - 1:
            next_header = cleaned_headers[i + 1]
            
            # Pattern: "Site Energy   So" + "urce Energy CO2" = "Site Energy" + "Source Energy CO2"
            if "Site Energy" in current and "urce Energy" in next_header:
                merged_headers.append("Site Energy")
                merged_headers.append("Source Energy CO2")
                i += 2
                continue
            # Pattern: "Site Energy" at end + "Source" at start of next
            elif current.endswith("Site Energy") and next_header.startswith("Source"):
                merged_headers.append("Site Energy")
                merged_headers.append("Source Energy CO2")
                i += 2
                continue
            # Pattern: "Emi" + "ssions" or similar
            elif current == "Emi" and next_header.startswith("ssions"):
                merged_headers.append("CO2 Emissions")
                i += 2
                continue
        
        merged_headers.append(current)
        i += 1
    
    # Use cleaned/merged headers
    # Ensure we have the right number of columns (use original count, pad if needed)
    num_cols_needed = len(eeu_table[0]) if len(eeu_table) > 0 else 0
    if len(merged_headers) < num_cols_needed:
        # Pad with empty strings if we merged columns
        merged_headers.extend([''] * (num_cols_needed - len(merged_headers)))
    elif len(merged_headers) > num_cols_needed:
        # Truncate if we have too many
        merged_headers = merged_headers[:num_cols_needed]
    
    df = pd.DataFrame(eeu_table[1::], columns=merged_headers[:num_cols_needed])
    nan_value = float("NaN")
    #cleans up the data table output
    df.replace("", nan_value, inplace=True)
    
    # Clean column names one more time after DataFrame creation
    df.columns = [str(col).strip().replace('\n', ' ').replace('\r', ' ') for col in df.columns]
    df.columns = [' '.join(str(col).split()) for col in df.columns]
    
    # Validate required columns exist before processing
    # Use flexible matching for split/malformed column names
    energy_col = None
    for col in df.columns:
        col_str = str(col).strip()
        col_lower = col_str.lower().replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Look for "site energy" - check if column contains these words in order
        # Handle cases like "Site Energy   So" where "Site Energy" appears first
        if 'site' in col_lower and 'energy' in col_lower:
            # Make sure "site" comes before "energy" and it's not "source energy"
            site_idx = col_lower.find('site')
            energy_idx = col_lower.find('energy')
            if site_idx < energy_idx and not col_lower.startswith('source'):
                energy_col = col
                break
        # Look for just "energy" (but not "source energy" or "end use")
        elif col_lower == 'energy' or (col_lower.startswith('energy') and 'end' not in col_lower and 'source' not in col_lower):
            energy_col = col
            break
    
    # If still not found, try looking for columns that start with "Site Energy" even with extra text
    if energy_col is None:
        for col in df.columns:
            col_str = str(col).strip()
            if col_str.startswith('Site Energy') or 'Site Energy' in col_str:
                # Make sure it's not "Source Energy"
                if not col_str.startswith('Source'):
                    energy_col = col
                    break
    
    if energy_col is None:
        raise ValueError(f"Required energy column not found in table. Available columns: {list(df.columns)}")
    
    df.dropna(subset = [energy_col], inplace=True)
    
    # Validate we still have data after dropping NaN
    if len(df) == 0:
        raise ValueError("No valid energy data found after cleaning")
    
    #renames columns - use flexible matching for split/malformed column names
    rename_map = {}
    
    # Find report field column using flexible matching
    report_field_col = None
    for col in df.columns:
        col_lower = str(col).lower().replace(' ', '')
        if 'energyenduse' in col_lower or 'enduse' in col_lower:
            report_field_col = col
            break
    if report_field_col:
        rename_map[report_field_col] = 'report_field'
    
    # Use the energy_col we found earlier
    if energy_col:
        rename_map[energy_col] = 'energy_value'
    
    # Handle source energy columns with flexible matching
    source_energy_col = None
    for col in df.columns:
        col_lower = str(col).lower().replace(' ', '')
        if 'sourceenergy' in col_lower or (col_lower.startswith('source') and 'energy' in col_lower):
            source_energy_col = col
            break
    if source_energy_col:
        rename_map[source_energy_col] = 'Source Energy'
    
    # Handle emissions columns with flexible matching
    emissions_col = None
    for col in df.columns:
        col_lower = str(col).lower().replace(' ', '')
        if 'emissions' in col_lower or col_lower == 'emi' or (col_lower.startswith('co2') and 'em' in col_lower):
            emissions_col = col
            break
    if emissions_col:
        rename_map[emissions_col] = 'CO2 Emissions'
    
    df = df.rename(columns=rename_map)
    
    # Validate required columns after renaming
    if 'report_field' not in df.columns:
        raise ValueError(f"Could not find energy end use column in table. Available columns: {list(df.columns)}")
    if 'energy_value' not in df.columns:
        raise ValueError(f"Could not find energy value column in table. Available columns: {list(df.columns)}")
    df['report_field']=df['report_field'].str.strip()

    df['energy_units']='mbtu'
    #df['co2_emissions_units']='kgco2/ft2/yr'

    #drop columns that aren't necessary for raw export (only if they exist)
    columns_to_drop = []
    if 'Source Energy' in df.columns:
        columns_to_drop.append('Source Energy')
    if 'CO2 Emissions' in df.columns:
        columns_to_drop.append('CO2 Emissions')
    
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop, axis=1)
    df = df.reset_index(drop=True)

    #pulls the information that the conditioned space value is in
    conditioned_table = page1.crop((350,100,595,200),relative=True)
    conditioned_table=conditioned_table.extract_table()
    
    # Validate conditioned table extraction
    if not conditioned_table or len(conditioned_table) == 0:
        raise ValueError("Could not extract conditioned area table from PDF")
    
    df_conditioned = pd.DataFrame(conditioned_table[0::],columns=['field','value'])
    df_conditioned.drop(columns=['field'])

    # Validate we have data in conditioned table
    if len(df_conditioned) == 0:
        raise ValueError("Conditioned area table is empty")
    
    if df_conditioned.shape[1] < 2:
        raise ValueError("Conditioned area table does not have expected format")
    
    df['conditioned_area_sf']=df_conditioned.iloc[0, 1]

    
    df['energy_value']=pd.to_numeric(df["energy_value"], downcast="float")
    df['conditioned_area_sf']=pd.to_numeric(df["conditioned_area_sf"], downcast="float")

    df['energy_value']=df['energy_value']*df['conditioned_area_sf']/1000
    df['report']='iesve'

    project_table = page1.crop((30,77,500,150),relative=True)
    project_table=project_table.extract_table()
    
    # Validate project table extraction
    if not project_table or len(project_table) == 0:
        raise ValueError("Could not extract project information table from PDF")
    
    print(project_table)
    df_project = pd.DataFrame(project_table,columns=['field','value'])
    df_project.drop(columns=['field'])

    # Validate we have enough rows in project table
    if len(df_project) == 0:
        raise ValueError("Project information table is empty")
    
    if df_project.shape[1] < 2:
        raise ValueError("Project information table does not have expected format")
    
    if len(df_project) < 1:
        raise ValueError("Project information table does not have project name row")
    
    df['project_name']=df_project.iloc[0, 1]
    
    # Find weather string by searching for patterns instead of assuming row position
    weather_string = None
    
    # Look for weather string by searching for common patterns
    # Pattern 1: Look for "Climate File" or "Weather file" in the field column
    for idx, row in df_project.iterrows():
        field_val = str(row.iloc[0]).lower() if len(row) > 0 else ''
        if 'climate' in field_val or 'weather' in field_val:
            if len(row) > 1:
                weather_string = str(row.iloc[1])
                break
    
    # Pattern 2: Look for WMO code pattern (6 digits) in any value
    if weather_string is None:
        for idx, row in df_project.iterrows():
            if len(row) > 1:
                value_str = str(row.iloc[1])
                # Look for WMO code pattern: typically appears as part of weather file name
                # Pattern: .722780 or similar (dot followed by 6 digits)
                if re.search(r'\.\d{6}', value_str) or re.search(r'\d{6}', value_str):
                    weather_string = value_str
                    break
    
    # Pattern 3: Fallback to row 2 if it exists (original behavior)
    if weather_string is None:
        if len(df_project) >= 3:
            weather_string = str(df_project.iloc[2, 1])
        else:
            raise ValueError("Could not find weather string in project table. Available rows: " + str([str(row.iloc[0]) + ": " + str(row.iloc[1]) if len(row) > 1 else str(row.iloc[0]) for idx, row in df_project.iterrows()]))
    
    # Clean the weather string
    if weather_string:
        weather_string = weather_string.strip()
        df['weather_string'] = weather_string
        print(f"DEBUG: Extracted weather_string: {weather_string}")
    else:
        # Print available rows for debugging
        available_rows = []
        for idx, row in df_project.iterrows():
            if len(row) > 1:
                available_rows.append(f"Row {idx}: '{row.iloc[0]}' = '{row.iloc[1]}'")
            else:
                available_rows.append(f"Row {idx}: '{row.iloc[0]}'")
        raise ValueError(f"Weather string is empty after extraction. Available rows: {', '.join(available_rows)}")

    #save_to='/content/drive/MyDrive/colab/energy/BEM Examples/Scripts/Outputs/Script 1/raw/'+export_filename

    #df.to_csv(save_to)
  except Exception as e:
    print(f"Error parsing IESVE report: {e}")
    # Re-raise the exception so it's caught by the caller's error handling
    raise

  return {'df':df,
                'warnings':[] ## warnings to be configured
                }