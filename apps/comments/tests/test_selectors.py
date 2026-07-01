"""
OKJ PLATFORM - COMMENTS SELECTOR TESTS (apps/comments/tests/test_selectors.py)
"""

import pytest
from accounts.models import User
from posts.models import Post
from comments.models import Comment
from comments.selectors import CommentSelector


@pytest.mark.django_db
class TestCommentSelector:
    def test_get_comments_tree_prefetch(self):
        user = User.objects.create_user(phone_number="+998902223344", okj_id="OKJ-91003")
        post = Post.objects.create(user=user, post_type=Post.PostType.REVIEW, slug="tree-test-review")

        root = Comment.objects.create(post=post, user=user, text="Asosiy fikr")
        reply1 = Comment.objects.create(post=post, user=user, parent=root, text="1-javob")
        reply2 = Comment.objects.create(post=post, user=user, parent=root, text="2-javob")

        tree = CommentSelector.get_comments_for_post(post.id)
        assert len(tree) == 1
        assert tree[0].id == root.id
        assert len(tree[0].replies.all()) == 2
