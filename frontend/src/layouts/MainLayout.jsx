import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import BackButton from '../components/BackButton';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function MainLayout() {
  const location = useLocation();
  const isHome = location.pathname === '/';

  return (
    <div
      className="min-h-screen flex flex-col font-sans antialiased"
      style={{ backgroundColor: 'var(--color-bg)', color: 'var(--color-text)' }}
    >
      <Navbar />
      {!isHome && (
        <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 pt-3 pb-1">
          <BackButton />
        </div>
      )}
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
