import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './useAuth';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-3" style={{ backgroundColor: 'var(--color-bg)' }}>
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: 'var(--color-blue)' }} />
        <p className="text-sm font-medium" style={{ color: 'var(--color-text-muted)' }}>
          Verifying session...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to landing page with return url state
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return children;
}
