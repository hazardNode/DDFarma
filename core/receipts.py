# core/receipts.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.http import HttpResponse
from decimal import Decimal
from .models import Order, Receipt
import zipfile
from django.utils import timezone
from datetime import datetime


def generate_receipt_pdf(receipt):
    """Generate a PDF receipt"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Company info
    p.setFont("Helvetica-Bold", 14)
    p.drawString(inch, height - inch, "Your Company Name")
    p.setFont("Helvetica", 10)
    p.drawString(inch, height - 1.2 * inch, "Company Address Line 1")
    p.drawString(inch, height - 1.4 * inch, "City, Province, Postal Code")
    p.drawString(inch, height - 1.6 * inch, "Tax ID: 123456789")

    # Receipt header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(width - 3 * inch, height - inch, "RECEIPT")
    p.setFont("Helvetica", 10)
    p.drawString(width - 3 * inch, height - 1.2 * inch, f"Receipt #: {receipt.receipt_number}")
    p.drawString(width - 3 * inch, height - 1.4 * inch, f"Date: {receipt.issue_date.strftime('%Y-%m-%d')}")
    p.drawString(width - 3 * inch, height - 1.6 * inch, f"Order #: {receipt.order.id}")

    # Customer info
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, height - 2.5 * inch, "Billed To:")
    p.setFont("Helvetica", 10)
    p.drawString(inch, height - 2.7 * inch, receipt.billing_name)
    p.drawString(inch, height - 2.9 * inch, receipt.billing_address)
    p.drawString(inch, height - 3.1 * inch,
                 f"{receipt.billing_city}, {receipt.billing_province} {receipt.billing_postal_code}")

    # Order items
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, height - 4 * inch, "Items:")

    y_position = height - 4.3 * inch
    p.setFont("Helvetica-Bold", 10)
    p.drawString(inch, y_position, "Product")
    p.drawString(width - 3 * inch, y_position, "Quantity")
    p.drawString(width - 2 * inch, y_position, "Price")
    p.drawString(width - 1.2 * inch, y_position, "Subtotal")

    p.line(inch, y_position - 0.1 * inch, width - inch, y_position - 0.1 * inch)

    y_position -= 0.3 * inch
    p.setFont("Helvetica", 10)

    for item in receipt.order.items.all():
        p.drawString(inch, y_position, item.product.name[:30])
        p.drawString(width - 3 * inch, y_position, str(item.quantity))
        p.drawString(width - 2 * inch, y_position, f"${item.price_at_purchase}")
        subtotal = item.quantity * item.price_at_purchase
        p.drawString(width - 1.2 * inch, y_position, f"${subtotal}")
        y_position -= 0.2 * inch

    # Summary
    y_position = max(y_position, height - 7 * inch)  # Ensure we have space
    p.line(inch, y_position - 0.1 * inch, width - inch, y_position - 0.1 * inch)
    y_position -= 0.3 * inch

    p.drawString(width - 3 * inch, y_position, "Subtotal:")
    p.drawString(width - 1.2 * inch, y_position, f"${receipt.subtotal}")
    y_position -= 0.2 * inch

    p.drawString(width - 3 * inch, y_position, "Shipping:")
    p.drawString(width - 1.2 * inch, y_position, f"${receipt.shipping_cost}")
    y_position -= 0.2 * inch

    p.drawString(width - 3 * inch, y_position, "Tax:")
    p.drawString(width - 1.2 * inch, y_position, f"${receipt.tax_amount}")
    y_position -= 0.2 * inch

    p.setFont("Helvetica-Bold", 10)
    p.drawString(width - 3 * inch, y_position, "Total:")
    p.drawString(width - 1.2 * inch, y_position, f"${receipt.total_amount}")

    # Payment info
    y_position -= 0.5 * inch
    p.setFont("Helvetica", 10)
    p.drawString(inch, y_position, f"Payment Method: {receipt.payment_method}")
    if receipt.payment_transaction_id:
        y_position -= 0.2 * inch
        p.drawString(inch, y_position, f"Transaction ID: {receipt.payment_transaction_id}")

    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(inch, inch, "This is an official receipt for tax purposes.")
    p.drawString(inch, 0.8 * inch, "Thank you for your business!")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


def download_receipt(request, order_id):
    """Generate and return a PDF receipt for download"""
    try:
        # Check if user is admin or the order owner
        order = Order.objects.get(id=order_id)
        if not request.user.is_staff and request.user != order.user:
            return HttpResponse("Unauthorized", status=403)

        # Get or create receipt
        receipt, created = Receipt.objects.get_or_create(
            order=order,
            defaults={
                'subtotal': sum(item.price_at_purchase * item.quantity for item in order.items.all()),
                'tax_amount': order.total_amount * Decimal('0.1'),  # Assuming 10% tax, adjust as needed
                'shipping_cost': order.shipping_method.cost,
                'total_amount': order.total_amount,
                'billing_name': f"{order.user.first_name} {order.user.last_name}",
                'billing_address': order.shipping_address.street,
                'billing_city': order.shipping_address.city,
                'billing_province': order.shipping_address.province,
                'billing_postal_code': order.shipping_address.postal_code,
                'payment_method': order.payment_set.first().payment_method if order.payment_set.exists() else "Unknown",
                'payment_transaction_id': order.payment_set.first().transaction_id if order.payment_set.exists() else None,
            }
        )

        buffer = generate_receipt_pdf(receipt)

        # Create HTTP response with PDF
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
        return response

    except Order.DoesNotExist:
        return HttpResponse("Order not found", status=404)


# Add to core/receipts.py
# core/receipts.py - Fixed bulk_download_receipts function
def bulk_download_receipts(request):
    """Download multiple receipts as a ZIP file"""
    if request.user.role == "ADMIN":
        return HttpResponse("Unauthorized", status=403)

    # Get parameters
    all_orders = request.GET.get('all') == 'true'
    start_date = None
    end_date = None

    # Handle date parsing more safely
    try:
        start_date_str = request.GET.get('start_date', '').strip()
        end_date_str = request.GET.get('end_date', '').strip()

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    except ValueError as e:
        return HttpResponse(f"Invalid date format: {str(e)}", status=400)

    # Query orders with better logic
    orders = Order.objects.all()

    if all_orders:
        # Download all orders
        pass  # orders already contains all orders
    elif start_date and end_date:
        # Filter by date range
        orders = orders.filter(order_date__date__range=[start_date, end_date])
    elif start_date:
        # Filter from start_date onwards
        orders = orders.filter(order_date__date__gte=start_date)
    elif end_date:
        # Filter up to end_date
        orders = orders.filter(order_date__date__lte=end_date)
    else:
        # If no criteria provided and not "all", return error
        return HttpResponse("Please select 'All Orders' or provide date range", status=400)

    if not orders.exists():
        return HttpResponse("No orders found for the selected criteria", status=404)

    # Create a ZIP file in memory
    buffer = BytesIO()
    try:
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            for order in orders:
                try:
                    # Calculate subtotal properly
                    subtotal = sum(item.price_at_purchase * item.quantity for item in order.items.all())

                    # Get payment method info correctly
                    payment_method_name = "Unknown"
                    payment_transaction_id = None

                    # Try to get payment method from the order's payment_method field
                    if order.payment_method:
                        payment_method_name = order.payment_method.display_name

                    # Try to get transaction ID from related Payment objects
                    payment_obj = order.payment_set.first() if hasattr(order, 'payment_set') else None
                    if payment_obj:
                        payment_transaction_id = payment_obj.transaction_id
                    elif order.stripe_payment_intent_id:
                        payment_transaction_id = order.stripe_payment_intent_id

                    # Get shipping cost
                    shipping_cost = order.shipping_cost if order.shipping_cost else Decimal('0.00')

                    # Calculate tax (you may want to adjust this logic)
                    tax_amount = order.total_amount - subtotal - shipping_cost
                    if tax_amount < 0:
                        tax_amount = Decimal('0.00')

                    # Get or create receipt
                    receipt, created = Receipt.objects.get_or_create(
                        order=order,
                        defaults={
                            'subtotal': subtotal,
                            'tax_amount': tax_amount,
                            'shipping_cost': shipping_cost,
                            'total_amount': order.total_amount,
                            'billing_name': f"{order.user.first_name} {order.user.last_name}".strip() or order.user.email,
                            'billing_address': order.billing_address.street if order.billing_address else order.shipping_address.street,
                            'billing_city': order.billing_address.city if order.billing_address else order.shipping_address.city,
                            'billing_province': order.billing_address.province if order.billing_address else order.shipping_address.province,
                            'billing_postal_code': order.billing_address.postal_code if order.billing_address else order.shipping_address.postal_code,
                            'payment_method': payment_method_name,
                            'payment_transaction_id': payment_transaction_id,
                        }
                    )

                    # Generate PDF
                    pdf_buffer = generate_receipt_pdf(receipt)

                    # Add to ZIP with a safe filename
                    safe_filename = f"receipt_order_{order.id}_{receipt.receipt_number}.pdf"
                    zip_file.writestr(safe_filename, pdf_buffer.getvalue())

                except Exception as e:
                    # Log the error but continue processing other orders
                    print(f"Error processing order {order.id}: {str(e)}")
                    continue

    except Exception as e:
        return HttpResponse(f"Error creating ZIP file: {str(e)}", status=500)

    # Return ZIP file
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="receipts_{timestamp}.zip"'
    return response