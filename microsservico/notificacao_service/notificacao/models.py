from django.db import models

# Create your models here.

class Notification(models.Model):
    # Loose reference to the order (no foreign key - separate service/database)
    order_id = models.IntegerField()
    message = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='SENT')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
