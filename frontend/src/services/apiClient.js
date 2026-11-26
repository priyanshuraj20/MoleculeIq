/**
 * Shared HTTP Client Module using Axios.
 *
 * Provides a pre-configured Axios instance with Bearer token injection
 * and automatic 401 refresh-token retry.
 */

import axios from 'axios';
import { API_CONFIG } from '../config/api.config';

export const apiClient = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: API_CONFIG.headers,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise = null;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          if (!refreshPromise) {
            refreshPromise = axios
              .post(
                `${API_CONFIG.baseURL}/api/auth/refresh`,
                { refresh_token: refreshToken },
                { withCredentials: true }
              )
              .finally(() => {
                refreshPromise = null;
              });
          }
          const { data } = await refreshPromise;
          if (data?.access_token) {
            localStorage.setItem('access_token', data.access_token);
            if (data.refresh_token) {
              localStorage.setItem('refresh_token', data.refresh_token);
            }
            originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
            return apiClient(originalRequest);
          }
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
    }
    return Promise.reject(error);
  }
);
