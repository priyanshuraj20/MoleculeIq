import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import ResearchPage from './pages/ResearchPage';
import ReportPage from './pages/ReportPage';
import MedicalSuggestionPage from './pages/MedicalSuggestionPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './auth/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<LandingPage />} />
          <Route
            path="research"
            element={
              <ProtectedRoute>
                <ResearchPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="suggestions"
            element={
              <ProtectedRoute>
                <MedicalSuggestionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="medical-suggestions"
            element={
              <ProtectedRoute>
                <MedicalSuggestionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="report"
            element={
              <ProtectedRoute>
                <ReportPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
