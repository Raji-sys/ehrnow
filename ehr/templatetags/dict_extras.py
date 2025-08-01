from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using template syntax"""
    if dictionary and key:
        return dictionary.get(key, 0)
    return 0