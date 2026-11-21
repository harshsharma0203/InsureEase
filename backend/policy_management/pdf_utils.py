import io
from datetime import datetime
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_policy_pdf_stream(policy):
    """Generates a professional PDF Policy Schedule document using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
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
        fontSize=12,
        leading=16,
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
    bold_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    elements = []

    # Header
    elements.append(Paragraph("InsureEase – InsureGroup Management Platform", header_style))
    elements.append(Paragraph("Official Group Insurance Policy Schedule & Certificate of Coverage", sub_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0270c3'), spaceAfter=15))

    # Summary Meta Table
    meta_data = [
        [Paragraph("<b>Policy Number:</b>", body_style), Paragraph(policy.policy_number, bold_style),
         Paragraph("<b>Status:</b>", body_style), Paragraph(policy.get_status_display(), bold_style)],
        [Paragraph("<b>Insurance Product:</b>", body_style), Paragraph(policy.product.name, body_style),
         Paragraph("<b>Coverage Type:</b>", body_style), Paragraph(policy.product.get_coverage_type_display(), body_style)],
        [Paragraph("<b>Inception Date:</b>", body_style), Paragraph(str(policy.start_date), body_style),
         Paragraph("<b>Expiry Date:</b>", body_style), Paragraph(str(policy.expiry_date), body_style)],
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

    # Insured Group Information
    elements.append(Paragraph("1. INSURED GROUP & EMPLOYER DETAILS", section_title))
    group = policy.group
    group_data = [
        [Paragraph("<b>Organization Name:</b>", body_style), Paragraph(group.name, bold_style)],
        [Paragraph("<b>Group Reference Code:</b>", body_style), Paragraph(group.group_code, body_style)],
        [Paragraph("<b>Registration / CIN:</b>", body_style), Paragraph(group.registration_number, body_style)],
        [Paragraph("<b>Industry Sector:</b>", body_style), Paragraph(group.industry, body_style)],
        [Paragraph("<b>Contact Official:</b>", body_style), Paragraph(f"{group.contact_person} ({group.contact_email}, {group.contact_phone})", body_style)],
        [Paragraph("<b>Registered Address:</b>", body_style), Paragraph(f"{group.address}, {group.city}, {group.state} - {group.pincode}", body_style)],
    ]
    group_table = Table(group_data, colWidths=[160, 380])
    group_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
    ]))
    elements.append(group_table)
    elements.append(Spacer(1, 15))

    # Coverage & Financial Schedule
    elements.append(Paragraph("2. COVERAGE SCHEDULE & FINANCIAL SUMMARY", section_title))
    fin_data = [
        [Paragraph("<b>Item Description</b>", bold_style), Paragraph("<b>Details / Value</b>", bold_style)],
        [Paragraph("Total Insured Lives (Members)", body_style), Paragraph(str(policy.total_members_covered), body_style)],
        [Paragraph("Sum Insured per Enrolled Member", body_style), Paragraph(f"INR {policy.sum_insured_per_member:,.2f}", body_style)],
        [Paragraph("Total Aggregate Sum Insured", body_style), Paragraph(f"INR {policy.total_sum_insured:,.2f}", bold_style)],
        [Paragraph("Annual Base Premium", body_style), Paragraph(f"INR {policy.base_annual_premium:,.2f}", body_style)],
        [Paragraph("Applicable Goods & Services Tax (18% GST)", body_style), Paragraph(f"INR {policy.tax_amount:,.2f}", body_style)],
        [Paragraph("<b>Total Premium Payable</b>", bold_style), Paragraph(f"<b>INR {policy.total_premium:,.2f}</b>", bold_style)],
    ]
    fin_table = Table(fin_data, colWidths=[320, 220])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0effe')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dbeafe')),
    ]))
    elements.append(fin_table)
    elements.append(Spacer(1, 15))

    # Terms and Underwriting endorsement
    elements.append(Paragraph("3. TERMS & REGULATORY DECLARATION", section_title))
    terms_text = policy.terms_and_conditions or (
        "This Group Policy Certificate is issued in conformity with standard group underwriting regulations. "
        "Coverage is strictly effective for registered active members during the policy term. "
        "All claims must be submitted within 30 days of the incident date accompanied by valid hospital discharge and expense documentation."
    )
    elements.append(Paragraph(terms_text, body_style))
    elements.append(Spacer(1, 20))

    # Signatures
    sig_data = [
        [Paragraph("<b>Authorized Underwriting Officer</b><br/>InsureEase Underwriting Operations", body_style),
         Paragraph(f"<b>Generated On:</b><br/>{datetime.now().strftime('%d %B %Y, %I:%M %p')}", body_style),
         Paragraph("<b>Digital Signature Stamp</b><br/>VERIFIED & ISSUED", bold_style)]
    ]
    sig_table = Table(sig_data, colWidths=[200, 180, 160])
    sig_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
