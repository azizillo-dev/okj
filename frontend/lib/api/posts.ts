import { apiClient } from './client';
import { APIResponse, PaginatedResponse, Post } from './types';

export const postsApi = {
  getFeed: async (params?: { page?: number; type?: string }): Promise<PaginatedResponse<Post>> => {
    const response = await apiClient.get<APIResponse<PaginatedResponse<Post>>>('/posts/', { params });
    return response.data.data!;
  },

  createPost: async (postData: Record<string, any>): Promise<Post> => {
    const response = await apiClient.post<APIResponse<Post>>('/posts/', postData);
    return response.data.data!;
  },

  likePost: async (postId: string): Promise<{ liked: boolean; likes_count: number }> => {
    const response = await apiClient.post<APIResponse<{ liked: boolean; likes_count: number }>>(`/interactions/like/`, {
      post_id: postId,
    });
    return response.data.data!;
  },
};
