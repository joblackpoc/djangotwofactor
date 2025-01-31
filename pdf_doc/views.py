from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from .models import Document
from .forms import DocumentForm, DocumentApprovalForm, DocumentSearchForm
from .utils import generate_pdf
import datetime

class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'pdf/list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        queryset = Document.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(post_by=self.request.user)

        form = DocumentSearchForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            status = form.cleaned_data.get('status')

            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )
            if date_from:
                queryset = queryset.filter(date__gte=date_from)
            if date_to:
                queryset = queryset.filter(date__lte=date_to)
            if status:
                queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = DocumentSearchForm(self.request.GET)
        return context

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'pdf/create.html'
    success_url = reverse_lazy('document_list')

    def form_valid(self, form):
        form.instance.post_by = self.request.user
        return super().form_valid(form)

class DocumentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'pdf/create.html'
    success_url = reverse_lazy('document_list')

    def test_func(self):
        obj = self.get_object()
        return obj.post_by == self.request.user and obj.status != 'accepted'

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'pdf/detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_print'] = (
            self.request.user.is_staff or
            (self.object.status == 'accepted' and 
             self.object.post_by == self.request.user)
        )
        if self.request.user.is_staff:
            context['approval_form'] = DocumentApprovalForm(instance=self.object)
        return context

class DocumentApproveView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Document
    form_class = DocumentApprovalForm
    template_name = 'pdf/approve.html'
    success_url = reverse_lazy('document_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.accept_by = self.request.user
        form.instance.updated_datetime = timezone.now()
        messages.success(self.request, 'Document status updated successfully.')
        return super().form_valid(form)

def generate_pdf_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    
    if not request.user.is_staff and (
        document.post_by != request.user or 
        document.status != 'accepted'
    ):
        messages.error(request, 'Permission denied.')
        return redirect('document_list')

    pdf = generate_pdf(document)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{document.title}.pdf"'
    return response

from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError
from redis import Redis
from redis.exceptions import RedisError
import os

def health_check(request):
    # Check database connection
    db_healthy = True
    try:
        connections['default'].cursor()
    except OperationalError:
        db_healthy = False

    # Check Redis connection
    redis_healthy = True
    try:
        redis_client = Redis.from_url(
            os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
            socket_connect_timeout=1
        )
        redis_client.ping()
    except RedisError:
        redis_healthy = False

    # Check disk usage
    storage_healthy = True
    try:
        stats = os.statvfs('/app')
        available_space = (stats.f_bavail * stats.f_frsize) / (1024 * 1024)  # MB
        if available_space < 500:  # Less than 500MB
            storage_healthy = False
    except Exception:
        storage_healthy = False

    status = all([db_healthy, redis_healthy, storage_healthy])
    
    response_data = {
        'status': 'healthy' if status else 'unhealthy',
        'database': 'up' if db_healthy else 'down',
        'redis': 'up' if redis_healthy else 'down',
        'storage': 'ok' if storage_healthy else 'low',
    }

    status_code = 200 if status else 503
    return JsonResponse(response_data, status=status_code)

def handler403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)