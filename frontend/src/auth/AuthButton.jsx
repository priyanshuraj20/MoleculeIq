import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from './useAuth';
import { LogIn, UserPlus, X, Loader2, Eye, EyeOff, Lock, Mail, User } from 'lucide-react';

export default function AuthButton({ label = 'Sign In', fullWidth = false, onSuccessCallback }) {
  const { login, register } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const resetForm = (nextMode = 'login') => {
    setMode(nextMode);
    setErrorMsg(null);
    setPassword('');
  };

  const handleOpen = () => {
    setErrorMsg(null);
    setIsOpen(true);
  };

  const handleClose = () => {
    if (isSubmitting) return;
    setIsOpen(false);
    setErrorMsg(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg(null);
    setIsSubmitting(true);

    try {
      if (mode === 'register') {
        await register(name, email, password);
      } else {
        await login(email, password);
      }
      setIsOpen(false);
      setName('');
      setEmail('');
      setPassword('');
      if (onSuccessCallback) onSuccessCallback();
    } catch (err) {
      setErrorMsg(err.message || 'Authentication failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={handleOpen}
        className={`inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold text-white rounded-lg transition-all cursor-pointer shadow-sm ${
          fullWidth ? 'w-full' : ''
        }`}
        style={{ backgroundColor: 'var(--color-blue)' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-blue-hover)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-blue)';
        }}
      >
        <LogIn className="w-4 h-4" />
        {label}
      </button>

      {isOpen &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs"
            onClick={handleClose}
          >
            <div
              className="w-full max-w-md bg-white rounded-2xl border shadow-xl p-6 space-y-5 animate-fade-up"
              style={{ borderColor: 'var(--color-border)' }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="text-lg font-bold" style={{ color: 'var(--color-text)' }}>
                    {mode === 'login' ? 'Sign in to MoleculeIQ' : 'Create your account'}
                  </h2>
                  <p className="text-xs mt-1" style={{ color: 'var(--color-text-faint)' }}>
                    {mode === 'login'
                      ? 'Access AI drug repurposing & clinical intelligence.'
                      : 'Start researching molecules with AI pipelines.'}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleClose}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
                  aria-label="Close modal"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Mode Switcher */}
              <div className="grid grid-cols-2 p-1 bg-slate-100 rounded-lg">
                <button
                  type="button"
                  onClick={() => resetForm('login')}
                  className={`py-1.5 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                    mode === 'login' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Sign In
                </button>
                <button
                  type="button"
                  onClick={() => resetForm('register')}
                  className={`py-1.5 text-xs font-semibold rounded-md transition-all cursor-pointer ${
                    mode === 'register' ? 'bg-white shadow-xs text-slate-900' : 'text-slate-500 hover:text-slate-700'
                  }`}
                >
                  Create Account
                </button>
              </div>

              {errorMsg && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-xs font-medium text-red-700">
                  {errorMsg}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-3.5">
                {mode === 'register' && (
                  <div>
                    <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--color-text)' }}>
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        required
                        minLength={2}
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Dr. Jane Doe"
                        className="w-full h-10 pl-9 pr-3 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
                        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--color-text)' }}>
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      className="w-full h-10 pl-9 pr-3 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
                      style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold mb-1" style={{ color: 'var(--color-text)' }}>
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      minLength={mode === 'register' ? 6 : 1}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={mode === 'register' ? 'Minimum 6 characters' : 'Enter your password'}
                      className="w-full h-10 pl-9 pr-10 text-sm border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
                      style={{ borderColor: 'var(--color-border)', color: 'var(--color-text)' }}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((prev) => !prev)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full h-10 flex items-center justify-center gap-2 text-sm font-semibold text-white rounded-lg transition-all disabled:opacity-60 cursor-pointer"
                  style={{ backgroundColor: 'var(--color-blue)' }}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                    </>
                  ) : mode === 'login' ? (
                    <>
                      <LogIn className="w-4 h-4" />
                      Sign In
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-4 h-4" />
                      Create Account
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
