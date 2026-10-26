import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Building2, MapPin, ArrowLeft, Loader2, AlertCircle } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { api } from '../services/api';
import { Jurisdiction } from '../types';

export const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [jurisdictions, setJurisdictions] = useState<Jurisdiction[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    country: 'United States',
    state_region: 'California',
    city: '',
    address: '',
    project_type: 'Residential Addition',
    building_type: 'Single Family Residence',
    num_floors: 1,
    area: 450,
    area_unit: 'sq_ft',
    stage: 'Pre-Submission Preparation',
    jurisdiction_id: 'US-CA-GENERIC'
  });

  useEffect(() => {
    api.getJurisdictions()
      .then(setJurisdictions)
      .catch(console.error);
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'num_floors' || name === 'area' ? Number(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim()) {
      setError('Please provide a project name.');
      return;
    }
    if (!formData.address.trim()) {
      setError('Please enter the street address.');
      return;
    }
    if (!formData.city.trim()) {
      setError('Please enter the city.');
      return;
    }

    setIsSubmitting(true);
    try {
      const created = await api.createProject(formData);
      navigate(`/projects/${created.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create project. Please verify inputs.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <main className="flex-1 max-w-3xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Back Link & Header */}
        <div className="mb-6">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Projects</span>
          </Link>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Create Residential Project</h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
            Set up your property location and submittal scope for automated pre-checks.
          </p>
        </div>

        {/* Form Card */}
        <div className="saas-card p-6 sm:p-8">
          
          {error && (
            <div className="mb-6 p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2 text-xs text-rose-800">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Section 1: Project & Property Details */}
            <div className="space-y-4">
              <div className="border-b border-slate-100 pb-2">
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  <span>Property & Location Details</span>
                </h2>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Project Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  required
                  placeholder="e.g., Oakwood Residence Addition"
                  value={formData.name}
                  onChange={handleChange}
                  className="saas-input"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Street Address <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  name="address"
                  required
                  placeholder="e.g., 124 Example Lane"
                  value={formData.address}
                  onChange={handleChange}
                  className="saas-input"
                />
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Must match the property address shown on your title blocks and permit application.
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    City <span className="text-rose-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="city"
                    required
                    placeholder="e.g., Sampletown"
                    value={formData.city}
                    onChange={handleChange}
                    className="saas-input"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    State / Region
                  </label>
                  <input
                    type="text"
                    name="state_region"
                    value={formData.state_region}
                    onChange={handleChange}
                    className="saas-input"
                  />
                </div>
              </div>
            </div>

            {/* Section 2: Building Specs & Jurisdiction */}
            <div className="space-y-4 pt-2">
              <div className="border-b border-slate-100 pb-2">
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-slate-400" />
                  <span>Scope & Permitting Authority</span>
                </h2>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Project Type
                  </label>
                  <select
                    name="project_type"
                    value={formData.project_type}
                    onChange={handleChange}
                    className="saas-select"
                  >
                    <option value="Residential Addition">Residential Addition</option>
                    <option value="New Single Family Residence">New Single Family Residence</option>
                    <option value="Renovation / Remodel">Renovation / Remodel</option>
                    <option value="Accessory Dwelling Unit (ADU)">Accessory Dwelling Unit (ADU)</option>
                    <option value="Deck / Patio Addition">Deck / Patio Addition</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Permitting Jurisdiction
                  </label>
                  <select
                    name="jurisdiction_id"
                    value={formData.jurisdiction_id}
                    onChange={handleChange}
                    className="saas-select font-mono text-xs"
                  >
                    {jurisdictions.map(j => (
                      <option key={j.id} value={j.id}>
                        {j.name} ({j.id})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Number of Stories
                  </label>
                  <input
                    type="number"
                    name="num_floors"
                    min="1"
                    max="5"
                    value={formData.num_floors}
                    onChange={handleChange}
                    className="saas-input"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Proposed Scope Area (sq ft)
                  </label>
                  <input
                    type="number"
                    name="area"
                    min="1"
                    value={formData.area}
                    onChange={handleChange}
                    className="saas-input"
                  />
                </div>
              </div>
            </div>

            {/* Form Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <Link
                to="/dashboard"
                className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center justify-center gap-1.5 px-5 py-2.5 text-xs sm:text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 active:bg-brand-800 rounded-lg shadow-xs transition-colors disabled:opacity-50 cursor-pointer"
              >
                {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                <span>{isSubmitting ? 'Creating Project...' : 'Create Project'}</span>
              </button>
            </div>

          </form>
        </div>

      </main>

      <Footer />
    </div>
  );
};
