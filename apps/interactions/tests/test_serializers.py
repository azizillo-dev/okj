"""
OKJ PLATFORM - INTERACTIONS SERIALIZER TESTS (apps/interactions/tests/test_serializers.py)
"""

from interactions.serializers import BookmarkCreateSerializer


class TestInteractionSerializers:
    def test_bookmark_create_serializer_valid(self):
        serializer = BookmarkCreateSerializer(data={"collection_name": "Sevimli asarlar"})
        assert serializer.is_valid() is True
        assert serializer.validated_data["collection_name"] == "Sevimli asarlar"
