/**
 * researchService.js
 *
 * Manages SSE streaming connection to the backend research pipeline.
 * Endpoint: GET /api/v1/research/stream?molecule_name={name}
 *
 * SSE event sequence (deterministic, 12 events):
 *   1.  research_started
 *   2.  clinical_started
 *   3.  clinical_completed     → data: { trials_found, total_found }
 *   4.  literature_started
 *   5.  literature_completed   → data: { papers_found, total_found }
 *   6.  market_started
 *   7.  market_completed       → data: { points_found, global_size_usd_mn }
 *   8.  patent_started
 *   9.  patent_completed       → data: { records_found, fto_summary }
 *  10.  aggregation_completed  → data: { domains_available }
 *  11.  scoring_completed      → data: { overall_score, confidence_score }
 *  12.  research_completed     → data: full ResearchContext JSON
 *  ERR. research_failed        → data: { error }
 */

import { API_CONFIG } from '../config/api.config';

// ─── SSE event → human-friendly status message mapping ───────────────────────

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
 * streamResearch
 *
 * Opens an SSE connection to the backend and calls the provided callbacks
 * as events arrive.
 *
 * @param {string}   moleculeName
 * @param {function} onStatusUpdate  (message: string, eventName: string) => void
 * @param {function} onComplete      (researchContext: object) => void
 * @param {function} onError         (message: string) => void
 * @returns {EventSource} — caller must call .close() to clean up
 */
export function streamResearch(moleculeName, onStatusUpdate, onComplete, onError) {
  const url = `${API_CONFIG.baseURL}/api/v1/research/stream?molecule_name=${encodeURIComponent(moleculeName)}`;

  const es = new EventSource(url);

  // ── Progress events ────────────────────────────────────────────────────────
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

  // ── Terminal: success ──────────────────────────────────────────────────────
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

  // ── Terminal: backend pipeline failure ────────────────────────────────────
  es.addEventListener('research_failed', (e) => {
    try {
      const parsed = JSON.parse(e.data);
      onError(parsed.error ?? 'Research pipeline failed. Please try again.');
    } catch {
      onError('Research pipeline failed. Please try again.');
    }
    es.close();
  });

  // ── Network / connection error ─────────────────────────────────────────────
  es.onerror = () => {
    onError('Unable to connect to the research backend. Please ensure the server is running.');
    es.close();
  };

  return es;
}
