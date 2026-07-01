# OKJ Platform — Follows Module Architecture (`apps/follows/`)

This document details the architectural principles behind the **Social Graph & Follows Module** of the **O'zbekiston Kitobxonlari Jamiyati (OKJ)** platform.

---

## 1. Directed Social Graph Modeling

In literature-oriented communities, directional relationships (following favorite reviewers or authors without requiring reciprocal friending) provide optimal discovery.
- **`follower`**: The reader initiating the relationship.
- **`following`**: The target reader being subscribed to.

---

## 2. Integrity Constraints & Anti-Abuse Rules

### 2.1 Preventing Self-Follows
A reader subscribing to themselves corrupts algorithmic feed ranking and artificially inflates follower counts. OKJ enforces two layers of defense against self-following:
1. **Model Validation Layer**: `clean()` validates `self.follower_id != self.following_id` before save.
2. **Database Schema Layer**: PostgreSQL `CheckConstraint(check=~Q(follower=F("following")))` guarantees database integrity even under direct SQL insertions or concurrency races.

### 2.2 Active Relationship Uniqueness
Using `UniqueConstraint(fields=["follower", "following"], condition=Q(is_deleted=False))`, a user can only maintain a single active follow record towards another user.

---

## 3. High-Performance $O(1)$ Row-Reuse (Toggle Strategy)

When a user follows, unfollows, and re-follows someone:
Instead of inserting redundant database rows that bloat historical tables, `FollowService.follow_user` performs an $O(1)$ lookup on `Follow.all_objects`. If a soft-deleted record exists (`is_deleted=True`), it reactivates the row (`is_deleted=False`). This minimizes PostgreSQL page fragmentation and preserves index density.

---

## 4. Decoupled Event Hook (`_on_user_followed`)

To adhere to the modular monolith architecture:
`FollowService._on_user_followed` serves as an asynchronous dispatch hook. Currently, it triggers gamification rewards (+5 XP). In upcoming milestones (**Step 9: Notifications** and **Step 10: Feed Ranking**), this hook will emit background event signals without altering core follow service code.
