/**
 * researchService.js
 *
 * Manages SSE streaming connection to the backend research pipeline.
 * Endpoint: GET /api/v1/research/stream?molecule_name={name}
 */

import { API_CONFIG } from '../config/api.config';

export const SSE_STATUS_MESSAGES = {
  research_started:      'Initializing research pipeline…',
  clinical_started:      'Collecting clinical evidence…',
  clinical_completed:    'Clinical evidence collected.',
  literature_started:    'Searching scientific literature…',
  literature_completed:  'Scientific literature indexed.',
  market_started:        'Analyzing market intelligence…',
  market_completed:      'Market intelligence gathered.',
  patent_started:        'Reviewing patent landscape…',
  patent_completed:      'Patent landscape reviewed.',
  aggregation_completed: 'Aggregating research domains…',
  scoring_completed:     'Calculating opportunity score…',
  research_completed:    'Research complete.',
  research_failed:       'Research pipeline encountered an error.',
};

/**
 * Helper to retrieve stored access_token from localStorage
 */
function getAuthToken() {
  return localStorage.getItem('access_token') || '';
}

/**
 * streamResearch
 */
export function streamResearch(moleculeName, onStatusUpdate, onComplete, onError) {
  const token = getAuthToken();
  let url = `${API_CONFIG.baseURL}/api/v1/research/stream?molecule_name=${encodeURIComponent(moleculeName)}`;
  if (token) {
    url += `&token=${encodeURIComponent(token)}`;
  }

  // EventSource automatically includes cookies if credentials are sent in same origin or with credentials setting
  const es = new EventSource(url, { withCredentials: true });

  const progressEvents = [
    'research_started',
    'clinical_started',
    'clinical_completed',
    'literature_started',
    'literature_completed',
    'market_started',
    'market_completed',
    'patent_started',
    'patent_completed',
    'aggregation_completed',
    'scoring_completed',
  ];

  progressEvents.forEach((eventName) => {
    es.addEventListener(eventName, () => {
      const msg = SSE_STATUS_MESSAGES[eventName] ?? eventName;
      onStatusUpdate(msg, eventName);
    });
  });

  es.addEventListener('research_completed', (e) => {
    try {
      const researchContext = JSON.parse(e.data);
      onStatusUpdate(SSE_STATUS_MESSAGES.research_completed, 'research_completed');
      onComplete(researchContext);
    } catch {
      onError('Failed to parse research results from server.');
    }
    es.close();
  });

  es.addEventListener('research_failed', (e) => {
    try {
      const parsed = JSON.parse(e.data);
      onError(parsed.error ?? 'Research pipeline failed. Please try again.');
    } catch {
      onError('Research pipeline failed. Please try again.');
    }
    es.close();
  });

  es.onerror = () => {
    onError('Unable to connect to the research backend. Please ensure the server is running.');
    es.close();
  };

  return es;
}

/**
 * Downloads standardized JSON report export.
 */
export async function downloadJsonReport(moleculeName) {
  const token = getAuthToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_CONFIG.baseURL}/api/research/json`;
  const response = await fetch(url, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: JSON.stringify({ molecule_name: moleculeName }),
  });

  if (!response.ok) {
    throw new Error(`Server returned HTTP ${response.status}`);
  }

  const data = await response.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `${moleculeName.replace(/\s+/g, '_')}_Research_Report.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Downloads C-suite Executive PDF Report.
 */
export async function downloadPdfReport(moleculeName) {
  const token = getAuthToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_CONFIG.baseURL}/api/research/pdf?molecule_name=${encodeURIComponent(moleculeName)}`;
  const response = await fetch(url, {
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error(`Server returned HTTP ${response.status}`);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = `${moleculeName.replace(/\s+/g, '_')}_Executive_Report.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}
