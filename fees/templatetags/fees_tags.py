from django import template
from students.models import AcademicYear

register = template.Library()


@register.simple_tag
def current_year_display():
    year = AcademicYear.get_current()
    return year.name if year else 'No Active Year'


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
