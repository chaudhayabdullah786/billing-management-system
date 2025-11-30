from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=10*mm
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=5*mm
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=3*mm
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10
    )
    
    right_style = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT
    )
    
    elements = []
    
    elements.append(Paragraph("GROCERY STORE", title_style))
    elements.append(Paragraph("Your Trusted Shopping Partner", subtitle_style))
    elements.append(Paragraph("123 Main Street, Karachi, Pakistan | Phone: +92 21 1234567", subtitle_style))
    elements.append(Spacer(1, 5*mm))
    
    elements.append(Paragraph("TAX INVOICE", ParagraphStyle('InvTitle', parent=styles['Heading2'], fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor('#2563eb'))))
    elements.append(Spacer(1, 5*mm))
    
    invoice_info = [
        ['Invoice Number:', invoice.invoice_number, 'Date:', invoice.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Customer:', invoice.customer.name if invoice.customer else 'Walk-in Customer', 'Mobile:', invoice.customer.mobile if invoice.customer else 'N/A'],
    ]
    
    info_table = Table(invoice_info, colWidths=[30*mm, 55*mm, 25*mm, 55*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))
    
    items_data = [['#', 'Product', 'Qty', 'Unit Price', 'Total']]
    for idx, item in enumerate(invoice.items, 1):
        items_data.append([
            str(idx),
            item.product_name,
            str(item.quantity),
            f"Rs. {float(item.unit_price):,.2f}",
            f"Rs. {float(item.total_price):,.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[10*mm, 85*mm, 20*mm, 30*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 5*mm))
    
    totals_data = [
        ['', '', '', 'Subtotal:', f"Rs. {float(invoice.subtotal):,.2f}"],
        ['', '', '', f'Tax ({float(invoice.tax_rate)}%):', f"Rs. {float(invoice.tax_amount):,.2f}"],
    ]
    
    if invoice.discount_amount > 0:
        totals_data.append(['', '', '', f'Discount ({float(invoice.discount_percent)}%):', f"-Rs. {float(invoice.discount_amount):,.2f}"])
    
    totals_data.append(['', '', '', 'TOTAL:', f"Rs. {float(invoice.total_amount):,.2f}"])
    
    totals_table = Table(totals_data, colWidths=[10*mm, 85*mm, 20*mm, 30*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, -1), (-1, -1), 12),
        ('LINEABOVE', (3, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 8*mm))
    
    payment_info = [
        ['Payment Method:', invoice.payment_method.upper()],
        ['Payment Status:', invoice.payment_status.upper()],
    ]
    
    if invoice.notes:
        payment_info.append(['Notes:', invoice.notes])
    
    payment_table = Table(payment_info, colWidths=[35*mm, 130*mm])
    payment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
    ]))
    elements.append(payment_table)
    elements.append(Spacer(1, 10*mm))
    
    elements.append(Paragraph("Thank you for shopping with us!", ParagraphStyle('Thanks', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#2563eb'))))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Please retain this invoice for your records.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
