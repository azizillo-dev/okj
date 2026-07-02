import { apiClient } from './client';
import { APIResponse, PaginatedResponse, Book } from './types';

export const booksApi = {
  getBooks: async (params?: { page?: number; search?: string }): Promise<PaginatedResponse<Book>> => {
    const response = await apiClient.get<APIResponse<PaginatedResponse<Book>>>('/books/', { params });
    return response.data.data!;
  },

  getBookBySlug: async (slug: string): Promise<Book> => {
    const response = await apiClient.get<APIResponse<Book>>(`/books/${slug}/`);
    return response.data.data!;
  },
};
