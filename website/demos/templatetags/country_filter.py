from django import template
register = template.Library()

@register.filter
def in_country(magazines, country):
    return magazines.filter(country=country)