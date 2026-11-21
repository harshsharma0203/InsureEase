import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_claim_settlement_pdf(claim):
    """Generates official claim settlement voucher / letter PDF."""
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
        fontSize=18,
        leading=22,
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
    bold_style = ParagraphStyle('BoldBody', parent=body_style, fontName='Helvetica-Bold')

    elements = []

    # Header
    elements.append(Paragraph("InsureEase Claims Settlement Division", header_style))
    elements.append(Paragraph("Official Claim Discharge & Settlement Advice", sub_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0270c3'), spaceAfter=15))

    # Settlement Summary
    settlement = getattr(claim, 'settlement', None)
    settle_amt = settlement.settlement_amount if settlement else claim.approved_amount
    settle_date = settlement.settlement_date if settlement else claim.settlement_date or datetime.today().date()
    tx_id = settlement.bank_transaction_id if settlement else claim.payment_reference or "N/A"
    mode = settlement.get_payment_mode_display() if settlement else "Electronic Fund Transfer"

    summary_data = [
        [Paragraph("<b>Claim Number:</b>", body_style), Paragraph(claim.claim_number, bold_style),
         Paragraph("<b>Settlement Status:</b>", body_style), Paragraph(claim.get_status_display(), bold_style)],
        [Paragraph("<b>Policy Number:</b>", body_style), Paragraph(claim.policy.policy_number, body_style),
         Paragraph("<b>Claim Type:</b>", body_style), Paragraph(claim.get_claim_type_display(), body_style)],
        [Paragraph("<b>Insured Member:</b>", body_style), Paragraph(f"{claim.member.full_name} ({claim.member.employee_id})", bold_style),
         Paragraph("<b>Employer / Group:</b>", body_style), Paragraph(claim.policy.group.name, body_style)],
        [Paragraph("<b>Incident Date:</b>", body_style), Paragraph(str(claim.incident_date), body_style),
         Paragraph("<b>Hospital / Provider:</b>", body_style), Paragraph(claim.hospital_name or "Network Hospital", body_style)],
    ]
    summary_table = Table(summary_data, colWidths=[120, 160, 110, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # Payout details
    elements.append(Paragraph("SETTLEMENT & PAYMENT ADVICE", section_title))
    payout_data = [
        [Paragraph("<b>Description</b>", bold_style), Paragraph("<b>Amount (INR)</b>", bold_style)],
        [Paragraph("Claim Amount Billed", body_style), Paragraph(f"INR {claim.claim_amount:,.2f}", body_style)],
        [Paragraph("Deductibles / Co-payment / Non-admissible Items", body_style), Paragraph(f"INR {(claim.claim_amount - settle_amt):,.2f}", body_style)],
        [Paragraph("<b>Net Approved Settlement Amount</b>", bold_style), Paragraph(f"<b>INR {settle_amt:,.2f}</b>", bold_style)],
        [Paragraph("Payment Mode / Channel", body_style), Paragraph(mode, body_style)],
        [Paragraph("Bank UTR / Transaction Reference", body_style), Paragraph(tx_id, bold_style)],
        [Paragraph("Disbursement Date", body_style), Paragraph(str(settle_date), body_style)],
    ]
    payout_table = Table(payout_data, colWidths=[330, 210])
    payout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dcfce7')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#86efac')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bbf7d0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f0fdf4')),
    ]))
    elements.append(payout_table)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("VERIFICATION & MEDICAL ASSESSMENT NOTES", section_title))
    notes = claim.verification_remarks or claim.diagnosis or "The claim documentation has been duly evaluated by the medical adjudicator panel and approved in accordance with policy terms."
    elements.append(Paragraph(notes, body_style))
    elements.append(Spacer(1, 20))

    # Footer
    sig_data = [
        [Paragraph("<b>Claims Adjudicator Officer</b><br/>InsureEase TPA Claims Desk", body_style),
         Paragraph("<b>Authorized Finance Signatory</b><br/>Disbursement Accounts Team", body_style),
         Paragraph("<b>Settlement Status</b><br/>ELECTRONICALLY PROCESSED", bold_style)]
    ]
    sig_table = Table(sig_data, colWidths=[180, 180, 180])
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
