import axios, { AxiosError, InternalAxiosRequestConfig, AxiosRequestConfig } from 'axios';
import { APIResponse, APIErrorDetail } from './types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  timeout: 15000, // 15 seconds request timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Centralized Token Storage Helpers
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

// Retry Strategy Configuration
const MAX_RETRIES = 2;
const RETRY_DELAY = 1000;

// Response Interceptor: Handle JWT Refresh, Retry Strategy, and Standardized Errors
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
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
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean; _retryCount?: number };

    // Automatic JWT Refresh handling on 401
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/token/refresh/')) {
        setAccessToken(null);
        return Promise.reject(formatAPIError(error));
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
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
        }, { withCredentials: true, timeout: 10000 });

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

    // Exponential Backoff Retry for idempotent requests (GET) on Network Error or 5xx
    if (originalRequest && originalRequest.method === 'get' && (!error.response || error.response.status >= 500)) {
      originalRequest._retryCount = originalRequest._retryCount || 0;
      if (originalRequest._retryCount < MAX_RETRIES) {
        originalRequest._retryCount += 1;
        const backoffDelay = RETRY_DELAY * Math.pow(2, originalRequest._retryCount - 1);
        await new Promise((res) => setTimeout(res, backoffDelay));
        return apiClient(originalRequest);
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
  const status = error.response?.status;
  let defaultMsg = 'Server bilan bog\'lanishda xatolik yuz berdi.';
  if (status === 403) defaultMsg = 'Ushbu amalni bajarish uchun sizda ruxsat yo\'q (403 Forbidden).';
  else if (status === 404) defaultMsg = 'So\'ralgan ma\'lumot yoki sahifa topilmadi (404 Not Found).';
  else if (status && status >= 500) defaultMsg = 'Serverda ichki xatolik yuz berdi. Iltimos, keyinroq qayta urinib ko\'ring (5xx).';
  else if (error.code === 'ERR_NETWORK') defaultMsg = 'Tarmoq aloqasi mavjud emas. Offline rejimidasiz.';

  return {
    code: status ? `HTTP_${status}` : error.code === 'ECONNABORTED' ? 'TIMEOUT_ERROR' : 'NETWORK_ERROR',
    message: error.code === 'ECONNABORTED' ? 'So\'rov vaqti tugadi. Server javob bermadi.' : error.response?.data?.error?.message || defaultMsg,
    details: error.response?.data || null,
  };
};

// Typed Generic Helpers for Axios
export async function apiGet<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<APIResponse<T>>(url, config);
  return response.data.data !== undefined ? response.data.data : (response.data as unknown as T);
}

export async function apiPost<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.post<APIResponse<T>>(url, data, config);
  return response.data.data !== undefined ? response.data.data : (response.data as unknown as T);
}

export async function apiPut<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.put<APIResponse<T>>(url, data, config);
  return response.data.data !== undefined ? response.data.data : (response.data as unknown as T);
}

export async function apiPatch<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.patch<APIResponse<T>>(url, data, config);
  return response.data.data !== undefined ? response.data.data : (response.data as unknown as T);
}

export async function apiDelete<T = void>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<APIResponse<T>>(url, config);
  return response.data.data !== undefined ? response.data.data : (response.data as unknown as T);
}

// Universal Fetch Wrapper for Next.js 16 Server Components (RSC) and Streaming
export async function fetchAPI<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), 15000);

  try {
    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const res = await fetch(url, {
      ...options,
      headers,
      signal: controller.signal,
    });

    clearTimeout(id);

    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      const errDetail: APIErrorDetail = json?.error || {
        code: `HTTP_${res.status}`,
        message: json?.message || 'Server xatoligi.',
        details: json,
      };
      throw errDetail;
    }

    return (json.data !== undefined ? json.data : json) as T;
  } catch (error: unknown) {
    clearTimeout(id);
    if ((error as { name?: string })?.name === 'AbortError') {
      throw { code: 'TIMEOUT_ERROR', message: 'So\'rov vaqti tugadi.' } as APIErrorDetail;
    }
    throw error;
  }
}
