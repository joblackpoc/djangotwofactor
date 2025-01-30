from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import PDFDocument
from .forms import PDFDocumentForm, DocumentReviewForm, DocumentSearchForm
import datetime

class DocumentListView(LoginRequiredMixin, ListView):
    model = PDFDocument
    template_name = 'pdf_app/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        queryset = PDFDocument.objects.all()
        if not self.request.user.has_perm('pdf_app.can_view_all_documents'):
            queryset = queryset.filter(created_by=self.request.user)

        form = DocumentSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')

            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)

        return queryset.select_related('created_by', 'accepted_by')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DocumentSearchForm(self.request.GET)
        return context

@login_required
def document_create(request):
    if request.method == 'POST':
        form = PDFDocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.created_by = request.user
            document.save()
            messages.success(request, 'Document created successfully.')
            return redirect('document_detail', pk=document.pk)
    else:
        form = PDFDocumentForm()
    
    return render(request, 'pdf_app/document_form.html', {'form': form})

class DocumentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = PDFDocument
    template_name = 'pdf_app/document_detail.html'
    context_object_name = 'document'

    def test_func(self):
        document = self.get_object()
        return (document.created_by == self.request.user or 
                self.request.user.has_perm('pdf_app.can_view_all_documents'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_review'] = self.request.user.has_perm('pdf_app.can_accept_documents')
        context['can_print'] = (self.object.status == 'accepted' or 
                              self.request.user.has_perm('pdf_app.can_accept_documents'))
        if context['can_review']:
            context['review_form'] = DocumentReviewForm(instance=self.object)
        return context

@login_required
@permission_required('pdf_app.can_accept_documents')
def document_review(request, pk):
    document = get_object_or_404(PDFDocument, pk=pk)
    
    if request.method == 'POST':
        form = DocumentReviewForm(request.POST, instance=document)
        if form.is_valid():
            review = form.save(commit=False)
            review.accepted_by = request.user
            review.updated_datetime = timezone.now()
            review.save()
            messages.success(request, 'Document reviewed successfully.')
            return redirect('document_detail', pk=pk)
    else:
        return HttpResponseForbidden()

    return render(request, 'pdf_app/document_review.html', {
        'form': form,
        'document': document
    })

@login_required
def document_update(request, pk):
    document = get_object_or_404(PDFDocument, pk=pk)
    
    if document.created_by != request.user:
        return HttpResponseForbidden()
        
    if document.status == 'accepted':
        messages.error(request, 'Cannot update an accepted document.')
        return redirect('document_detail', pk=pk)
        
    if request.method == 'POST':
        form = PDFDocumentForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save(commit=False)
            document.status = 'pending'
            document.save()
            messages.success(request, 'Document updated successfully.')
            return redirect('document_detail', pk=pk)
    else:
        form = PDFDocumentForm(instance=document)
    
    return render(request, 'pdf_app/document_form.html', {
        'form': form,
        'is_update': True
    })