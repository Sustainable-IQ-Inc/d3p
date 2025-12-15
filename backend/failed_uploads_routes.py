from fastapi import APIRouter, Depends, HTTPException, Query
from utils import verify_token, supabase
from typing import Optional, Dict, Union
from gcs_upload import generate_signed_url
from upload_routes import upload_report, get_upload_status_id, get_user_email
from email_service import send_upload_complete_notification_to_user
import logging_start
import os
from urllib.parse import urlparse

router = APIRouter()

@router.get("/pending-uploads/")
async def get_pending_uploads(authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    """Get user's pending/failed uploads"""
    if not authorized['is_authorized']:
        return {"error": "not authorized"}
    
    user_id = authorized.get('user_id')
    company_id = authorized.get('company_id')
    
    if not user_id or not company_id:
        logging_start.logger.warning(f"Missing user_id or company_id. user_id: {user_id}, company_id: {company_id}")
        return []
    
    try:
        # Get pending and failed status IDs
        pending_status_id = get_upload_status_id('pending')
        failed_status_id = get_upload_status_id('failed')
        
        logging_start.logger.info(f"Status IDs - pending: {pending_status_id}, failed: {failed_status_id}")
        
        status_ids = []
        if pending_status_id:
            status_ids.append(pending_status_id)
        if failed_status_id:
            status_ids.append(failed_status_id)
        
        if not status_ids:
            logging_start.logger.warning("No status IDs found for pending/failed")
            return []
        
        # Note: user_id in uploads table is bigint (references old users table), 
        # but we have UUID from Supabase auth, so we filter by company_id only
        query = supabase.table('uploads')\
            .select('id, file_name, created_at, processing_error, upload_status_id, project_id, file_url, baseline_status, design_status')\
            .in_('upload_status_id', status_ids)\
            .eq('company_id', company_id)\
            .order('created_at', desc=True)
        
        # Note: We include uploads with or without project_id, as a user may have
        # submitted project details for a failed upload, but it's still pending processing
        
        data, _ = query.execute()
        
        logging_start.logger.info(f"Found {len(data[1]) if data and len(data) > 1 else 0} pending/failed uploads for user {user_id}")
        
        if data and len(data) > 1:
            return data[1]
        return []
        
    except Exception as e:
        logging_start.logger.error(f"Error getting pending uploads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/failed-uploads/")
async def get_failed_uploads(authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    """Get all failed and pending uploads (superadmin only)"""
    if not authorized['is_authorized'] or authorized.get('role') != 'superadmin':
        return {"error": "not authorized"}
    
    try:
        failed_status_id = get_upload_status_id('failed')
        pending_status_id = get_upload_status_id('pending')
        
        status_ids = []
        if failed_status_id:
            status_ids.append(failed_status_id)
        if pending_status_id:
            status_ids.append(pending_status_id)
        
        if not status_ids:
            return []
        
        # Get uploads that are either failed or pending (pending means user submitted details but processing hasn't completed)
        # Note: user_id in uploads is bigint (old users table), so we can't join with profiles (UUID)
        # We'll get company info separately
        query = supabase.table('uploads')\
            .select('id, file_name, created_at, processing_error, upload_status_id, project_id, file_url, user_id, company_id, baseline_status, design_status, notified_admin, companies(company_name)')\
            .in_('upload_status_id', status_ids)\
            .order('created_at', desc=True)
        
        data, _ = query.execute()
        
        if data and len(data) > 1:
            # Enrich with user email from profiles if we can find it via project
            enriched_data = []
            for upload in data[1]:
                upload_dict = dict(upload)
                
                # Try to get user email from the project's edit history or recent uploads
                user_email = 'N/A'
                if upload_dict.get('project_id'):
                    try:
                        # Try to get the most recent user who worked on this project from edit_history
                        history_data, _ = supabase.table('edit_history')\
                            .select('user_id')\
                            .eq('table_name', 'projects')\
                            .eq('record_id', upload_dict['project_id'])\
                            .order('created_at', desc=True)\
                            .limit(1)\
                            .execute()
                        
                        if history_data and len(history_data) > 1 and history_data[1]:
                            # user_id in edit_history is UUID, so we can get email from profiles
                            history_user_id = history_data[1][0].get('user_id')
                            if history_user_id:
                                profile_data, _ = supabase.table('profiles')\
                                    .select('email')\
                                    .eq('id', history_user_id)\
                                    .limit(1)\
                                    .execute()
                                if profile_data and len(profile_data) > 1 and profile_data[1]:
                                    user_email = profile_data[1][0].get('email', 'N/A')
                    except Exception as e:
                        logging_start.logger.warning(f"Could not get user email for upload {upload_dict.get('id')}: {e}")
                
                upload_dict['user_email'] = user_email
                enriched_data.append(upload_dict)
            
            return enriched_data
        return []
        
    except Exception as e:
        logging_start.logger.error(f"Error getting failed uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/failed-uploads/{upload_id}/download")
async def download_failed_file(upload_id: int, authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)):
    """Get signed URL to download failed file"""
    if not authorized['is_authorized'] or authorized.get('role') != 'superadmin':
        logging_start.logger.warning(f"Unauthorized download attempt for upload_id: {upload_id}")
        return {"error": "not authorized"}
    
    try:
        logging_start.logger.info(f"Download request for upload_id: {upload_id}")
        # Get upload record - need baseline_eeu_id and design_eeu_id to find file in eeu_data
        upload_data, _ = supabase.table('uploads')\
            .select('file_url, file_name, project_id, created_at, upload_status_id, design_baseline_type')\
            .eq('id', upload_id)\
            .limit(1)\
            .execute()
        
        if not upload_data or len(upload_data) <= 1 or not upload_data[1]:
            logging_start.logger.warning(f"Upload not found: {upload_id}")
            raise HTTPException(status_code=404, detail="Upload not found")
        
        upload_record = upload_data[1][0]
        file_url = upload_record.get('file_url')
        file_name = upload_record.get('file_name')
        project_id = upload_record.get('project_id')
        design_baseline_type = upload_record.get('design_baseline_type')
        logging_start.logger.info(f"Found upload {upload_id}, file_url present: {bool(file_url)}, file_name: {file_name}, project_id: {project_id}, type: {design_baseline_type}")
        
        # Check if file_url is None or empty string
        if not file_url or (isinstance(file_url, str) and not file_url.strip()):
            # For all uploads, file_url is stored in eeu_data table
            # eeu_data has upload_id pointing back to uploads
            try:
                eeu_data, _ = supabase.table('eeu_data')\
                    .select('file_url, file_name')\
                    .eq('upload_id', upload_id)\
                    .execute()
                if eeu_data and len(eeu_data) > 1 and eeu_data[1]:
                    # Get the first eeu_data record with a file_url
                    for eeu_record in eeu_data[1]:
                        if eeu_record.get('file_url'):
                            file_url = eeu_record.get('file_url')
                            if not file_name and eeu_record.get('file_name'):
                                file_name = eeu_record.get('file_name')
                            logging_start.logger.info(f"Found file_url in eeu_data for upload_id: {upload_id}")
                            break
            except Exception as e:
                logging_start.logger.warning(f"Error checking eeu_data for upload_id {upload_id}: {e}")
            
            if not file_url:
                error_msg = f"File URL not found for upload {upload_id}. This upload may have been created without a file, or the file may have been deleted."
                logging_start.logger.error(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
        
        # Use a default file_name if still missing
        if not file_name:
            file_name = f"upload_{upload_id}_file"
        
        # Generate signed URL
        # Parse URL to get blob name first
        parsed = urlparse(file_url)
        path = parsed.path.lstrip('/')
        logging_start.logger.info(f"Parsed file_url path: {path}, netloc: {parsed.netloc}")
        
        BUCKET_NAME = os.environ.get('BUCKET_NAME')
        
        # Handle different GCS URL formats:
        # 1. https://storage.googleapis.com/BUCKET_NAME/blob/path
        # 2. https://storage.googleapis.com/BUCKET_NAME/blob/path?signature=...
        # 3. /BUCKET_NAME/blob/path (from signed URLs)
        # 4. BUCKET_NAME/blob/path (already parsed)
        
        # If the netloc is storage.googleapis.com, the path is /BUCKET_NAME/blob/path
        if parsed.netloc == 'storage.googleapis.com' or parsed.netloc.endswith('.storage.googleapis.com'):
            # Path format: /BUCKET_NAME/blob/path
            # Remove leading / and extract blob path after bucket name
            path_parts = path.split('/', 1)
            if len(path_parts) > 1:
                # First part is bucket name, second part is blob path
                blob_name = path_parts[1]
            else:
                blob_name = path
        elif BUCKET_NAME and path.startswith(BUCKET_NAME + '/'):
            # Path already includes bucket name at start
            blob_name = path[len(BUCKET_NAME) + 1:]
        elif '/' in path:
            # Try to extract blob path - assume first part might be bucket name
            parts = path.split('/', 1)
            if len(parts) > 1:
                # Check if first part looks like a bucket name
                first_part = parts[0]
                # If it contains dashes and no dots, likely a bucket name
                if '-' in first_part and '.' not in first_part and first_part != 'report_uploads' and first_part != 'failed_uploads':
                    blob_name = parts[1]  # Second part is blob path
                else:
                    # First part is part of the blob path
                    blob_name = path
            else:
                blob_name = path
        else:
            blob_name = path
        
        logging_start.logger.info(f"Extracted blob_name: {blob_name}")
        
        # Final cleanup: if blob_name still starts with bucket name, remove it
        if BUCKET_NAME and blob_name.startswith(BUCKET_NAME + '/'):
            blob_name = blob_name[len(BUCKET_NAME) + 1:]
            logging_start.logger.info(f"Removed bucket name from blob_name, new blob_name: {blob_name}")
        
        try:
            # Generate new signed URL using the corrected blob name
            signed_url = generate_signed_url(blob_name, download_as=file_name)
            logging_start.logger.info(f"Generated signed URL successfully for upload_id: {upload_id}, blob_name: {blob_name}")
            return {"signed_url": signed_url, "file_name": file_name}
        except Exception as e:
            logging_start.logger.error(f"Error generating signed URL for blob_name '{blob_name}': {e}", exc_info=True)
            error_str = str(e)
            
            # If NoSuchKey error, the file might not exist or blob name is wrong
            if 'NoSuchKey' in error_str or 'does not exist' in error_str.lower():
                error_msg = f"File not found in GCS. Blob name: {blob_name}. The file may have been deleted or the file URL is incorrect."
                logging_start.logger.error(error_msg)
                raise HTTPException(status_code=404, detail=error_msg)
            
            # For other errors, return original URL as fallback
            logging_start.logger.warning(f"Returning original URL as fallback due to error: {e}")
            return {"signed_url": file_url, "file_name": file_name}
        
    except HTTPException:
        raise
    except Exception as e:
        logging_start.logger.error(f"Error downloading failed file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/admin/failed-uploads/{upload_id}/file-url")
async def update_failed_upload_file_url(
    upload_id: int,
    file_url: str,
    file_name: Optional[str] = None,
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token)
):
    """Update the file_url for a failed upload (superadmin only)"""
    if not authorized['is_authorized'] or authorized.get('role') != 'superadmin':
        return {"error": "not authorized"}
    
    try:
        logging_start.logger.info(f"Updating file_url for upload {upload_id}")
        
        # Verify upload exists
        upload_data, _ = supabase.table('uploads')\
            .select('id')\
            .eq('id', upload_id)\
            .limit(1)\
            .execute()
        
        if not upload_data or len(upload_data) <= 1 or not upload_data[1]:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        # Update file_url (and optionally file_name)
        update_data = {'file_url': file_url}
        if file_name:
            update_data['file_name'] = file_name
        
        supabase.table('uploads')\
            .update(update_data)\
            .eq('id', upload_id)\
            .execute()
        
        logging_start.logger.info(f"Updated file_url for upload {upload_id}")
        return {"status": "success", "message": f"Updated file_url for upload {upload_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging_start.logger.error(f"Error updating file_url for upload {upload_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/failed-uploads/{upload_id}/rerun")
async def rerun_failed_upload(
    upload_id: int,
    authorized: Dict[str, Union[bool, Optional[str]]] = Depends(verify_token),
    baseline_design: Optional[str] = Query(None)
):
    """Rerun processing for failed upload"""
    if not authorized['is_authorized'] or authorized.get('role') != 'superadmin':
        return {"error": "not authorized"}
    
    try:
        # Get upload record
        upload_data, _ = supabase.table('uploads')\
            .select('file_url, file_name, processing_error, user_id, company_id, project_id, report_type_id, baseline_status, design_status')\
            .eq('id', upload_id)\
            .limit(1)\
            .execute()
        
        if not upload_data or len(upload_data) <= 1 or not upload_data[1]:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        upload = upload_data[1][0]
        file_url = upload.get('file_url')
        file_name = upload.get('file_name')
        user_id = upload.get('user_id')
        company_id = upload.get('company_id')
        project_id = upload.get('project_id')
        report_type_id = upload.get('report_type_id')
        
        if not file_url:
            logging_start.logger.warning(f"Upload {upload_id} has no file_url. Cannot rerun.")
            raise HTTPException(status_code=400, detail="File URL not found for this upload. The file may have been deleted or the upload was created without a file.")
        
        # Determine which side to rerun
        baseline_failed = upload.get('baseline_status') == 'failed'
        design_failed = upload.get('design_status') == 'failed'
        
        if baseline_design:
            # Rerun specific side
            side_to_rerun = baseline_design
        elif baseline_failed and not design_failed:
            side_to_rerun = 'baseline'
        elif design_failed and not baseline_failed:
            side_to_rerun = 'design'
        elif baseline_failed and design_failed:
            # Both failed, need to specify which to rerun
            raise HTTPException(status_code=400, detail="Both baseline and design failed. Please specify baseline_design parameter.")
        else:
            # General failure, try to determine from file
            side_to_rerun = 'baseline'  # Default
        
        # Get file extension
        file_extension = os.path.splitext(file_name or '')[1] if file_name else None
        
        # Rerun processing
        result = upload_report(
            file_url,
            side_to_rerun,
            report_type=report_type_id,
            file_extension=file_extension,
            file_name=file_name,
            user_id=user_id,
            company_id=company_id
        )
        
        if result.get('status') == 'success':
            # Update upload record
            completed_status_id = get_upload_status_id('completed')
            update_data = {
                'upload_status_id': completed_status_id,
                'processing_error': None
            }
            
            # Update baseline/design status
            if side_to_rerun == 'baseline':
                update_data['baseline_status'] = 'completed'
            else:
                update_data['design_status'] = 'completed'
            
            # If both sides are now completed, mark overall as completed
            if side_to_rerun == 'baseline' and upload.get('design_status') != 'failed':
                update_data['baseline_status'] = 'completed'
            elif side_to_rerun == 'design' and upload.get('baseline_status') != 'failed':
                update_data['design_status'] = 'completed'
            
            supabase.table('uploads')\
                .update(update_data)\
                .eq('id', upload_id)\
                .execute()
            
            # Get project name for email
            project_name = None
            if project_id:
                try:
                    project_data, _ = supabase.table('projects')\
                        .select('project_name')\
                        .eq('id', project_id)\
                        .limit(1)\
                        .execute()
                    if project_data and len(project_data) > 1 and project_data[1]:
                        project_name = project_data[1][0].get('project_name')
                except:
                    pass
            
            # Send completion email to user
            user_email = get_user_email(user_id)
            if user_email and project_id:
                send_upload_complete_notification_to_user(
                    upload_id,
                    user_email,
                    project_id,
                    project_name or 'Your Project',
                    side_to_rerun
                )
                
                # Mark as notified
                supabase.table('uploads')\
                    .update({'notified_user_complete': True})\
                    .eq('id', upload_id)\
                    .execute()
            
            return {
                "status": "success",
                "message": f"{side_to_rerun.capitalize()} processing completed successfully",
                "eeu_id": result.get('eeu_id')
            }
        else:
            # Update error message
            error_msg = result.get('errors', result.get('message', 'Processing failed'))
            update_data = {
                'processing_error': error_msg
            }
            
            if side_to_rerun == 'baseline':
                update_data['baseline_status'] = 'failed'
            else:
                update_data['design_status'] = 'failed'
            
            supabase.table('uploads')\
                .update(update_data)\
                .eq('id', upload_id)\
                .execute()
            
            return {
                "status": "error",
                "message": f"{side_to_rerun.capitalize()} processing failed",
                "errors": error_msg
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logging_start.logger.error(f"Error rerunning failed upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

