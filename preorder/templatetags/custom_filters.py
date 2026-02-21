"""
custom_filters.py — Custom Django template filters used in templates.

Usage in templates:
  {% load custom_filters %}
  {{ value|percentage:total }}
"""

from django import template

register = template.Library()


@register.filter
def percentage(value, total):
    """
    Usage: {{ current_orders|percentage:max_capacity }}
    Returns an integer percentage (0-100).
    """
    try:
        if int(total) == 0:
            return 0
        return int((int(value) / int(total)) * 100)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    """Usage: {{ max_capacity|subtract:current_orders }} → remaining slots."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def multiply(value, arg):
    """Usage: {{ price|multiply:quantity }} → subtotal."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
