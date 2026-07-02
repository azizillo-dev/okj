import { apiClient } from './client';
import { APIResponse, PassportAnalytics } from './types';

export const passportApi = {
  getUserPassport: async (okjId: string): Promise<PassportAnalytics> => {
    const response = await apiClient.get<APIResponse<PassportAnalytics>>(`/passport/${okjId}/`);
    return response.data.data!;
  },

  followUser: async (userId: string): Promise<{ following: boolean }> => {
    const response = await apiClient.post<APIResponse<{ following: boolean }>>(`/follows/toggle/`, {
      target_id: userId,
    });
    return response.data.data!;
  },
};
