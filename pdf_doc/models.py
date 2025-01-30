from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    office_name = models.CharField(max_length=255)
    date = models.DateField()
    receiver = models.CharField(max_length=255)
    description = models.TextField()
    summary = models.TextField()
    object = models.TextField()
    
    # User Relations
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='created_documents'
    )
    accepted_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,
        related_name='accepted_documents',
        null=True,
        blank=True
    )
    
    # Status and Result
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    result = models.TextField(blank=True)
    
    # Timestamps
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_datetime']
        permissions = [
            ("can_accept_documents", "Can accept documents"),
            ("can_view_all_documents", "Can view all documents"),
        ]
    
    def clean(self):
        if self.status in ['accepted', 'rejected'] and not self.result:
            raise ValidationError({
                'result': 'Result is required when accepting or rejecting a document'
            })
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.created_by.username} - {self.status}"