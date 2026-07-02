"""
PDF Invoice Generator
Generates professional PDF receipts using ReportLab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO


def generate_invoice_pdf(order):
    """
    Generate a PDF invoice for an order.

    Args:
        order: Dictionary containing order details

    Returns:
        bytes: PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=5,
        spaceAfter=5
    )

    # Restaurant Header
    elements.append(Paragraph("CloudCuisine", title_style))
    elements.append(Paragraph("Cloud-Based Restaurant Management System", subtitle_style))
    elements.append(Paragraph("123 Restaurant Street, Food City, FC 12345", subtitle_style))
    elements.append(Paragraph("Phone: (555) 123-4567 | Email: info@cloudcuisine.com", subtitle_style))
    elements.append(Spacer(1, 20))

    # Divider line
    line_data = [['-' * 80]]
    line_table = Table(line_data, colWidths=[7*inch])
    line_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#bdc3c7')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 20))

    # Invoice Info
    invoice_info = [
        ['INVOICE', f'#{order["id"]}'],
        ['Date:', format_datetime(order.get('created_at'))],
        ['Status:', order['status'].upper()],
        ['Payment Method:', order.get('payment_method', 'Cash').upper()]
    ]

    info_table = Table(invoice_info, colWidths=[3.5*inch, 3.5*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#7f8c8d')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    # Customer Details
    elements.append(Paragraph("Customer Details", header_style))
    customer_info = [
        ['Name:', order.get('username', 'N/A')],
        ['Email:', order.get('email', 'N/A')],
        ['Phone:', order.get('phone', 'N/A')],
        ['Delivery Address:', order.get('delivery_address', 'N/A')]
    ]

    customer_table = Table(customer_info, colWidths=[1.5*inch, 5.5*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#7f8c8d')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 20))

    # Order Items Table
    elements.append(Paragraph("Order Items", header_style))

    # Table header
    item_data = [['Item', 'Quantity', 'Price', 'Subtotal']]

    # Table rows
    for item in order.get('items', []):
        item_data.append([
            item.get('item_name', 'Unknown'),
            str(item.get('quantity', 0)),
            f"${item.get('price_per_item', 0):.2f}",
            f"${item.get('subtotal', 0):.2f}"
        ])

    items_table = Table(item_data, colWidths=[3.5*inch, 1*inch, 1.25*inch, 1.25*inch])
    items_table.setStyle(TableStyle([
        # Header style
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        # Body style
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
        # Alignment
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        # Grid
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#3498db')),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))

    # Order Summary
    elements.append(Paragraph("Order Summary", header_style))

    summary_data = [
        ['', 'Subtotal:', f"${order.get('total_amount', 0):.2f}"],
        ['', 'GST (18%):', f"${order.get('gst_amount', 0):.2f}"],
        ['', 'Service Charge (5%):', f"${order.get('service_charge', 0):.2f}"],
        ['', 'Discount:', f"-${order.get('discount', 0):.2f}"],
        ['', '', ''],
        ['', 'Grand Total:', f"${order.get('grand_total', 0):.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[3.5*inch, 2*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -3), colors.HexColor('#7f8c8d')),
        ('TEXTCOLOR', (1, 5), (-1, 5), colors.HexColor('#2c3e50')),
        ('FONTNAME', (1, 5), (-1, 5), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 5), (-1, 5), 12),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        # Line above grand total
        ('LINEABOVE', (1, 5), (-1, 5), 1, colors.HexColor('#2c3e50')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))

    # Special Instructions
    if order.get('special_instructions'):
        elements.append(Paragraph("Special Instructions", header_style))
        elements.append(Paragraph(order['special_instructions'], normal_style))
        elements.append(Spacer(1, 20))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#95a5a6')
    )

    elements.append(Paragraph("Thank you for dining with us!", footer_style))
    elements.append(Paragraph("Visit us at www.cloudcuisine.com | Follow us @CloudCuisine", footer_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))

    # Build PDF
    doc.build(elements)

    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


def format_datetime(dt_value):
    """Format datetime value for display."""
    if isinstance(dt_value, str):
        try:
            from datetime import datetime
            dt_value = datetime.strptime(dt_value, '%Y-%m-%d %H:%M:%S')
        except:
            return dt_value
    if isinstance(dt_value, datetime):
        return dt_value.strftime('%B %d, %Y at %I:%M %p')
    return str(dt_value)


def generate_sales_report(report_data, start_date, end_date):
    """
    Generate a sales report PDF.

    Args:
        report_data: List of daily sales data
        start_date: Report start date
        end_date: Report end date

    Returns:
        bytes: PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20
    )

    elements.append(Paragraph("CloudCuisine Sales Report", title_style))
    elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Sales Table
    sales_data = [['Date', 'Orders', 'Revenue', 'GST', 'Total']]

    for row in report_data:
        sale_date = row.get('sale_date', 'N/A')
        order_count = row.get('order_count', 0)
        total_revenue = float(row.get('total_revenue', 0))
        total_gst = float(row.get('total_gst', 0))
        subtotal = float(row.get('subtotal', 0))

        sales_data.append([
            str(sale_date),
            str(order_count),
            f"${subtotal:.2f}",
            f"${total_gst:.2f}",
            f"${total_revenue:.2f}"
        ])

    # Totals row
    total_orders = sum(row.get('order_count', 0) for row in report_data)
    total_revenue = sum(float(row.get('total_revenue', 0)) for row in report_data)
    total_gst = sum(float(row.get('total_gst', 0)) for row in report_data)
    total_subtotal = sum(float(row.get('subtotal', 0)) for row in report_data)

    sales_data.append(['TOTALS', str(total_orders), f"${total_subtotal:.2f}", f"${total_gst:.2f}", f"${total_revenue:.2f}"])

    sales_table = Table(sales_data, colWidths=[1.5*inch, 1*inch, 1.25*inch, 1.25*inch, 1.25*inch])
    sales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#3498db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(sales_table)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data
