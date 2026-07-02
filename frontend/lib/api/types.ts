export interface APIErrorDetail {
  code: string;
  message: string;
  details?: Record<string, any> | null;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: APIErrorDetail;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface UserProfile {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar?: string | null;
  okj_id?: string;
  total_xp: number;
  level?: number;
  bio?: string | null;
  streak_days?: number;
}

export type User = UserProfile;

export interface Author {
  id: string;
  name: string;
  slug?: string;
}

export interface Book {
  id: string;
  title: string;
  slug: string;
  isbn_10?: string | null;
  isbn_13?: string | null;
  cover_image?: string | null;
  authors: Author[];
  average_rating?: number;
  ratings_count?: number;
  description?: string;
}

export type PostType = 'QUOTE' | 'REVIEW' | 'SHOWCASE' | 'EXCHANGE' | 'GIFT' | 'SELL';

export interface PostMedia {
  id: string;
  file_url: string;
  media_type: 'IMAGE' | 'VIDEO';
}

export interface Post {
  id: string;
  user: UserProfile;
  book?: Book | null;
  post_type: PostType;
  title?: string;
  content: string;
  quote_page?: number | null;
  price?: number | null;
  media: PostMedia[];
  likes_count: number;
  comments_count: number;
  is_liked_by_user?: boolean;
  created_at: string;
}

export interface PassportAnalytics {
  okj_id: string;
  user: UserProfile;
  books_read_count: number;
  pages_read_count: number;
  current_streak: number;
  stamps: Array<{
    id: string;
    icon: string;
    label: string;
    locked: boolean;
  }>;
}

export interface Comment {
  id: string;
  post_id: string;
  parent_id?: string | null;
  user: UserProfile;
  content: string;
  likes_count: number;
  is_liked_by_user?: boolean;
  created_at: string;
  replies?: Comment[];
}

