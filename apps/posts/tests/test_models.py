"""
OKJ PLATFORM - POSTS MODEL TESTS (apps/posts/tests/test_models.py)
"""

import pytest
from accounts.models import User
from posts.models import Post, PostMedia, DraftPost


@pytest.mark.django_db
class TestPostsModels:
    def test_post_and_view_counter_creation(self):
        user = User.objects.create_user(phone_number="+998901114455", okj_id="OKJ-80001")
        post = Post.objects.create(
            user=user,
            post_type=Post.PostType.QUOTE,
            status=Post.Status.PUBLISHED,
            quote_text="Kitob - aqlning chirog'idir.",
            slug="kitob-aqlning-chirogidir",
        )
        assert hasattr(post, "view_counter")
        assert post.view_counter.total_views == 0
        assert str(post) == f"{user.username} — QUOTE (PUBLISHED)"

    def test_draft_post_proxy_model(self):
        user = User.objects.create_user(phone_number="+998901114456", okj_id="OKJ-80002")
        Post.objects.create(user=user, post_type=Post.PostType.REVIEW, status=Post.Status.DRAFT, slug="draft-review")
        Post.objects.create(user=user, post_type=Post.PostType.REVIEW, status=Post.Status.PUBLISHED, slug="pub-review")

        drafts = DraftPost.objects.all()
        assert len(drafts) == 1
        assert drafts[0].status == Post.Status.DRAFT
