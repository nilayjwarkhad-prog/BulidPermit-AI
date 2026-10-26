import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoadingSpinner } from './components/common/LoadingSpinner';

// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { CreateProjectPage } from './pages/CreateProjectPage';
import { ProjectOverviewPage } from './pages/ProjectOverviewPage';
import { ProjectDocumentsPage } from './pages/ProjectDocumentsPage';
import { ProjectAnalysisPage } from './pages/ProjectAnalysisPage';
import { ProjectFindingsPage } from './pages/ProjectFindingsPage';
import { ProjectChecklistPage } from './pages/ProjectChecklistPage';
import { ProjectReportsPage } from './pages/ProjectReportsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Pages */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected SaaS App Pages */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/new"
              element={
                <ProtectedRoute>
                  <CreateProjectPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id"
              element={
                <ProtectedRoute>
                  <ProjectOverviewPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id/documents"
              element={
                <ProtectedRoute>
                  <ProjectDocumentsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id/analysis"
              element={
                <ProtectedRoute>
                  <ProjectAnalysisPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id/findings"
              element={
                <ProtectedRoute>
                  <ProjectFindingsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id/checklist"
              element={
                <ProtectedRoute>
                  <ProjectChecklistPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/projects/:id/reports"
              element={
                <ProtectedRoute>
                  <ProjectReportsPage />
                </ProtectedRoute>
              }
            />

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
