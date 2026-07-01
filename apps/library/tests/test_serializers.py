"""
OKJ PLATFORM - LIBRARY SERIALIZER TESTS (apps/library/tests/test_serializers.py)
"""

import pytest
from library.serializers import LogReadingProgressSerializer, CreateGoalSerializer


class TestLibrarySerializers:
    def test_log_reading_progress_serializer_valid(self):
        data = {
            "library_item_id": "123e4567-e89b-12d3-a456-426614174000",
            "pages_read": 25,
            "minutes_spent": 30,
        }
        serializer = LogReadingProgressSerializer(data=data)
        assert serializer.is_valid() is True

    def test_log_reading_progress_serializer_invalid_pages(self):
        data = {
            "library_item_id": "123e4567-e89b-12d3-a456-426614174000",
            "pages_read": 0,
        }
        serializer = LogReadingProgressSerializer(data=data)
        assert serializer.is_valid() is False
        assert "pages_read" in serializer.errors
