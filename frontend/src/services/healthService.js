/**
 * System Health Service Module.
 * 
 * Interacts with the backend GET /health endpoint to verify connectivity.
 */

import { apiClient } from './apiClient';

/**
 * Checks backend server health.
 * 
 * @returns {Promise<{ isConnected: boolean, data?: object, error?: string }>}
 */
export const checkBackendHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    // Verify response status and data payload
    if (response.status === 200 && response.data?.status === 'ok') {
      return { isConnected: true, data: response.data };
    }
    return { isConnected: false, error: 'Unexpected response status' };
  } catch (error) {
    // Catch connection refused, timeout, or network failure without throwing
    return { 
      isConnected: false, 
      error: error.message || 'Unable to reach backend server' 
    };
  }
};
