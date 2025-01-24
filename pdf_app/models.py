from django.db import models
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB limit
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    return value

class YearCategory(models.Model):
    year = models.PositiveIntegerField(unique=True, default=2025)
    
    class Meta:
        verbose_name_plural = "Year Categories"
        ordering = ['-year']
    
    def __str__(self):
        return str(self.year)

    def clean(self):
        if not 1900 <= self.year <= 2100:
            raise ValidationError("Year must be between 1900 and 2100")

class Category(models.Model):
    name = models.CharField(max_length=100)
    year_category = models.ForeignKey(
        YearCategory,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
        unique_together = ['name', 'year_category']
    
    def __str__(self):
        return f"{self.name} ({self.year_category.year})"

    def clean(self):
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError("Category name cannot be empty")

class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    
    class Meta:
        verbose_name_plural = "Sub Categories"
        ordering = ['name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

    def clean(self):
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError("Subcategory name cannot be empty")

class Post(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    pdf_file = models.FileField(
        upload_to='pdfs/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf'],
                message="Only PDF files are allowed."
            ),
            validate_file_size
        ]
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('pdf_app:post_detail', kwargs={'pk': self.pk})

    def clean(self):
        if self.title:
            self.title = self.title.strip()
        if not self.title:
            raise ValidationError("Title cannot be empty")
        
        if not self.pdf_file:
            raise ValidationError("PDF file is required")
        
        if self.pdf_file and not self.pdf_file.name.lower().endswith('.pdf'):
            raise ValidationError('File must be a PDF.')