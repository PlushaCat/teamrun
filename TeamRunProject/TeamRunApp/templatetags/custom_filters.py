from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def is_older_than_yesterday(value):
    yesterday = datetime.now().date() - timedelta(days=1)
    return value.date() < yesterday