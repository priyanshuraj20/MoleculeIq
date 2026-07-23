/**
 * App.jsx — Root component.
 *
 * Checks if the backend is reachable on startup.
 * Shows a simple connected / offline status.
 */

import { useState, useEffect } from 'react';
import { checkBackendHealth } from './services/healthService';

export default function App() {
  // status can be: 'checking' | 'connected' | 'offline'
  const [status, setStatus] = useState('checking');
  const [checkedAt, setCheckedAt] = useState('');

  useEffect(() => {
    let alive = true;

    async function ping() {
      const result = await checkBackendHealth();
      if (!alive) return;
      setStatus(result.isConnected ? 'connected' : 'offline');
      setCheckedAt(new Date().toLocaleTimeString());
    }

    ping();
    return () => { alive = false; };
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0f1117' }}>
      <div style={{ width: 360, padding: '32px 28px', backgroundColor: '#16181d', border: '1px solid #2a2d35', borderRadius: 10 }}>

        {/* App name */}
        <p style={{ margin: '0 0 4px', fontSize: 13, color: '#6b7280', letterSpacing: '0.05em' }}>
          MOLECULEIQ
        </p>
        <h1 style={{ margin: '0 0 28px', fontSize: 20, fontWeight: 600, color: '#f3f4f6' }}>
          Startup Check
        </h1>

        {/* Status row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '14px 16px', backgroundColor: '#0f1117', borderRadius: 7, border: '1px solid #2a2d35' }}>
          <StatusDot status={status} />
          <span style={{ fontSize: 14, color: '#e5e7eb' }}>
            {status === 'checking' && 'Connecting to backend…'}
            {status === 'connected' && 'Backend is reachable'}
            {status === 'offline' && 'Backend not reachable'}
          </span>
        </div>

        {/* Checked at */}
        {checkedAt && (
          <p style={{ margin: '12px 0 0', fontSize: 12, color: '#4b5563' }}>
            Last checked at {checkedAt}
          </p>
        )}

        {/* Endpoint info */}
        <p style={{ margin: '24px 0 0', fontSize: 12, color: '#374151' }}>
          GET {import.meta.env.VITE_API_BASE_URL}/health
        </p>
      </div>
    </div>
  );
}

// Small colored dot to show status at a glance
function StatusDot({ status }) {
  const colors = {
    checking: '#f59e0b',
    connected: '#22c55e',
    offline:   '#ef4444',
  };
  return (
    <span style={{
      display: 'inline-block',
      width: 8,
      height: 8,
      borderRadius: '50%',
      flexShrink: 0,
      backgroundColor: colors[status] || '#6b7280',
    }} />
  );
}

