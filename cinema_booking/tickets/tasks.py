from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Ticket, Transaction

@shared_task
def delete_unpaid_tickets():
    # Lấy thời gian 20 phút trước
    twenty_minutes_ago = timezone.now() - timedelta(minutes=20)
    
    # Tìm các ticket chưa thanh toán và đã tạo hơn 20 phút
    unpaid_tickets = Ticket.objects.filter(
        status='pending',
        purchase_date__lte=twenty_minutes_ago
    )
    
    # Xóa các transaction liên quan và ticket
    for ticket in unpaid_tickets:
        # Xóa transaction nếu có
        try:
            transaction = Transaction.objects.get(ticket=ticket)
            transaction.delete()
        except Transaction.DoesNotExist:
            pass
        
        # Xóa ticket
        ticket.delete()
    
    return f"Đã xóa {unpaid_tickets.count()} ticket chưa thanh toán" 