from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def status_badge(status):
    """Return a Bootstrap badge for document status."""
    colors = {
        'pending': 'warning',
        'accepted': 'success',
        'rejected': 'danger'
    }
    color = colors.get(status, 'secondary')
    return mark_safe(f'<span class="badge bg-{color}">{status.title()}</span>')

@register.filter
def can_edit_document(user, document):
    """Check if user can edit the document."""
    if user.is_staff:
        return True
    return document.post_by == user and document.status != 'accepted'

@register.filter
def can_print_document(user, document):
    """Check if user can print the document."""
    if user.is_staff:
        return True
    return document.post_by == user and document.status == 'accepted'

@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Returns the URL-encoded querystring for the current page,
    updating the params with the key/value pairs passed to the tag.
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using string key."""
    return dictionary.get(key)

@register.filter
def format_date(date):
    """Format date in a consistent way."""
    if date:
        return date.strftime("%Y-%m-%d")
    return ''