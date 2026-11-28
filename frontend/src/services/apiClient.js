/**
 * Shared HTTP Client Module using Axios.
 *
 * Provides a pre-configured Axios instance with Bearer token injection
 * and clean cold-start / network error normalization.
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

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    if (!error.response || status === 502 || status === 503 || status === 504) {
      error.friendlyMessage = 'Backend server is starting up. Please wait a moment and try again.';
    } else {
      error.friendlyMessage =
        error.response?.data?.detail || error.message || 'An unexpected error occurred.';
    }
    return Promise.reject(error);
  }
);
