from django.db import models

# Create your models here.

class PaymentTransaction(models.Model):
    # Loose reference to the order (no foreign key - separate service/database)
    order_id = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, default='PENDING')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_transactions'
