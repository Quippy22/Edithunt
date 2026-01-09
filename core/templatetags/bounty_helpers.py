"""
Custom template tags and filters for the core application.
"""
from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.simple_tag
def remaining_time_display(deadline):
    """
    Calculates the time remaining until a deadline and returns a dictionary
    containing a formatted string and a corresponding Tailwind CSS class for color-coding.

    Args:
        deadline (datetime): The deadline datetime object for a bounty.

    Returns:
        dict: A dictionary with two keys:
              'text' (str): Formatted time remaining (e.g., "5 days, 12 hours left").
              'class' (str): The Tailwind CSS class for color-coding the text.
    """
    now = timezone.now()
    remaining = deadline - now

    if remaining < timedelta(seconds=0):
        return {'text': 'Expired', 'class': 'text-gray-500'}

    days = remaining.days
    hours = remaining.seconds // 3600

    text = f"{days} days, {hours} hours left"

    css_class = ''
    if remaining < timedelta(days=1):
        # Less than 1 day: Dark Red
        css_class = 'text-red-800 dark:text-red-600'
    elif remaining < timedelta(days=3):
        # 1 to 3 days: Bright Red
        css_class = 'text-red-600 dark:text-red-400'
    elif remaining < timedelta(days=7):
        # 3 to 7 days: Yellow
        css_class = 'text-yellow-600 dark:text-yellow-400'
    else:
        # More than 7 days: Green
        css_class = 'text-green-500 dark:text-green-400'

    return {'text': text, 'class': css_class}
