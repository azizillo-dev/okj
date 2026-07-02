"""
OKJ PLATFORM - POSTS SERIALIZER TESTS (apps/posts/tests/test_serializers.py)
"""

from posts.serializers import CreatePostSerializer


class TestPostSerializers:
    def test_create_post_serializer_valid(self):
        data = {
            "post_type": "REVIEW",
            "status": "PUBLISHED",
            "title": "Ajoyib kitob",
            "content": "Juda yoqdi.",
            "user_rating": 5,
        }
        serializer = CreatePostSerializer(data=data)
        assert serializer.is_valid() is True

    def test_create_post_serializer_invalid_rating(self):
        data = {
            "post_type": "REVIEW",
            "user_rating": 10,
        }
        serializer = CreatePostSerializer(data=data)
        assert serializer.is_valid() is False
        assert "user_rating" in serializer.errors
