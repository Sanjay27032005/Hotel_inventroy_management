from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

HOTEL_NAME = "CoreStone Grand"
HOTEL_ADDRESS = "ECR Road, Puducherry, Tamil Nadu, India"
HOTEL_CONTACT = "+91 90000 00000 · reservations@corestone-hrm.com"


def build_invoice_pdf(invoice, customer, items) -> bytes:
    """Renders a printable invoice matching the field layout specified across
    Sections 15 (Restaurant), 21 (Accommodation), and 63 (common Invoice Types) of the
    requirement document: hotel name/address, invoice number, date, customer, booking
    reference, line items, subtotal/discount/tax/additional charges/grand total, and
    payment method/status.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    right_style = ParagraphStyle("right", parent=styles["Normal"], alignment=TA_RIGHT)

    elements = []

    elements.append(Paragraph(f"<b>{HOTEL_NAME}</b>", styles["Title"]))
    elements.append(Paragraph(HOTEL_ADDRESS, styles["Normal"]))
    elements.append(Paragraph(HOTEL_CONTACT, styles["Normal"]))
    elements.append(Spacer(1, 12))

    header_table = Table([
        ["Invoice Number:", invoice.invoice_number, "Date:", invoice.created_at.strftime("%d-%b-%Y")],
        ["Booking ID:", invoice.booking_code or "-", "Service:", invoice.service_type.value.replace("_", " ").title()],
        ["Customer:", f"{customer.first_name} {customer.last_name}" if customer else "-",
         "Customer ID:", customer.customer_code if customer else "-"],
    ], colWidths=[80, 160, 70, 160])
    header_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 16))

    item_rows = [["Description", "Qty", "Rate", "Amount"]]
    for it in items:
        item_rows.append([it.description, f"{it.quantity:g}", f"₹{float(it.rate):.2f}", f"₹{float(it.amount):.2f}"])

    items_table = Table(item_rows, colWidths=[260, 60, 80, 90])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A2F29")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3EFE6")]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 16))

    totals_rows = [
        ["Subtotal", f"₹{float(invoice.subtotal):.2f}"],
        ["Discount", f"-₹{float(invoice.discount):.2f}"],
        ["Tax", f"+₹{float(invoice.tax):.2f}"],
    ]
    if invoice.additional_charges:
        totals_rows.append(["Additional Charges", f"+₹{float(invoice.additional_charges):.2f}"])
    totals_rows.append(["Grand Total", f"₹{float(invoice.grand_total):.2f}"])

    totals_table = Table(totals_rows, colWidths=[400, 90])
    totals_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, -1), (-1, -1), 11),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1A2F29")),
        ("TOPPADDING", (0, -1), (-1, -1), 6),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 16))

    payment_method = invoice.payment_method.value.replace("_", " ").title() if invoice.payment_method else "Not yet recorded"
    elements.append(Paragraph(f"<b>Payment Method:</b> {payment_method}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Payment Status:</b> {invoice.payment_status.value.replace('_', ' ').title()}", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for staying with us.", styles["Italic"]))

    doc.build(elements)
    return buffer.getvalue()
