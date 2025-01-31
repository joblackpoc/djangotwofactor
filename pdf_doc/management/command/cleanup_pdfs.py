from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import os
from datetime import timedelta
from pdf_doc.models import Document

class Command(BaseCommand):
    help = 'Cleanup old PDF files and related records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete files older than specified days'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        # Get documents older than cutoff date
        old_documents = Document.objects.filter(
            created_datetime__lt=cutoff_date,
            status='rejected'
        )

        if dry_run:
            self.stdout.write('Dry run - following would be deleted:')
            for doc in old_documents:
                self.stdout.write(f'- {doc.title} (created: {doc.created_datetime})')
            return

        count = 0
        for doc in old_documents:
            try:
                # Delete associated PDF file
                pdf_path = os.path.join(settings.MEDIA_ROOT, f'pdfs/{doc.id}.pdf')
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    count += 1

                # Delete database record
                doc.delete()

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f'Error deleting {doc.title}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} old PDF files')
        )