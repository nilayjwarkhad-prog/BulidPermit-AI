import React from 'react';
import { NavLink, useParams, useLocation, Link } from 'react-router-dom';
import { MapPin, Building2, FileText, CheckSquare, AlertTriangle, FileSpreadsheet, ChevronRight } from 'lucide-react';
import { Project } from '../../types';
import { StatusBadge } from '../common/StatusBadge';

interface ProjectHeaderProps {
  project: Project;
}

export const ProjectHeader: React.FC<ProjectHeaderProps> = ({ project }) => {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();

  const isReviewActive = location.pathname.includes('/findings') || location.pathname.includes('/analysis');

  const tabs = [
    { 
      to: `/projects/${id}`, 
      label: 'Overview', 
      icon: Building2, 
      end: true,
      isActive: location.pathname === `/projects/${id}`
    },
    { 
      to: `/projects/${id}/documents`, 
      label: 'Documents', 
      icon: FileText, 
      count: project.document_count,
      isActive: location.pathname.startsWith(`/projects/${id}/documents`)
    },
    { 
      to: `/projects/${id}/findings`, 
      label: 'Review', 
      icon: AlertTriangle, 
      count: project.open_findings_count, 
      alert: (project.open_findings_count || 0) > 0,
      isActive: isReviewActive
    },
    { 
      to: `/projects/${id}/checklist`, 
      label: 'Checklist', 
      icon: CheckSquare,
      isActive: location.pathname.startsWith(`/projects/${id}/checklist`)
    },
    { 
      to: `/projects/${id}/reports`, 
      label: 'Reports', 
      icon: FileSpreadsheet,
      isActive: location.pathname.startsWith(`/projects/${id}/reports`)
    },
  ];

  return (
    <div className="bg-white border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-5">
        
        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-2.5">
          <Link to="/dashboard" className="hover:text-slate-900 transition-colors">
            Projects
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-900 font-medium truncate max-w-[240px] sm:max-w-md">{project.name}</span>
        </div>

        {/* Project Header Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">{project.name}</h1>
            <StatusBadge status={project.jurisdiction_supported} type="jurisdiction" size="sm" />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded font-mono">
              {project.jurisdiction_id}
            </span>
          </div>
        </div>

        {/* Property Specs Meta Line */}
        <div className="flex flex-wrap items-center gap-y-1.5 gap-x-4 text-xs text-slate-600 pb-4">
          <div className="flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{project.address}, {project.city}, {project.state_region}</span>
          </div>
          <span className="text-slate-300">•</span>
          <div className="flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span>{project.project_type} ({project.building_type})</span>
          </div>
          {project.area && (
            <>
              <span className="text-slate-300">•</span>
              <span className="text-slate-500">
                {project.area.toLocaleString()} {project.area_unit.replace('_', ' ')}
              </span>
            </>
          )}
        </div>

        {/* 5 Primary Task Tabs */}
        <nav className="flex items-center gap-1 overflow-x-auto -mb-px">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <NavLink
                key={tab.to}
                to={tab.to}
                end={tab.end}
                className={`
                  flex items-center gap-2 px-3.5 py-2.5 text-xs sm:text-sm font-medium border-b-2 whitespace-nowrap transition-colors
                  ${tab.isActive
                    ? 'border-brand-600 text-brand-700 font-semibold'
                    : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }
                `}
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{tab.label}</span>
                {tab.count !== undefined && (
                  <span className={`px-1.5 py-0.2 rounded-full text-xs font-semibold ${
                    tab.alert ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'
                  }`}>
                    {tab.count}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

      </div>
    </div>
  );
};
