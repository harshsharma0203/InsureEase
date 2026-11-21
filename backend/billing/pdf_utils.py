import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_invoice_pdf(invoice):
    """Generates official tax invoice PDF for group insurance policy premiums."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0c406d')
    )
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#03599e'),
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    bold_style = ParagraphStyle('BoldBody', parent=body_style, fontName='Helvetica-Bold')

    elements = []

    # Header
    elements.append(Paragraph("InsureEase Insurance Solutions Ltd.", header_style))
    elements.append(Paragraph("GST Registered Corporate Tax Invoice", sub_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0270c3'), spaceAfter=15))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Invoice Number:</b>", body_style), Paragraph(invoice.invoice_number, bold_style),
         Paragraph("<b>Status:</b>", body_style), Paragraph(invoice.get_status_display(), bold_style)],
        [Paragraph("<b>Invoice Date:</b>", body_style), Paragraph(str(invoice.invoice_date), body_style),
         Paragraph("<b>Due Date:</b>", body_style), Paragraph(str(invoice.due_date), bold_style)],
        [Paragraph("<b>Policy Number:</b>", body_style), Paragraph(invoice.policy.policy_number, body_style),
         Paragraph("<b>Product:</b>", body_style), Paragraph(invoice.policy.product.name, body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[120, 160, 100, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 15))

    # Billed To
    group = invoice.group
    elements.append(Paragraph("BILLED TO (INSURED CORPORATE CLIENT):", section_title))
    billed_data = [
        [Paragraph("<b>Organization:</b>", body_style), Paragraph(group.name, bold_style)],
        [Paragraph("<b>Group Code & Reg:</b>", body_style), Paragraph(f"{group.group_code} | {group.registration_number}", body_style)],
        [Paragraph("<b>Contact Official:</b>", body_style), Paragraph(f"{group.contact_person} ({group.contact_email})", body_style)],
        [Paragraph("<b>Billing Address:</b>", body_style), Paragraph(f"{group.address}, {group.city}, {group.state} - {group.pincode}", body_style)],
    ]
    billed_table = Table(billed_data, colWidths=[140, 400])
    billed_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(billed_table)
    elements.append(Spacer(1, 15))

    # Item breakdown
    elements.append(Paragraph("PREMIUM BREAKDOWN & TAX SCHEDULE:", section_title))
    items_data = [
        [Paragraph("<b>Description / Coverage Details</b>", bold_style), Paragraph("<b>Rate</b>", bold_style), Paragraph("<b>Amount (INR)</b>", bold_style)],
        [Paragraph(f"Annual Group Insurance Premium ({invoice.policy.product.name}) - {invoice.policy.total_members_covered} Enrolled Lives", body_style), Paragraph("Base", body_style), Paragraph(f"INR {invoice.subtotal_amount:,.2f}", body_style)],
        [Paragraph(f"Integrated Goods and Services Tax (GST @ {invoice.tax_rate_percentage}%)", body_style), Paragraph(f"{invoice.tax_rate_percentage}%", body_style), Paragraph(f"INR {invoice.tax_amount:,.2f}", body_style)],
        [Paragraph("<b>TOTAL INVOICE AMOUNT</b>", bold_style), Paragraph("-", body_style), Paragraph(f"<b>INR {invoice.total_amount:,.2f}</b>", bold_style)],
        [Paragraph("Total Amount Received / Paid", body_style), Paragraph("-", body_style), Paragraph(f"INR {invoice.paid_amount:,.2f}", body_style)],
        [Paragraph("<b>NET OUTSTANDING BALANCE DUE</b>", bold_style), Paragraph("-", body_style), Paragraph(f"<b>INR {invoice.balance_due:,.2f}</b>", bold_style)],
    ]
    items_table = Table(items_data, colWidths=[340, 80, 120])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0effe')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f1f5f9')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#fee2e2') if invoice.balance_due > 0 else colors.HexColor('#dcfce7')),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))

    # Payment advice
    elements.append(Paragraph("BANK WIRE PAYMENT INSTRUCTIONS:", section_title))
    bank_text = (
        "Beneficiary: InsureEase General Insurance Ltd. | Account: 50200084920194 | Bank: HDFC Bank Ltd. | IFSC: HDFC0000128 | Branch: Mumbai Main"
    )
    elements.append(Paragraph(bank_text, body_style))
    elements.append(Spacer(1, 20))

    # Signature
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    sig_data = [
        [Paragraph("This is a computer-generated tax invoice and requires no physical signature.<br/>Authorized Signatory - InsureEase Finance Desk", body_style),
         Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[400, 140])
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
