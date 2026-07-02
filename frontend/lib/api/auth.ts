import { apiClient } from './client';
import { APIResponse, User } from './types';

export interface LoginPayload {
  username?: string;
  phone_number?: string;
  password?: string;
  otp?: string;
}

export interface RegisterPayload {
  username?: string;
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
    const requestPayload = {
      phone_number: payload.phone_number || payload.username,
      password: payload.password,
      device_id: 'web_browser',
      device_type: 'WEB',
    };
    const response = await apiClient.post<APIResponse<AuthTokensResponse>>('/auth/login/password/', requestPayload);
    return response.data.data || (response.data as unknown as AuthTokensResponse);
  },

  register: async (payload: RegisterPayload): Promise<{ message: string; user_id?: string }> => {
    const requestPayload = {
      phone_number: payload.phone_number || payload.username,
      first_name: payload.first_name,
      last_name: payload.last_name,
    };
    const response = await apiClient.post<APIResponse<{ message: string; user_id?: string }>>('/accounts/register/', requestPayload);
    return response.data.data || { message: 'Tasdiqlash kodi yuborildi' };
  },

  requestOtp: async (phoneOrUsername: string): Promise<any> => {
    const response = await apiClient.post<APIResponse<any>>('/auth/otp/request/', {
      phone_number: phoneOrUsername,
      purpose: 'LOGIN',
    });
    return response.data.data;
  },

  verifyOtp: async (phoneOrUsername: string, otp: string): Promise<AuthTokensResponse> => {
    const response = await apiClient.post<APIResponse<AuthTokensResponse>>('/auth/otp/verify/', {
      phone_number: phoneOrUsername,
      code: otp,
      device_id: 'web_browser',
      device_type: 'WEB',
    });
    return response.data.data || (response.data as unknown as AuthTokensResponse);
  },

  logout: async (refreshToken?: string | null): Promise<void> => {
    await apiClient.post('/auth/logout/', { refresh: refreshToken, device_id: 'web_browser' }).catch(() => {});
  },

  logoutAll: async (): Promise<void> => {
    await apiClient.post('/auth/logout/all/').catch(() => {});
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<APIResponse<User>>('/accounts/me/');
    return response.data.data!;
  },

  updateProfile: async (payload: Partial<{ first_name: string; last_name: string; bio: string }>): Promise<User> => {
    const response = await apiClient.patch<APIResponse<User>>('/accounts/me/', payload);
    return response.data.data!;
  },

  updateAvatar: async (avatarDataUrl: string): Promise<User> => {
    const response = await apiClient.patch<APIResponse<User>>('/accounts/me/', { avatar_url: avatarDataUrl });
    return response.data.data!;
  },
};
