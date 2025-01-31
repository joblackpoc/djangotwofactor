from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Document
from .forms import DocumentForm, DocumentAcceptForm, DocumentSearchForm
from .utils import generate_pdf

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'document_manager/document_form.html'
    success_url = reverse_lazy('document_list')

    def form_valid(self, form):
        form.instance.post_by = self.request.user
        return super().form_valid(form)

class DocumentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'document_manager/document_form.html'
    success_url = reverse_lazy('document_list')

    def test_func(self):
        obj = self.get_object()
        return obj.post_by == self.request.user and not obj.is_accepted

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'document_manager/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        queryset = Document.objects.all()
        if not self.request.user.has_perm('document_manager.can_view_all_documents'):
            queryset = queryset.filter(post_by=self.request.user)

        form = DocumentSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get('search_query')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            status = form.cleaned_data.get('status')

            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)
            if status == 'accepted':
                queryset = queryset.filter(is_accepted=True)
            elif status == 'pending':
                queryset = queryset.filter(is_accepted=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DocumentSearchForm(self.request.GET)
        return context

class StaffDocumentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Document
    template_name = 'document_manager/staff_document_list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def test_func(self):
        return self.request.user.has_perm('document_manager.can_accept_document')

class DocumentPreviewView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'document_manager/document_preview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_print'] = (
            self.object.is_accepted or 
            self.request.user.has_perm('document_manager.can_accept_document')
        )
        return context
    
from django.http import HttpResponse
from .utils import generate_pdf

def download_pdf(request, pk):
    try:
        document = get_object_or_404(Document, pk=pk)
        
        # Check if user has permission to download
        if not (document.is_accepted or 
                document.post_by == request.user or 
                request.user.has_perm('document_manager.can_accept_document')):
            messages.error(request, "You don't have permission to download this document.")
            return redirect('document_list')
        
        # Generate PDF
        pdf = generate_pdf(document)
        
        # Create the HttpResponse object with PDF headers
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.title}.pdf"'
        return response
        
    except Exception as e:
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('document_list')