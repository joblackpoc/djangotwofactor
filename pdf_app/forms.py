from django import forms
from .models import Post, Category, SubCategory, YearCategory

class PostForm(forms.ModelForm):
    year_category = forms.ModelChoiceField(
        queryset=YearCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Year"
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Category"
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Subcategory"
    )

    class Meta:
        model = Post
        fields = ['year_category', 'category', 'subcategory', 'title', 'description', 'pdf_file']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # If we have an instance (editing an existing post)
        if self.instance.pk:
            # Set the year category
            self.fields['year_category'].initial = self.instance.subcategory.category.year_category
            
            # Set category queryset and initial value
            self.fields['category'].queryset = Category.objects.filter(
                year_category=self.instance.subcategory.category.year_category
            )
            self.fields['category'].initial = self.instance.subcategory.category
            
            # Set subcategory queryset and initial value
            self.fields['subcategory'].queryset = SubCategory.objects.filter(
                category=self.instance.subcategory.category
            )
            self.fields['subcategory'].initial = self.instance.subcategory

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )
    year = forms.ModelChoiceField(
        queryset=YearCategory.objects.all(),
        required=False,
        empty_label="All Years",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )