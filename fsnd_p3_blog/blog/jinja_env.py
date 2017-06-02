from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse

def format_datetime(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
       'static': staticfiles_storage.url,
       'url': reverse,
    })
    env.filters['format_datetime'] = format_datetime
    return env
