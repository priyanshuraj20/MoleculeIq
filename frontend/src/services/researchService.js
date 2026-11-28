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
  repurposing_started:   'Discovering drug repurposing opportunities…',
  repurposing_completed: 'Drug repurposing indications identified.',
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

async function waitForBackendReady(onWakeNotice, signal, maxWaitMs = 55000) {
  const start = Date.now();
  let notified = false;
  const slowTimer = setTimeout(() => {
    notified = true;
    onWakeNotice('Backend server is starting up (may take 30–45s)...');
  }, 2000);

  try {
    while (Date.now() - start < maxWaitMs) {
      if (signal.aborted) return false;
      try {
        const res = await fetch(`${API_CONFIG.baseURL}/health`, { signal });
        if (res.ok) return true;
      } catch (err) {
        if (err?.name === 'AbortError') return false;
      }
      if (!notified) {
        notified = true;
        onWakeNotice('Backend server is starting up. Please wait...');
      }
      await new Promise((r) => setTimeout(r, 2500));
    }
    return false;
  } finally {
    clearTimeout(slowTimer);
  }
}

export function streamResearch(moleculeName, onStatusUpdate, onComplete, onError) {
  let es = null;
  let cancelled = false;
  const controller = new AbortController();

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
    'repurposing_started',
    'repurposing_completed',
    'aggregation_completed',
    'scoring_completed',
  ];

  waitForBackendReady(
    (msg) => {
      if (!cancelled) onStatusUpdate(msg, 'research_started');
    },
    controller.signal
  ).then((ready) => {
    if (cancelled) return;
    if (!ready) {
      onError('Backend server is still starting up. Please wait a few seconds and retry.');
      return;
    }

    const token = getAuthToken();
    let url = `${API_CONFIG.baseURL}/api/v1/research/stream?molecule_name=${encodeURIComponent(moleculeName)}`;
    if (token) {
      url += `&token=${encodeURIComponent(token)}`;
    }

    es = new EventSource(url, { withCredentials: true });

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
      onError('Backend server is starting up or temporarily busy. Please wait a moment and retry.');
      es.close();
    };
  });

  return {
    close: () => {
      cancelled = true;
      controller.abort();
      if (es) es.close();
    },
  };
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
