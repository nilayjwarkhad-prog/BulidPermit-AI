import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, CheckCircle2, FileSearch, Scale, FileText, ArrowRight, AlertTriangle, Layers, Cpu, Compass } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 md:pt-24 md:pb-28 border-b border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-200 text-xs font-semibold text-brand-700 mb-6">
            <span className="flex h-2 w-2 rounded-full bg-brand-600"></span>
            AI-Powered Permit Pre-Submission Assistant
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-tight md:leading-[1.15]">
            Detect permit discrepancies <br className="hidden sm:inline" />
            <span className="text-brand-600">before</span> you file with the city.
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Upload architectural plans, site surveys, and application forms. Our deterministic rules engine and local AI inspect missing documents, contradictory measurements, and zoning setbacks before submission.
          </p>

          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-base font-semibold text-white bg-brand-600 rounded-xl hover:bg-brand-700 shadow-sm transition-all"
            >
              <span>Start Free Pre-Check</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-base font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all"
            >
              <span>Explore Demo Account</span>
            </Link>
          </div>

          {/* Quick Pillars */}
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <FileSearch className="w-5 h-5 text-brand-600 mb-2" />
              <h4 className="font-semibold text-xs text-slate-900">Cross-Doc Verification</h4>
              <p className="text-[11px] text-slate-500 mt-1">Flags mismatched addresses and conflicting square footages.</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <Scale className="w-5 h-5 text-brand-600 mb-2" />
              <h4 className="font-semibold text-xs text-slate-900">Setback & Zoning Checks</h4>
              <p className="text-[11px] text-slate-500 mt-1">Evaluates front, rear, and side yard dimensional thresholds.</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <Cpu className="w-5 h-5 text-brand-600 mb-2" />
              <h4 className="font-semibold text-xs text-slate-900">Local Gemma 4 AI Engine</h4>
              <p className="text-[11px] text-slate-500 mt-1">Runs open-weight model locally without sending plans to paid clouds.</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <FileText className="w-5 h-5 text-brand-600 mb-2" />
              <h4 className="font-semibold text-xs text-slate-900">Formal PDF Reports</h4>
              <p className="text-[11px] text-slate-500 mt-1">Downloadable pre-submission audit report for your design team.</p>
            </div>
          </div>

        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-slate-50 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-brand-600 mb-2">Step-by-Step Workflow</h2>
            <h3 className="text-3xl font-bold text-slate-900 tracking-tight">How the Pre-Check Assistant Works</h3>
            <p className="mt-3 text-sm text-slate-600">A structured preparation pipeline designed for residential permits.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative">
              <span className="text-3xl font-extrabold text-brand-100 font-mono absolute top-4 right-5">01</span>
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mb-4">
                <Compass className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Define Project & Jurisdiction</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Specify your property location, building scope (addition, remodel, ADU), and permitting municipality.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative">
              <span className="text-3xl font-extrabold text-brand-100 font-mono absolute top-4 right-5">02</span>
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mb-4">
                <Layers className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Upload Submittal Set</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Upload your permit application, architectural drawings, site plan, and structural notes in PDF or high-res format.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative">
              <span className="text-3xl font-extrabold text-brand-100 font-mono absolute top-4 right-5">03</span>
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mb-4">
                <FileSearch className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Automated 9-Step Review</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Extracts text, identifies categories, tests address consistency, cross-references areas, and verifies required sheets.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm relative">
              <span className="text-3xl font-extrabold text-brand-100 font-mono absolute top-4 right-5">04</span>
              <div className="w-10 h-10 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mb-4">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h4 className="text-base font-bold text-slate-900 mb-2">Audit Report & Checklist</h4>
              <p className="text-xs text-slate-600 leading-relaxed">
                Inspect findings with sheet page references, resolve issues, and download a comprehensive pre-submission report.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* Limitations & Ethics Banner */}
      <section className="py-14 bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
            <div className="flex items-center gap-2 text-slate-900 font-bold text-sm">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Safety, Privacy, and Regulatory Boundaries</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              BuildPermit AI is an organizational and document-checking aid. It never guarantees permit issuance and does not substitute for licensed architectural, structural, or legal review. Uploaded files remain strictly isolated to your project environment and are never utilized for training public AI models.
            </p>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
