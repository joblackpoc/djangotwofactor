from django import forms
from .models import Document
from django.core.exceptions import ValidationError
from django.utils import timezone

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'title', 'office_name', 'date', 'receiver',
            'description', 'summary', 'object'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'object': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        
        if date and date > timezone.now().date():
            raise ValidationError({
                'date': 'Date cannot be in the future'
            })
        return cleaned_data

class DocumentApprovalForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['status', 'result']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        result = cleaned_data.get('result')

        if status in ['accepted', 'rejected'] and not result:
            raise ValidationError({
                'result': 'Result is required when accepting or rejecting a document'
            })
        return cleaned_data

class DocumentSearchForm(forms.Form):
    search = forms.CharField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    status = forms.ChoiceField(
        choices=[('', 'All')] + Document._meta.get_field('status').choices,
        required=False
    )