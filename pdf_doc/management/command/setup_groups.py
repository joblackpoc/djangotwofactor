from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pdf_app.models import PDFDocument

class Command(BaseCommand):
    help = 'Create default groups and permissions for PDF Generator'

    def handle(self, *args, **kwargs):
        # Create groups
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        user_group, _ = Group.objects.get_or_create(name='Normal Users')

        # Get content type for PDFDocument model
        pdf_content_type = ContentType.objects.get_for_model(PDFDocument)

        # Create custom permissions
        view_all_perm, _ = Permission.objects.get_or_create(
            codename='can_view_all_documents',
            name='Can view all documents',
            content_type=pdf_content_type,
        )
        
        accept_perm, _ = Permission.objects.get_or_create(
            codename='can_accept_documents',
            name='Can accept documents',
            content_type=pdf_content_type,
        )

        # Get basic model permissions
        view_perm = Permission.objects.get(
            codename='view_pdfdocument',
            content_type=pdf_content_type,
        )
        add_perm = Permission.objects.get(
            codename='add_pdfdocument',
            content_type=pdf_content_type,
        )
        change_perm = Permission.objects.get(
            codename='change_pdfdocument',
            content_type=pdf_content_type,
        )

        # Assign permissions to staff group
        staff_permissions = [
            view_perm,
            add_perm,
            change_perm,
            view_all_perm,
            accept_perm,
        ]
        staff_group.permissions.set(staff_permissions)

        # Assign permissions to normal users group
        user_permissions = [
            view_perm,
            add_perm,
            change_perm,
        ]
        user_group.permissions.set(user_permissions)

        self.stdout.write(
            self.style.SUCCESS('Successfully created groups and permissions')
        )