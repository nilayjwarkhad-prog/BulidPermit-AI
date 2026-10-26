import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { ShieldCheck, Plus, LogOut, FolderKanban } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { AIHealthStatus } from '../../types';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [aiHealth, setAiHealth] = useState<AIHealthStatus | null>(null);

  useEffect(() => {
    api.getAIHealth()
      .then(setAiHealth)
      .catch(() => setAiHealth({ available: false, ai_enabled: false, model: 'N/A', message: 'Offline', installed_models: [] }));
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isProjectsActive = location.pathname.startsWith('/projects') || location.pathname === '/dashboard';

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200/90 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        
        {/* Brand Logo & Primary Nav */}
        <div className="flex items-center gap-8">
          <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm shadow-xs">
              BP
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-slate-900 text-sm tracking-tight leading-tight">
                BuildPermit <span className="text-brand-600 font-normal">AI</span>
              </span>
            </div>
          </Link>

          {user && (
            <nav className="hidden sm:flex items-center gap-1">
              <Link
                to="/dashboard"
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                  isProjectsActive 
                    ? 'bg-slate-100 text-slate-900 font-semibold' 
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Projects
              </Link>
            </nav>
          )}
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              {/* Subtle AI Engine Status */}
              <div 
                title={aiHealth?.available ? `AI Model: ${aiHealth.model}` : 'Deterministic analysis active'}
                className="hidden md:flex items-center gap-1.5 px-2 py-1 rounded bg-slate-50 border border-slate-200 text-[11px] text-slate-500 font-mono"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${aiHealth?.available ? 'bg-emerald-500' : 'bg-slate-400'}`}></span>
                <span>{aiHealth?.available ? aiHealth.model : 'Deterministic'}</span>
              </div>

              <Link
                to="/projects/new"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-xs transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Project</span>
              </Link>

              <div className="h-4 w-px bg-slate-200 mx-1"></div>

              {/* User Menu */}
              <div className="flex items-center gap-2">
                <div 
                  className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-700 font-semibold text-xs"
                  title={user.email}
                >
                  {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </div>
                <span className="hidden lg:inline text-xs text-slate-600 max-w-[120px] truncate">{user.email}</span>
                <button
                  onClick={handleLogout}
                  title="Sign out"
                  className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="px-3 py-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 rounded-md transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-3.5 py-1.5 text-xs font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-md shadow-xs transition-colors"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};
