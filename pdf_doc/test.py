from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.core import mail
from .models import PDFDocument
from .forms import PDFDocumentForm, DocumentReviewForm
import datetime

class PDFDocumentTestCase(TestCase):
    def setUp(self):
        # Create user groups
        self.staff_group = Group.objects.create(name='Staff')
        self.normal_group = Group.objects.create(name='Normal Users')

        # Create users
        self.normal_user = User.objects.create_user(
            username='normal_user',
            password='testpass123',
            email='normal@example.com'
        )
        self.staff_user = User.objects.create_user(
            username='staff_user',
            password='testpass123',
            email='staff@example.com',
            is_staff=True
        )
        
        # Add users to groups
        self.normal_user.groups.add(self.normal_group)
        self.staff_user.groups.add(self.staff_group)

        # Create test document
        self.document = PDFDocument.objects.create(
            title='Test Document',
            office_name='Test Office',
            date=timezone.now().date(),
            receiver='Test Receiver',
            description='Test Description',
            summary='Test Summary',
            object='Test Object',
            created_by=self.normal_user,
            status='pending'
        )

    def test_document_creation(self):
        """Test document creation"""
        self.assertEqual(self.document.title, 'Test Document')
        self.assertEqual(self.document.status, 'pending')
        self.assertEqual(self.document.created_by, self.normal_user)

    def test_document_list_view(self):
        """Test document list view access"""
        # Test unauthenticated access
        response = self.client.get(reverse('pdf_app:document_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test normal user access
        self.client.login(username='normal_user', password='testpass123')
        response = self.client.get(reverse('pdf_app:document_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pdf_app/document_list.html')

    def test_document_creation_view(self):
        """Test document creation view"""
        self.client.login(username='normal_user', password='testpass123')
        
        data = {
            'title': 'New Document',
            'office_name': 'Test Office',
            'date': timezone.now().date(),
            'receiver': 'Test Receiver',
            'description': 'Test Description',
            'summary': 'Test Summary',
            'object': 'Test Object',
        }
        
        response = self.client.post(reverse('pdf_app:document_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(PDFDocument.objects.filter(title='New Document').exists())

    def test_document_review(self):
        """Test document review process"""
        self.client.login(username='staff_user', password='testpass123')
        
        review_data = {
            'status': 'accepted',
            'result': 'Document approved',
        }
        
        response = self.client.post(
            reverse('pdf_app:document_review', kwargs={'pk': self.document.pk}),
            review_data
        )
        
        # Refresh document from database
        self.document.refresh_from_db()
        self.assertEqual(self.document.status, 'accepted')
        self.assertEqual(self.document.result, 'Document approved')

    def test_document_update(self):
        """Test document update"""
        self.client.login(username='normal_user', password='testpass123')
        
        update_data = {
            'title': 'Updated Document',
            'office_name': self.document.office_name,
            'date': self.document.date,
            'receiver': self.document.receiver,
            'description': 'Updated Description',
            'summary': self.document.summary,
            'object': self.document.object,
        }
        
        response = self.client.post(
            reverse('pdf_app:document_update', kwargs={'pk': self.document.pk}),
            update_data
        )
        
        # Refresh document from database
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Document')
        self.assertEqual(self.document.description, 'Updated Description')

    def test_document_permissions(self):
        """Test document access permissions"""
        # Create another normal user
        other_user = User.objects.create_user(
            username='other_user',
            password='testpass123'
        )
        
        # Test access to document detail
        self.client.login(username='other_user', password='testpass123')
        response = self.client.get(
            reverse('pdf_app:document_detail', kwargs={'pk': self.document.pk})
        )
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Test staff access
        self.client.login(username='staff_user', password='testpass123')
        response = self.client.get(
            reverse('pdf_app:document_detail', kwargs={'pk': self.document.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_document_search(self):
        """Test document search functionality"""
        self.client.login(username='normal_user', password='testpass123')
        
        # Create additional test documents
        PDFDocument.objects.create(
            title='Search Test',
            office_name='Search Office',
            date=timezone.now().date(),
            receiver='Search Receiver',
            description='Searchable Description',
            summary='Test Summary',
            object='Test Object',
            created_by=self.normal_user
        )
        
        # Test search by title
        response = self.client.get(reverse('pdf_app:document_list'), {'search_query': 'Search'})
        self.assertContains(response, 'Search Test')
        self.assertNotContains(response, 'Test Document')

    def test_email_notifications(self):
        """Test email notifications"""
        self.client.login(username='staff_user', password='testpass123')
        
        # Review document
        review_data = {
            'status': 'accepted',
            'result': 'Document approved',
        }
        
        response = self.client.post(
            reverse('pdf_app:document_review', kwargs={'pk': self.document.pk}),
            review_data
        )
        
        # Check that one email has been sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.normal_user.email)

class PDFDocumentFormTests(TestCase):
    """Test form validation"""
    
    def test_document_form_validation(self):
        form_data = {
            'title': '',  # Empty title should fail
            'office_name': 'Test Office',
            'date': timezone.now().date(),
            'receiver': 'Test Receiver',
            'description': 'Test Description',
            'summary': 'Test Summary',
            'object': 'Test Object',
        }
        
        form = PDFDocumentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

class PDFDocumentUtilsTests(TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='testpass123'
        )
        self.document = PDFDocument.objects.create(
            title='Test Document',
            office_name='Test Office',
            date=timezone.now().date(),
            receiver='Test Receiver',
            description='Test Description',
            summary='Test Summary',
            object='Test Object',
            created_by=self.user
        )
    
    def test_pdf_generation(self):
        """Test PDF generation utility"""
        from .utils import generate_pdf
        pdf_content = generate_pdf(self.document)
        self.assertIsNotNone(pdf_content)

    def test_document_filename_generation(self):
        """Test filename generation utility"""
        from .utils import get_document_filename
        filename = get_document_filename(self.document)
        self.assertIn('test-document', filename.lower())
        self.assertIn('.pdf', filename.lower())