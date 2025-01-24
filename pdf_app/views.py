from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import JsonResponse
from .models import Post, Category, SubCategory, YearCategory
from .forms import PostForm, SearchForm

class PostListView(ListView):
    model = Post
    template_name = 'pdf_app/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)
        
        if form.is_valid():
            query = form.cleaned_data.get('query')
            year = form.cleaned_data.get('year')
            category = form.cleaned_data.get('category')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            
            if year:
                queryset = queryset.filter(
                    subcategory__category__year_category=year
                )
            
            if category:
                queryset = queryset.filter(
                    subcategory__category=category
                )
        
        return queryset

class PostDetailView(DetailView):
    model = Post
    template_name = 'pdf_app/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the full URL for the PDF file
        context['pdf_url'] = self.request.build_absolute_uri(self.object.pdf_file.url)
        return context

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'pdf_app/post_form.html'
    success_url = reverse_lazy('pdf_app:post_list')

    def form_valid(self, form):
        # Set the subcategory from the form before saving
        form.instance.subcategory = form.cleaned_data['subcategory']
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'pdf_app/post_form.html'

    def form_valid(self, form):
        # Set the subcategory from the form before saving
        form.instance.subcategory = form.cleaned_data['subcategory']
        return super().form_valid(form)

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'pdf_app/post_confirm_delete.html'
    success_url = reverse_lazy('pdf_app:post_list')

def get_categories(request):
    """AJAX view to get categories for a year"""
    year_id = request.GET.get('year_id')
    categories = Category.objects.filter(year_category_id=year_id)
    return JsonResponse({
        'categories': list(categories.values('id', 'name'))
    })

def get_subcategories(request):
    """AJAX view to get subcategories for a category"""
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse({
        'subcategories': list(subcategories.values('id', 'name'))
    })