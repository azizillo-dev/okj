import { apiClient } from './client';
import { APIResponse, PassportAnalytics } from './types';

export interface HeatmapContribution {
  date: string;
  pagesRead: number;
  xpEarned: number;
}

export const passportApi = {
  getUserPassport: async (_okjId?: string): Promise<PassportAnalytics> => {
    const response = await apiClient.get<APIResponse<PassportAnalytics>>('/passport/');
    return response.data.data!;
  },
};

