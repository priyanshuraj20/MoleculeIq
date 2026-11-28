/**
 * Centralized API Configuration Module.
 * 
 * Reads the backend base URL from Vite environment variables (VITE_API_BASE_URL).
 * Falls back to http://127.0.0.1:8000 if not explicitly defined in .env.
 */

export const API_CONFIG = {
  // Vite exposes env variables via import.meta.env
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 60000, // 60s timeout to accommodate backend cold starts
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
};
