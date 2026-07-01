"""
OKJ PLATFORM - SHARED DRF MIXINS (shared/mixins.py)
Nega bu fayl kerak: HackSoft Django Styleguide bo'yicha APIView va Serializerlarda
serializerni tanlash (m-n: read va write uchun alohida serializer) mixinlarini berish.
"""

from rest_framework.response import Response
from rest_framework import status


class MultiSerializerViewSetMixin:
    """
    Actionga qarab turli serializerlarni tanlaydi:
    m-n: list() va retrieve() uchun ReadSerializer, create() uchun WriteSerializer.
    """
    serializer_action_classes = {}

    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()
