from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _, ugettext_noop as _noop


class MomoAppConfig(AppConfig):
    name = 'momo_app'
    verbose_name = _('momo_app')

    def ready(self):
        import momo_app.signals
