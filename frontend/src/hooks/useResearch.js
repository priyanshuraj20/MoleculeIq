import { useState, useRef, useCallback, useEffect } from 'react';
import { streamResearch } from '../services/researchService';

/**
 * useResearch
 * Manages research execution lifecycle: idle -> loading -> success | error.
 */
export function useResearch() {
  const [status, setStatus]               = useState('idle');
  const [statusMessage, setStatusMessage] = useState('');
  const [lastEvent, setLastEvent]         = useState('');
  const [data, setData]                   = useState(null);
  const [errorMessage, setErrorMessage]   = useState('');

  const esRef = useRef(null);

  const reset = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }
    setStatus('idle');
    setStatusMessage('');
    setLastEvent('');
    setData(null);
    setErrorMessage('');
  }, []);

  const runResearch = useCallback((moleculeName) => {
    if (!moleculeName?.trim()) return;

    if (esRef.current) {
      esRef.current.close();
      esRef.current = null;
    }

    setStatus('loading');
    setStatusMessage('Initializing research pipeline…');
    setLastEvent('research_started');
    setData(null);
    setErrorMessage('');

    const es = streamResearch(
      moleculeName.trim(),
      (message, eventName) => {
        setStatusMessage(message);
        if (eventName) setLastEvent(eventName);
      },
      (researchContext) => {
        setData(researchContext);
        setStatus('success');
        setLastEvent('research_completed');
        esRef.current = null;
      },
      (message) => {
        setErrorMessage(message);
        setStatus('error');
        setLastEvent('research_failed');
        esRef.current = null;
      }
    );

    esRef.current = es;
  }, []);

  // Cleanup EventSource connection on unmount
  useEffect(() => {
    return () => {
      if (esRef.current) {
        esRef.current.close();
        esRef.current = null;
      }
    };
  }, []);

  return { status, statusMessage, lastEvent, data, errorMessage, runResearch, reset };
}
