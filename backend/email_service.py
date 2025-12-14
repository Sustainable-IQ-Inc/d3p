import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
import logging_start

logger = logging_start.logger

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@d3p.com')
FRONTEND_URL = os.getenv('REDIRECT_URL', 'http://localhost:8081')
# Admin email addresses (comma-separated list) for failed upload notifications
ADMIN_EMAILS = os.getenv('ADMIN_EMAILS', '').split(',') if os.getenv('ADMIN_EMAILS') else []
# Clean up whitespace and filter out empty strings
ADMIN_EMAILS = [email.strip() for email in ADMIN_EMAILS if email.strip()]


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
    logger.info(f"send_failed_upload_notification_to_admin called for upload_id: {upload_id}")
    logger.info(f"Parameters: user_email={user_email}, file_name={file_name}, baseline_design={baseline_design}, company_name={company_name}")
    
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set, skipping email notification")
        return False
    
    logger.info(f"SENDGRID_API_KEY is set: {bool(SENDGRID_API_KEY)}")
    
    try:
        # Get admin emails from environment variable
        logger.info(f"ADMIN_EMAILS from env: {os.getenv('ADMIN_EMAILS', 'NOT SET')}")
        logger.info(f"ADMIN_EMAILS parsed list: {ADMIN_EMAILS}")
        
        if not ADMIN_EMAILS:
            logger.warning("ADMIN_EMAILS environment variable not set or empty, skipping email notification")
            return False
        
        admin_emails = ADMIN_EMAILS
        logger.info(f"Sending email to admin addresses: {admin_emails}")
        
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
        
        logger.info(f"Creating email message: from={SENDGRID_FROM_EMAIL}, to={admin_emails}, subject={subject}")
        
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=admin_emails,
            subject=subject,
            html_content=content
        )
        
        logger.info(f"Initializing SendGrid client")
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        logger.info(f"Sending email via SendGrid...")
        response = sg.send(message)
        
        logger.info(f"SendGrid response status code: {response.status_code}")
        logger.info(f"SendGrid response headers: {response.headers}")
        logger.info(f"SendGrid response body: {response.body}")
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Failed upload notification sent successfully to admins for upload {upload_id}")
            return True
        else:
            logger.error(f"SendGrid returned non-success status code {response.status_code} for upload {upload_id}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending failed upload notification for upload {upload_id}: {str(e)}", exc_info=True)
        return False


def send_immediate_failed_upload_notification(
    upload_id: int,
    user_email: str,
    file_name: str,
    error_message: str,
    baseline_design: Optional[str] = None,
    company_name: Optional[str] = None
):
    """
    Send email notification to admin immediately when a file upload fails during processing.
    This is different from send_failed_upload_notification_to_admin which is sent when the form is completed.
    """
    if not SENDGRID_API_KEY:
        logger.warning("SENDGRID_API_KEY not set, skipping email notification")
        return False
    
    try:
        # Get admin emails from environment variable
        if not ADMIN_EMAILS:
            logger.warning("ADMIN_EMAILS environment variable not set or empty, skipping email notification")
            return False
        
        admin_emails = ADMIN_EMAILS
        
        # Build email content
        subject = "File Upload Failed - Immediate Notification"
        
        baseline_design_text = ""
        if baseline_design:
            baseline_design_text = f"<p><strong>Type:</strong> {baseline_design.capitalize()}</p>"
        
        company_text = ""
        if company_name:
            company_text = f"<p><strong>Company:</strong> {company_name}</p>"
        
        # Truncate error message if too long for email
        error_display = error_message[:500] + "..." if len(error_message) > 500 else error_message
        
        content = f"""
        <html>
        <body>
            <h2>File Upload Failed</h2>
            <p>A file upload has failed during processing and requires your attention.</p>
            
            <h3>Upload Details:</h3>
            <p><strong>Upload ID:</strong> {upload_id}</p>
            <p><strong>File Name:</strong> {file_name}</p>
            {baseline_design_text}
            {company_text}
            <p><strong>User Email:</strong> {user_email}</p>
            <p><strong>Error Message:</strong></p>
            <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap;">{error_display}</pre>
            
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
        
        logger.info(f"Immediate failed upload notification sent to admins for upload {upload_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending immediate failed upload notification: {str(e)}")
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


