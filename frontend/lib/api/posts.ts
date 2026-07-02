import { apiClient } from './client';
import { APIResponse, PaginatedResponse, Post, Comment } from './types';

export const postsApi = {
  getFeed: async (params?: { page?: number; type?: string }): Promise<PaginatedResponse<Post>> => {
    const response = await apiClient.get<APIResponse<PaginatedResponse<Post>>>('/posts/', { params });
    return response.data.data!;
  },

  getPostById: async (postId: string): Promise<Post> => {
    const response = await apiClient.get<APIResponse<Post>>(`/posts/${postId}/`);
    return response.data.data!;
  },

  getPostComments: async (postId: string): Promise<Comment[]> => {
    const response = await apiClient.get<APIResponse<Comment[]>>(`/comments/`, {
      params: { post_id: postId },
    });
    return response.data.data || [];
  },

  addComment: async (postId: string, content: string, parentId?: string): Promise<Comment> => {
    const response = await apiClient.post<APIResponse<Comment>>(`/comments/`, {
      post_id: postId,
      content,
      parent_id: parentId || null,
    });
    return response.data.data!;
  },

  createPost: async (postData: Record<string, any>): Promise<Post> => {
    const response = await apiClient.post<APIResponse<Post>>('/posts/', postData);
    return response.data.data!;
  },

  deletePost: async (postId: string): Promise<void> => {
    await apiClient.delete(`/posts/${postId}/`);
  },

  reportPost: async (postId: string, reason: string, description?: string): Promise<void> => {
    await apiClient.post(`/moderation/reports/`, {
      content_type: 'POST',
      target_id: postId,
      reason,
      description,
    });
  },

  likePost: async (postId: string): Promise<{ liked: boolean; likes_count: number }> => {
    const response = await apiClient.post<APIResponse<{ liked: boolean; likes_count: number }>>(`/interactions/like/`, {
      post_id: postId,
    });
    return response.data.data!;
  },
};
