from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    """Dynamically get an attribute from an object"""
    return getattr(obj, attr_name, 0)

@register.filter
def split(value, arg):
    """Split a string by a delimiter"""
    return value.split(arg)
