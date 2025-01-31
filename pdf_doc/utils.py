try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from io import BytesIO
    from django.conf import settings
    import os
except ImportError as e:
    raise ImportError(f"Required package 'reportlab' is missing. Please install it using: pip install reportlab\nError: {e}")

def generate_pdf(document):
    try:
        buffer = BytesIO()
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
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12
        )

        # Add the content
        elements.append(Paragraph(document.title, title_style))
        elements.append(Spacer(1, 12))

        # Document info table
        data = [
            ['Office:', document.office_name],
            ['Date:', document.date.strftime('%Y-%m-%d')],
            ['Receiver:', document.receiver],
        ]
        
        info_table = Table(data, colWidths=[100, 400])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Main content sections
        sections = [
            ('Description', document.description),
            ('Summary', document.summary),
            ('Object', document.object)
        ]

        for section_title, content in sections:
            elements.append(Paragraph(section_title, header_style))
            elements.append(Paragraph(content, normal_style))
            elements.append(Spacer(1, 20))

        # Status information
        if document.is_accepted:
            elements.append(Paragraph('Status: Accepted', header_style))
            if document.accept_by:
                elements.append(Paragraph(
                    f'Accepted by: {document.accept_by.get_full_name() or document.accept_by.username}',
                    normal_style
                ))
                elements.append(Paragraph(
                    f'Accepted on: {document.updated_datetime.strftime("%Y-%m-%d %H:%M")}',
                    normal_style
                ))
        else:
            elements.append(Paragraph('Status: Pending Review', header_style))

        # Build the PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        return pdf
    
    except Exception as e:
        # Log the error (you should configure proper logging)
        print(f"Error generating PDF: {str(e)}")
        raise