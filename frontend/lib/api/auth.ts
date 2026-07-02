import { apiClient } from './client';
import { APIResponse, User } from './types';

export interface LoginPayload {
  username: string;
  password?: string;
  otp?: string;
}

export interface RegisterPayload {
  username: string;
  phone_number?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  password?: string;
}

export interface AuthTokensResponse {
  access: string;
  refresh: string;
  user?: User;
}

export const authApi = {
  login: async (payload: LoginPayload): Promise<AuthTokensResponse> => {
    const response = await apiClient.post<APIResponse<AuthTokensResponse>>('/auth/token/', payload);
    return response.data.data || (response.data as unknown as AuthTokensResponse);
  },

  register: async (payload: RegisterPayload): Promise<{ message: string; user_id?: string }> => {
    const response = await apiClient.post<APIResponse<{ message: string; user_id?: string }>>('/auth/register/', payload);
    return response.data.data || { message: 'Tasdiqlash kodi yuborildi' };
  },

  verifyOtp: async (username: string, otp: string): Promise<AuthTokensResponse> => {
    const response = await apiClient.post<APIResponse<AuthTokensResponse>>('/auth/verify-otp/', { username, otp });
    return response.data.data || (response.data as unknown as AuthTokensResponse);
  },

  logout: async (refreshToken?: string | null): Promise<void> => {
    await apiClient.post('/auth/logout/', { refresh: refreshToken }).catch(() => {});
  },

  logoutAll: async (): Promise<void> => {
    await apiClient.post('/auth/logout-all/').catch(() => {});
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<APIResponse<User>>('/users/me/');
    return response.data.data!;
  },

  updateProfile: async (payload: Partial<{ first_name: string; last_name: string; bio: string }>): Promise<User> => {
    const response = await apiClient.patch<APIResponse<User>>('/users/me/', payload);
    return response.data.data!;
  },

  updateAvatar: async (avatarDataUrl: string): Promise<User> => {
    const response = await apiClient.patch<APIResponse<User>>('/users/me/avatar/', { avatar: avatarDataUrl });
    return response.data.data!;
  },
};
