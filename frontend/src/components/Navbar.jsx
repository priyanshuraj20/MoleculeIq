import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import MoleculeIQLogo from './MoleculeIQLogo';
import { useAuth } from '../auth/useAuth';
import GoogleLoginButton from '../auth/GoogleLoginButton';
import { LogOut, User as UserIcon, ChevronDown } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [imgError, setImgError] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    navigate('/', { replace: true });
  };

  const initialLetter = user?.name ? user.name.charAt(0).toUpperCase() : 'U';

  return (
    <header
      className="sticky top-0 z-50 bg-white border-b"
      style={{ borderColor: 'var(--color-border)', boxShadow: 'var(--shadow-card)' }}
    >
      <div className="w-full flex items-center justify-between px-8 lg:px-12 py-3">

        {/* ── Left: Cropped Brand Logo ──────────────────────────── */}
        <Link to="/" className="flex items-center gap-3 select-none shrink-0">
          <MoleculeIQLogo
            style={{ height: '64px', width: 'auto', display: 'block' }}
          />
        </Link>

        {/* ── Right: Auth Section ────────────────────────────────── */}
        <div className="flex items-center gap-3 shrink-0">
          {!isAuthenticated ? (
            <GoogleLoginButton />
          ) : (
            <div className="relative" ref={dropdownRef}>
              {/* Profile Avatar Button */}
              <button
                type="button"
                onClick={() => setDropdownOpen((prev) => !prev)}
                className="flex items-center gap-2 p-1 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer border border-transparent hover:border-slate-200"
                aria-label="User menu"
              >
                {user?.picture && !imgError ? (
                  <img
                    src={user.picture}
                    alt={user.name || 'User'}
                    className="w-9 h-9 rounded-full object-cover border"
                    style={{ borderColor: 'var(--color-border)' }}
                    onError={() => setImgError(true)}
                    referrerPolicy="no-referrer"
                  />
                ) : (
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-white text-sm"
                    style={{ backgroundColor: 'var(--color-blue)' }}
                  >
                    {initialLetter}
                  </div>
                )}
                <span className="hidden sm:inline-block text-sm font-semibold max-w-[120px] truncate" style={{ color: 'var(--color-text)' }}>
                  {user?.name || 'Account'}
                </span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-500" />
              </button>

              {/* Minimal Profile Dropdown Menu */}
              {dropdownOpen && (
                <div
                  className="absolute right-0 mt-2 w-64 bg-white border rounded-xl shadow-lg py-3 px-4 z-50 space-y-3 animate-fade-up"
                  style={{ borderColor: 'var(--color-border)' }}
                >
                  {/* User Profile Card */}
                  <div className="flex items-center gap-3">
                    {user?.picture && !imgError ? (
                      <img
                        src={user.picture}
                        alt={user.name}
                        className="w-11 h-11 rounded-full object-cover border shrink-0"
                        style={{ borderColor: 'var(--color-border-light)' }}
                        onError={() => setImgError(true)}
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <div
                        className="w-11 h-11 rounded-full flex items-center justify-center font-bold text-white text-base shrink-0"
                        style={{ backgroundColor: 'var(--color-blue)' }}
                      >
                        {initialLetter}
                      </div>
                    )}
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold truncate" style={{ color: 'var(--color-text)' }}>
                        {user?.name || 'User'}
                      </p>
                      <p className="text-xs truncate mt-0.5" style={{ color: 'var(--color-text-faint)' }}>
                        {user?.email || ''}
                      </p>
                    </div>
                  </div>

                  {/* Divider */}
                  <div className="border-t" style={{ borderColor: 'var(--color-border-light)' }} />

                  {/* Logout Button */}
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="w-full flex items-center justify-start gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors cursor-pointer text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="w-4 h-4 text-red-600 shrink-0" />
                    Log out
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
