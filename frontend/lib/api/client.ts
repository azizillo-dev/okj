import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { APIResponse, APIErrorDetail } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Centralized Token Storage Helpers (Client-side fallback when not pure HttpOnly)
let accessToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  accessToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('okj_access_token', token);
    } else {
      localStorage.removeItem('okj_access_token');
    }
  }
};

export const getAccessToken = (): string | null => {
  if (accessToken) return accessToken;
  if (typeof window !== 'undefined') {
    return localStorage.getItem('okj_access_token');
  }
  return null;
};

// Request Interceptor: Attach Access Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle JWT Refresh and Standardized Errors
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<APIResponse>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Automatic JWT Refresh handling on 401
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/token/refresh/')) {
        setAccessToken(null);
        return Promise.reject(formatAPIError(error));
      }

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('okj_refresh_token') : null;
        const res = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        }, { withCredentials: true });

        const newToken = res.data?.data?.access || res.data?.access;
        if (newToken) {
          setAccessToken(newToken);
          processQueue(null, newToken);
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          return apiClient(originalRequest);
        }
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        setAccessToken(null);
        if (typeof window !== 'undefined') {
          localStorage.removeItem('okj_refresh_token');
        }
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(formatAPIError(error));
  }
);

// Centralized Error Formatter conforming to OKJ backend standard
export const formatAPIError = (error: AxiosError<APIResponse>): APIErrorDetail => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  return {
    code: error.response?.status ? `HTTP_${error.response.status}` : 'NETWORK_ERROR',
    message: error.response?.data?.error?.message || error.message || 'Server bilan bog\'lanishda xatolik yuz berdi.',
    details: error.response?.data || null,
  };
};
