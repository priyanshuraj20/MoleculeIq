/**
 * Shared HTTP Client Module using Axios.
 * 
 * Provides a pre-configured Axios instance to standardize base URL,
 * headers, and request timeouts across all frontend services.
 */

import axios from 'axios';
import { API_CONFIG } from '../config/api.config';

// Create configured Axios instance
export const apiClient = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: API_CONFIG.headers,
});
