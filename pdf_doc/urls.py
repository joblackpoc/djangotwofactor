from django.urls import path
from . import views

app_name = 'pdf_doc'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/update/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('<int:pk>/approve/', views.DocumentApproveView.as_view(), name='document_approve'),
    path('<int:pk>/pdf/', views.generate_pdf_view, name='document_pdf'),
    path('health/', views.health_check, name='health_check'),
]
