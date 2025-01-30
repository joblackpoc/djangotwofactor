from django.urls import path
from . import views

app_name = 'pdf_doc'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('create/', views.document_create, name='document_create'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/update/', views.document_update, name='document_update'),
    path('<int:pk>/review/', views.document_review, name='document_review'),
]