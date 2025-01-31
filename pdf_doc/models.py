from django.db import models
#from django.contrib.auth.models import User
from authentication.models import CustomUser as User
from django.utils import timezone
from django.core.exceptions import ValidationError

class Document(models.Model):
    title = models.CharField(max_length=255)
    office_name = models.CharField(max_length=255)
    date = models.DateField()
    receiver = models.CharField(max_length=255)
    description = models.TextField()
    summary = models.TextField()
    object = models.TextField()
    post_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='posted_documents'
    )
    accept_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_documents'
    )
    result = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_datetime']
        permissions = [
            ("can_approve_document", "Can approve document"),
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
        return f"{self.title} - {self.status}"