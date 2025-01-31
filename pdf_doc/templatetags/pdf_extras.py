from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import mark_safe
import markdown as md

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    """Convert markdown to HTML."""
    return mark_safe(md.markdown(value))

@register.filter
def status_color(status):
    """Return Bootstrap color class based on status."""
    colors = {
        'pending': 'warning',
        'accepted': 'success',
        'rejected': 'danger'
    }
    return colors.get(status, 'secondary')

@register.filter
def file_size_format(size):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@register.simple_tag(takes_context=True)
def is_document_editable(context, document):
    """Check if document is editable by current user."""
    user = context['request'].user
    return (
        user.is_staff or 
        (document.post_by == user and document.status != 'accepted')
    )

@register.simple_tag(takes_context=True)
def can_print_document(context, document):
    """Check if user can print document."""
    user = context['request'].user
    return (
        user.is_staff or 
        (document.status == 'accepted' and document.post_by == user)
    )

@register.inclusion_tag('pdf/status_badge.html')
def status_badge(status):
    """Render status badge with appropriate color."""
    return {
        'status': status,
        'color': status_color(status)
    }

@register.simple_tag
def query_transform(request, **kwargs):
    """Transform current URL query parameters."""
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            updated[k] = v
        else:
            updated.pop(k, 0)
    return updated.urlencode()