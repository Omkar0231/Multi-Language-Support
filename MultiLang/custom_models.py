from django.db.models import *


class MultiLanguageJSONField(JSONField):
    """
    This is a new JSONField Type which is Specifically used for Multi-Languages. This is created to avoid the
    disruption if using the JSONField directly.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
