import { apiClient } from './client';
import { APIResponse, PassportAnalytics } from './types';

export interface HeatmapContribution {
  date: string;
  pagesRead: number;
  xpEarned: number;
}

export const passportApi = {
  getUserPassport: async (okjId: string): Promise<PassportAnalytics> => {
    const response = await apiClient.get<APIResponse<PassportAnalytics>>(`/passport/${okjId}/`);
    return response.data.data!;
  },

  getHeatmap: async (okjId: string, year?: number): Promise<HeatmapContribution[]> => {
    const response = await apiClient.get<APIResponse<HeatmapContribution[]>>(`/passport/${okjId}/heatmap/`, {
      params: { year },
    });
    return response.data.data || [];
  },

  spinWheel: async (): Promise<{ prize_index: number; prize_label: string; xp_won: number }> => {
    const response = await apiClient.post<APIResponse<{ prize_index: number; prize_label: string; xp_won: number }>>('/passport/spin-wheel/');
    return response.data.data!;
  },

  followUser: async (userId: string): Promise<{ following: boolean }> => {
    const response = await apiClient.post<APIResponse<{ following: boolean }>>(`/follows/toggle/`, {
      target_id: userId,
    });
    return response.data.data!;
  },
};
