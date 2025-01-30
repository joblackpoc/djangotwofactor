from django import template
from django.utils.safestring import mark_safe
from ..utils import (
    can_user_view_document,
    can_user_print_document,
    can_user_edit_document
)

register = template.Library()

@register.filter
def status_badge(status):
    """
    Return a Bootstrap badge for document status.
    """
    colors = {
        'pending': 'warning',
        'accepted': 'success',
        'rejected': 'danger'
    }
    color = colors.get(status, 'secondary')
    return mark_safe(f'<span class="badge bg-{color}">{status.title()}</span>')

@register.filter
def can_view(user, document):
    """
    Check if user can view the document.
    """
    return can_user_view_document(user, document)

@register.filter
def can_print(user, document):
    """
    Check if user can print the document.
    """
    return can_user_print_document(user, document)

@register.filter
def can_edit(user, document):
    """
    Check if user can edit the document.
    """
    return can_user_edit_document(user, document)

@register.simple_tag
def document_action_buttons(user, document):
    """
    Generate action buttons for a document based on user permissions.
    """
    buttons = []
    
    # View button
    if can_user_view_document(user, document):
        buttons.append(
            f'<a href="#" class="btn btn-info btn-sm">View</a>'
        )
    
    # Edit button
    if can_user_edit_document(user, document):
        buttons.append(
            f'<a href="#" class="btn btn-warning btn-sm">Edit</a>'
        )
    
    # Print button
    if can_user_print_document(user, document):
        buttons.append(
            f'<a href="#" class="btn btn-primary btn-sm">Print</a>'
        )
    
    return mark_safe(' '.join(buttons))

@register.simple_tag
def document_status_icon(status):
    """
    Return an appropriate icon for the document status.
    """
    icons = {
        'pending': '<i class="fas fa-clock text-warning"></i>',
        'accepted': '<i class="fas fa-check-circle text-success"></i>',
        'rejected': '<i class="fas fa-times-circle text-danger"></i>'
    }
    return mark_safe(icons.get(status, ''))

@register.inclusion_tag('pdf_app/tags/document_stats.html')
def document_statistics(user):
    """
    Display document statistics for user.
    """
    from ..utils import get_document_statistics
    return {
        'stats': get_document_statistics(user)
    }