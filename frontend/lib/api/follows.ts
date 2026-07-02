import { apiClient } from './client';
import { APIResponse } from './types';

export const followsApi = {
  followUser: async (userId: string): Promise<any> => {
    const response = await apiClient.post<APIResponse<any>>(`/users/${userId}/follow/`);
    return response.data.data;
  },

  unfollowUser: async (userId: string): Promise<any> => {
    const response = await apiClient.post<APIResponse<any>>(`/users/${userId}/unfollow/`);
    return response.data.data;
  },
};
