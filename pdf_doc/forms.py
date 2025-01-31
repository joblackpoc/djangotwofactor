from django import forms
from .models import Document
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'office_name', 'date', 'receiver', 
                 'description', 'summary', 'object']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'summary': forms.Textarea(attrs={'rows': 4}),
            'object': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class DocumentAcceptForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['is_accepted', 'result']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 4}),
        }

class DocumentSearchForm(forms.Form):
    search_query = forms.CharField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    status = forms.ChoiceField(
        choices=[('all', 'All'), ('accepted', 'Accepted'), ('pending', 'Pending')],
        required=False
    )