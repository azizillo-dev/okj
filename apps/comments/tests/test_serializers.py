"""
OKJ PLATFORM - COMMENTS SERIALIZER TESTS (apps/comments/tests/test_serializers.py)
"""

from comments.serializers import CommentWriteSerializer


class TestCommentSerializers:
    def test_comment_write_serializer_valid(self):
        serializer = CommentWriteSerializer(data={"text": "Yaxshi fikr"})
        assert serializer.is_valid() is True
        assert serializer.validated_data["text"] == "Yaxshi fikr"
