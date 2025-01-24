from django import forms
from .models import Post, Comment, Category
#from crispy_forms.helper import FormHelper
#from crispy_forms.layout import Layout, Submit, Div, Field, Row, Column
from django_ckeditor_5.widgets import CKEditor5Widget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }

class PostForm(forms.ModelForm):
    # Change categories to use Select widget instead of CheckboxSelectMultiple
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'size': '3'  # Show 3 options at once
        }),
        required=False
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'categories', 'status', 'featured', 'allow_comments']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            }),
            'content': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='default'
            ),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_comments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }
# class ReplyForm(forms.ModelForm):
#     class Meta:
#         model = Reply
#         fields = ['content']
#         widgets = {
#             'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

# class ReplyForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = ['content']
#         widgets = {
#             'content': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 2,
#                 'placeholder': 'Write your reply here...'
#             })
#         }
#         labels = {
#             'content': 'Reply'
#         }

class PostSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + list(Post.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    order_by = forms.ChoiceField(
        choices=[
            ('-created_date', 'Newest First'),
            ('created_date', 'Oldest First'),
            ('-views', 'Most Viewed'),
            ('-total_likes', 'Most Liked'),
            ('-total_comments', 'Most Commented'),
        ],
        required=False,
        initial='-created_date',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class CategorySearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search categories...'
        })
    )
    order_by = forms.ChoiceField(
        choices=[
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('-posts_count', 'Most Posts'),
            ('created_at', 'Oldest'),
            ('-created_at', 'Newest'),
        ],
        required=False,
        initial='name',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )