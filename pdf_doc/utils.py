import os
import logging
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from reportlab.lib.pagesizes import A4


from reportlab.lib.colors import black

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def generate_pdf(document):
    """
    Generate PDF from document data using ReportLab.
    """
    try:
        # Create a buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object using ReportLab
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Add title
        elements.append(Paragraph(document.title, title_style))
        
        # Add office name
        elements.append(Paragraph(
            document.office_name,
            ParagraphStyle(
                'OfficeName',
                parent=styles['Normal'],
                fontSize=16,
                spaceAfter=20,
                alignment=1
            )
        ))
        
        # Add date
        elements.append(Paragraph(
            f"Date: {document.date.strftime('%B %d, %Y')}",
            ParagraphStyle(
                'Date',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20,
                alignment=1
            )
        ))
        
        # Add receiver
        elements.append(Paragraph(
            f"To: {document.receiver}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 12))
        
        # Add sections with headers
        sections = [
            ('Description', document.description),
            ('Summary', document.summary),
            ('Object', document.object)
        ]
        
        for section_title, content in sections:
            # Add section header
            elements.append(Paragraph(
                section_title,
                styles['Heading2']
            ))
            # Add section content
            elements.append(Paragraph(
                content,
                styles['Normal']
            ))
            elements.append(Spacer(1, 12))

        # Add signatures
        signature_data = [
            ['Created By:', 'Approved By:' if document.accepted_by else ''],
            [document.created_by.get_full_name() or document.created_by.username,
             document.accepted_by.get_full_name() or document.accepted_by.username if document.accepted_by else '']
        ]
        
        signature_table = Table(
            signature_data,
            colWidths=[doc.width/2 - 12]*2,
            style=TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 50),
                ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
            ])
        )
        
        elements.append(Spacer(1, 30))
        elements.append(signature_table)
        
        # Build PDF document
        doc.build(elements)
        
        # Get PDF from buffer
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf
        
    except Exception as e:
        logger.error(f"PDF generation failed for document {document.id}: {str(e)}")
        raise

def get_document_filename(document):
    """
    Generate a clean filename for the document.
    """
    safe_title = "".join([c for c in document.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    date_str = document.date.strftime('%Y%m%d')
    return f"{safe_title}_{date_str}.pdf"

def can_user_view_document(user, document):
    """
    Check if user has permission to view the document.
    """
    return (
        user.is_staff or
        document.created_by == user or
        (document.status == 'accepted' and document.accepted_by is not None)
    )

def can_user_print_document(user, document):
    """
    Check if user has permission to print the document.
    """
    return (
        user.is_staff or
        (document.created_by == user and document.status == 'accepted')
    )

def can_user_edit_document(user, document):
    """
    Check if user has permission to edit the document.
    """
    return (
        document.created_by == user and
        document.status != 'accepted'
    )

def validate_document_data(data):
    """
    Validate document data before saving.
    """
    errors = {}
    
    required_fields = ['title', 'office_name', 'date', 'receiver', 'description']
    for field in required_fields:
        if not data.get(field):
            errors[field] = 'This field is required.'
    
    if len(data.get('title', '')) > 255:
        errors['title'] = 'Title must be less than 255 characters.'

    if errors:
        raise ValidationError(errors)

def get_document_statistics(user=None):
    """
    Get document statistics, optionally filtered by user.
    """
    from .models import PDFDocument
    
    queryset = PDFDocument.objects.all()
    if user and not user.is_staff:
        queryset = queryset.filter(created_by=user)
    
    return {
        'total': queryset.count(),
        'pending': queryset.filter(status='pending').count(),
        'accepted': queryset.filter(status='accepted').count(),
        'rejected': queryset.filter(status='rejected').count(),
    }

def send_document_notification(document, action):
    """
    Send email notification about document status changes.
    """
    from django.core.mail import send_mail
    
    subject = f'Document {document.title} has been {action}'
    context = {
        'document': document,
        'action': action,
        'date': datetime.now()
    }
    
    html_message = render_to_string('pdf_app/email/notification.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [document.created_by.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")