# OKJ Platform — Comments Module Architecture (`apps/comments/`)

This document serves as the comprehensive architectural reference for the **Comments & Discussions Module**, managing community engagement across the **O'zbekiston Kitobxonlari Jamiyati (OKJ)** platform.

---

## 1. Flat-Tree Hierarchy (Maximum 2 Levels)

Unlike traditional forums or Reddit threads that allow infinite nested replies ($O(N)$ depth recursion), OKJ enforces a strict **Flat-Tree Hierarchy (Maximum 2 Levels)** modeled after Instagram and YouTube:
- **Level 0 (Root Comment)**: Directly attached to a `Post` (`parent = None`).
- **Level 1 (Reply)**: Directly attached to a Root Comment (`parent = root_comment`).

### Why Flat-Tree?
If user $C$ replies to reply $B$, which replied to root comment $A$ (3rd level attempt), the service layer automatically redirects user $C$'s `parent_id` pointer directly to root comment $A$:
```python
target_parent = parent_comment.parent if parent_comment.parent_id else parent_comment
```
This guarantees UI consistency on mobile screens without deeply indented UI trees and prevents recursive database queries.

---

## 2. Gamification & Anti-Spam Strategy

Following OKJ's gamification rules:
- **Root Comments (`Level 0`)**: Rewarded with **+5 XP** via `UserService.add_xp(user, amount=5)`.
- **Replies (`Level 1`)**: **0 XP awarded**.
*Why*: If users received XP for every nested reply, bad actors could spam brief replies inside active discussions to farm XP. Restricting rewards to original top-level commentary encourages meaningful, high-effort book insights.

---

## 3. High-Performance Query Optimization (N+1 Free)

To fetch an entire post's comment tree in exactly **2 SQL queries**, `CommentSelector.get_comments_for_post(post_id)` uses Django's `Prefetch` mechanism:
1. **Query 1**: Retrieves all approved root comments (`parent__isnull=True`) with author profiles joined via `select_related("user")`.
2. **Query 2**: Retrieves all approved child replies matching those root IDs in bulk (`WHERE parent_id IN (...)`), also joining their authors via `select_related("user")`.

---

## 4. Soft Delete & Text Interpretation

When a root comment with child replies is deleted via `soft_delete_comment`:
- The database record is retained with `is_deleted = True` and `deleted_at = timezone.now()`.
- Child replies remain untouched and visible under the discussion thread.
- `CommentReadSerializer` dynamically evaluates `obj.is_deleted`. If true, the output text is replaced with `"Bu izoh muallif tomonidan o'chirilgan"`, preserving conversational flow without dead links.
