import { apiClient } from './client';
import { APIResponse, PaginatedResponse, Post, Comment } from './types';

export const postsApi = {
  getFeed: async (params?: { page?: number; type?: string }): Promise<PaginatedResponse<Post>> => {
    const response = await apiClient.get<APIResponse<PaginatedResponse<Post>>>('/posts/', { params });
    return response.data.data!;
  },

  getPostById: async (slug: string): Promise<Post> => {
    const response = await apiClient.get<APIResponse<Post>>(`/posts/${slug}/`);
    return response.data.data!;
  },

  getPostBySlug: async (slug: string): Promise<Post> => {
    const response = await apiClient.get<APIResponse<Post>>(`/posts/${slug}/`);
    return response.data.data!;
  },

  getPostComments: async (slug: string): Promise<Comment[]> => {
    const response = await apiClient.get<APIResponse<Comment[]>>(`/posts/${slug}/comments/`);
    return response.data.data || [];
  },

  getComments: async (slug: string): Promise<Comment[]> => {
    const response = await apiClient.get<APIResponse<Comment[]>>(`/posts/${slug}/comments/`);
    return response.data.data || [];
  },

  addComment: async (slug: string, content: string, parentId?: string): Promise<Comment> => {
    const response = await apiClient.post<APIResponse<Comment>>(`/posts/${slug}/comments/`, {
      content,
      parent_id: parentId || null,
    });
    return response.data.data!;
  },

  createComment: async (slug: string, content: string, parentId?: string): Promise<Comment> => {
    const response = await apiClient.post<APIResponse<Comment>>(`/posts/${slug}/comments/`, {
      content,
      parent_id: parentId || null,
    });
    return response.data.data!;
  },

  createPost: async (postData: Record<string, any>): Promise<Post> => {
    const response = await apiClient.post<APIResponse<Post>>('/posts/', postData);
    return response.data.data!;
  },

  deletePost: async (slug: string): Promise<void> => {
    await apiClient.delete(`/posts/${slug}/`);
  },

  reportPost: async (slug: string, reason: string, description?: string): Promise<void> => {
    await apiClient.post(`/posts/${slug}/report/`, {
      reason,
      description,
    });
  },

  likePost: async (slug: string): Promise<{ liked: boolean; likes_count: number }> => {
    const response = await apiClient.post<APIResponse<{ liked: boolean; likes_count: number }>>(`/posts/${slug}/like/`);
    return response.data.data!;
  },

  toggleLike: async (slug: string): Promise<{ liked: boolean; likes_count: number }> => {
    const response = await apiClient.post<APIResponse<{ liked: boolean; likes_count: number }>>(`/posts/${slug}/like/`);
    return response.data.data!;
  },
};
