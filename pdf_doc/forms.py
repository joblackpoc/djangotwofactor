from django import forms
from django.core.exceptions import ValidationError
from .models import PDFDocument
from django.utils.translation import gettext_lazy as _

class PDFDocumentForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['title', 'office_name', 'date', 'receiver', 
                 'description', 'summary', 'object']
        
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'office_name': forms.TextInput(attrs={'class': 'form-control'}),
            'receiver': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'object': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Add any custom validation here
        return cleaned_data

class DocumentReviewForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['status', 'result']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        result = cleaned_data.get('result')
        
        if status in ['accepted', 'rejected'] and not result:
            raise ValidationError({
                'result': _('Result is required when accepting or rejecting a document')
            })
        return cleaned_data

class DocumentSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or description'
        })
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise ValidationError('Start date must be before end date')
        return cleaned_data