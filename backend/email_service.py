import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
import logging_start

logger = logging_start.logger

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@d3p.com')
FRONTEND_URL = os.getenv('REDIRECT_URL', 'http://localhost:8081')


def send_failed_upload_notification_to_admin(
    upload_id: int,
    user_email: str,
    file_name: str,
    error_message: str,
    baseline_design: Optional[str] = None,
    company_name: Optional[str] = None
):
    """
    Send email notification to admin when a failed upload form is completed.
    """
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set, skipping email notification")
        return False
    
    try:
        # Get admin emails (superadmin role)
        from utils import supabase
        
        admin_query = supabase.table('profiles')\
            .select('email')\
            .eq('role', 'superadmin')
        
        admin_data, _ = admin_query.execute()
        
        if not admin_data or len(admin_data) == 0:
            logger.warning("No admin users found to notify")
            return False
        
        admin_emails = [admin['email'] for admin in admin_data if admin.get('email')]
        
        if not admin_emails:
            logger.warning("No admin email addresses found")
            return False
        
        # Build email content
        subject = "New Failed Upload Requires Attention"
        
        baseline_design_text = ""
        if baseline_design:
            baseline_design_text = f"<p><strong>Type:</strong> {baseline_design.capitalize()}</p>"
        
        company_text = ""
        if company_name:
            company_text = f"<p><strong>Company:</strong> {company_name}</p>"
        
        content = f"""
        <html>
        <body>
            <h2>Failed Upload Notification</h2>
            <p>A user has completed the form for a failed file upload that requires your attention.</p>
            
            <h3>Upload Details:</h3>
            <p><strong>Upload ID:</strong> {upload_id}</p>
            <p><strong>File Name:</strong> {file_name}</p>
            {baseline_design_text}
            {company_text}
            <p><strong>User Email:</strong> {user_email}</p>
            <p><strong>Error Message:</strong> {error_message}</p>
            
            <p><a href="{FRONTEND_URL}/admin/failed-uploads">View Failed Uploads</a></p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=admin_emails,
            subject=subject,
            html_content=content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Failed upload notification sent to admins for upload {upload_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending failed upload notification: {str(e)}")
        return False


def send_upload_complete_notification_to_user(
    upload_id: int,
    user_email: str,
    project_id: str,
    project_name: str,
    baseline_design: Optional[str] = None
):
    """
    Send email notification to user when their upload has been successfully processed.
    """
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set, skipping email notification")
        return False
    
    try:
        subject = "Your Upload Has Been Processed"
        
        baseline_design_text = ""
        if baseline_design:
            baseline_design_text = f"<p><strong>Type:</strong> {baseline_design.capitalize()}</p>"
        
        content = f"""
        <html>
        <body>
            <h2>Upload Processing Complete</h2>
            <p>Your file upload has been successfully processed!</p>
            
            <h3>Project Details:</h3>
            <p><strong>Project Name:</strong> {project_name}</p>
            {baseline_design_text}
            
            <p><a href="{FRONTEND_URL}/projects/{project_id}">View Project</a></p>
        </body>
        </html>
        """
        
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=user_email,
            subject=subject,
            html_content=content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Upload complete notification sent to {user_email} for upload {upload_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending upload complete notification: {str(e)}")
        return False


