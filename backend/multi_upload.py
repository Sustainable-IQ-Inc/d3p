from utils import supabase
import pandas as pd

from conversions import convert_units_in_table

def return_matched_files_details(upload_batch_id,baseline_design):
        query = supabase.table('eeu_data')\
            .select('id,total_energy,use_type_total_area,climate_zone,upload_id,file_name')\
            .eq('upload_batch_id', upload_batch_id)\
            .eq('baseline_design', baseline_design)\
        
        
        data, count = query.execute()
        
        if data[1] != []:
            #in future, add a conversion here for all the energy and area columns
            return data[1]
        else:
            return "no results"

#create an upload_batch
#eeu_data_uploads should be a dict with eeu_data_id, baseline_design


def create_upload_batch(company_id):
    upload_batch_dict = {'company_id':company_id}
    try:
        data, count = supabase.table('upload_batches')\
            .insert(upload_batch_dict)\
            .execute()
        upload_batch_id = data[1][0]['id']
        return upload_batch_id
    except Exception as e:
        print(e)
        return "error upload table"
    
def create_uploads_for_design_files(design_files,upload_batch_id,company_id):

    upload_data = {'upload_batch_id':upload_batch_id,'company_id':company_id}

    upload_ids = []

    for design_file in design_files:
        #create a new upload record and associate the eeu_id with it.
        try:
            data, count = supabase.table('uploads')\
                .insert(upload_data)\
                .execute()
            upload_id = data[1][0]['id']
            upload_ids.append(upload_id)
            
        except Exception as e:
            print(e)
            return "error upload table"
        
        try:
            update_eeu_data = {'upload_id':upload_id}
            data, count = supabase.table('eeu_data')\
                .update(update_eeu_data)\
                .eq('id', design_file)\
                .execute()

        
        except Exception as e:
            print(e)
            return "error updating eeu_data table with upload_id"
    return upload_ids



def update_uploads_with_batch_id(design_files,baseline_files,upload_batch_id):    
    uploads_list = design_files + baseline_files
    for eeu_data_upload in uploads_list:
        update_dict = {'upload_batch_id':upload_batch_id}
        #if the upload is a design recrod, create a new upload record and associate the eeu_id with it. 
        #append the new upload_id to the uploads_list
        #Associate the upload with the batch
        #add the upload record_id to the update_dict
        try:
            data, count = supabase.table('eeu_data')\
                .update(update_dict)\
                .eq('id', eeu_data_upload)\
                .execute()
            

            
        except Exception as e:
            print(e)
            return "error eeu table"
        
    return "success"
        
    #return the list of uploads with their id, filename and the count of unmatched baseline files


def process_multi_upload(company_id,design_files,baseline_files):
    try:
        batch_id = create_upload_batch(company_id)
    except Exception as e:
        print(e)
        return "error creating batch"
    try:
        create_uploads_for_design_files(design_files,batch_id,company_id)
        
    except Exception as e:
        print(e)
        return "error creating uploads"
    try:
        update_uploads_with_batch_id(design_files,baseline_files,batch_id)
        uploads = return_matched_files_details(batch_id,baseline_design='design')
    except Exception as e:
        print(e)
        return "error updating uploads"
    try:
        unmatched_baseline_files = return_matched_files_details(batch_id,baseline_design='baseline')
    except Exception as e:
        print(e)
        return "error getting unmatched baseline files"
    response = {"uploads":uploads,"unmatched_baseline_files":unmatched_baseline_files}
    return response
    
    



        


        
         
        
   





#associate each upload with the upload_batch

