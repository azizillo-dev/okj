"""
OKJ PLATFORM - COMMENTS MODEL TESTS (apps/comments/tests/test_models.py)
"""

import pytest
from django.core.exceptions import ValidationError
from accounts.models import User
from posts.models import Post
from comments.models import Comment


@pytest.mark.django_db
class TestCommentsModels:
    def test_comment_creation_and_string_representation(self):
        user = User.objects.create_user(phone_number="+998901112233", okj_id="OKJ-91001")
        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="comment-model-quote")

        comment = Comment.objects.create(post=post, user=user, text="Juda ajoyib iqtibos!")
        assert "Root" in str(comment)
        assert comment.is_approved is True

    def test_comment_validation_empty_text(self):
        user = User.objects.create_user(phone_number="+998901112234", okj_id="OKJ-91002")
        post = Post.objects.create(user=user, post_type=Post.PostType.QUOTE, slug="comment-model-quote-2")

        comment = Comment(post=post, user=user, text="")
        with pytest.raises(ValidationError):
            comment.full_clean()
