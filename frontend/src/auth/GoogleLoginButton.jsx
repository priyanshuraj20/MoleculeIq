import React, { useState } from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from './useAuth';
import { Loader2 } from 'lucide-react';

export default function GoogleLoginButton({ onSuccessCallback }) {
  const { loginWithGoogle } = useAuth();
  const [isAuthenticating, setIsAuthenticating] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) return;

    setIsAuthenticating(true);
    setErrorMsg(null);

    try {
      await loginWithGoogle(credentialResponse.credential);
      if (onSuccessCallback) {
        onSuccessCallback();
      }
    } catch (err) {
      console.error('Login error:', err);
      setErrorMsg(err.message || 'Failed to sign in with Google.');
    } finally {
      setIsAuthenticating(false);
    }
  };

  const handleError = () => {
    console.error('Google OAuth Popup Failed');
    setErrorMsg('Google Sign-In was cancelled or failed.');
  };

  return (
    <div className="flex flex-col items-center gap-1.5">
      {isAuthenticating ? (
        <div className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          Signing in...
        </div>
      ) : (
        <div className="google-btn-wrapper select-none">
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={handleError}
            useOneTap={false}
            shape="rectangular"
            theme="outline"
            size="large"
            text="continue_with"
            locale="en"
          />
        </div>
      )}

      {errorMsg && (
        <span className="text-xs text-red-600 font-medium">{errorMsg}</span>
      )}
    </div>
  );
}
