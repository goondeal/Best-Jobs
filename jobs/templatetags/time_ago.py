from datetime import datetime
from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime


register = template.Library()

@register.filter(expects_localtime=True)
def timeago(value, arg=None):
    try:
        tzinfo = getattr(value, 'tzinfo', None)
        # value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object
        return value
    except ValueError:
        # Date arguments out of range
        return value

    # today = datetime.now(tzinfo)
    # delta = value - today
    
    # if abs(delta.days) < 8:
    #     return naturaltime(value)
    # else:
    #     res = naturaltime(value)
    #     comma_idx = res.find(',')
    #     return res[:comma_idx] + res[res.find(' ago'):] if comma_idx != -1 else res
    res = naturaltime(value)
    comma_idx = res.find(',')
    return res[:comma_idx] + res[res.find(' ago'):] if comma_idx != -1 else res

    # if delta.days < 1:
    #     fa_str = _("ago")
    # else:
    #     fa_str = _("from now")

    # return "%s %s %s" % (abs(delta.days), day_str, fa_str)

@register.filter(expects_localtime=True)
def weekpassed(value, arg=None):
    try:
        tzinfo = getattr(value, 'tzinfo', None)
        # value = date(value.year, value.month, value.day)
    except AttributeError:
        # Passed value wasn't a date object
        return value
    except ValueError:
        # Date arguments out of range
        return value

    today = datetime.now(tzinfo)
    delta = today - value
    
    return delta.days > 6
    # if delta.days < 1:
    #     fa_str = _("ago")
    # else:
    #     fa_str = _("from now")

    # return "%s %s %s" % (abs(delta.days), day_str, fa_str)
