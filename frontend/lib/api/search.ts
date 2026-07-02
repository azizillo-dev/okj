import { apiClient } from './client';
import { APIResponse } from './types';

export interface GlobalSearchResult {
  count: number;
  books: any[];
  users: any[];
  posts: any[];
}

export const searchApi = {
  globalSearch: async (query: string, type?: string): Promise<GlobalSearchResult> => {
    const response = await apiClient.get<APIResponse<GlobalSearchResult>>('/search/', {
      params: { q: query, type },
    });
    return response.data.data!;
  },
};
