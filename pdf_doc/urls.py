from django.urls import path
from . import views

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('update/<int:pk>/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('preview/<int:pk>/', views.DocumentPreviewView.as_view(), name='document_preview'),
    path('staff/', views.StaffDocumentListView.as_view(), name='staff_document_list'),
    path('download/<int:pk>/', views.download_pdf, name='download_pdf'),
]