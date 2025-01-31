from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Document(models.Model):
    title = models.CharField(max_length=200)
    office_name = models.CharField(max_length=100)
    date = models.DateField()
    receiver = models.CharField(max_length=100)
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
    result = models.TextField(blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_datetime']
        permissions = [
            ("can_accept_document", "Can accept document"),
            ("can_view_all_documents", "Can view all documents"),
        ]

    def __str__(self):
        return self.title