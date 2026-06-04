import React, { useState, useEffect } from 'react';
import { Languages, FileText, Mic, History, User } from 'lucide-react';
import AuthForms from './components/AuthForms';
import TextTranslator from './components/TextTranslator';
import AudioTranslator from './components/AudioTranslator';
import DocumentTranslator from './components/DocumentTranslator';
import HistoryLogs from './components/HistoryLogs';

const API_URL = "http://127.0.0.1:8000/api/v1";

export default function App() {
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState(null);
  const [languages, setLanguages] = useState([]);
  const [activeTab, setActiveTab] = useState('text'); // text, document, audio, history

  // Fetch languages list on mount
  useEffect(() => {
    const loadLanguages = async () => {
      try {
        const res = await fetch(`${API_URL}/languages`);
        if (res.ok) {
          const data = await res.json();
          setLanguages(data);
        } else {
          throw new Error();
        }
      } catch (e) {
        // Fallback default list if API is offline during mount
        setLanguages([
          { code: 'en', name: 'English', nllb_code: 'eng_Latn' },
          { code: 'hi', name: 'Hindi', nllb_code: 'hin_Deva' },
          { code: 'fr', name: 'French', nllb_code: 'fra_Latn' },
          { code: 'es', name: 'Spanish', nllb_code: 'spa_Latn' },
          { code: 'zh', name: 'Chinese', nllb_code: 'zho_Hans' },
          { code: 'ar', name: 'Arabic', nllb_code: 'ara_Arab' },
          { code: 'de', name: 'German', nllb_code: 'deu_Latn' },
          { code: 'ja', name: 'Japanese', nllb_code: 'jpn_Jpan' }
        ]);
      }
    };
    loadLanguages();
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      
      {/* Header Navbar */}
      <header className="border-b border-glassBorder bg-slate-950/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-skyAccent to-indigoPrimary flex items-center justify-center text-white text-base shadow-lg shadow-sky-500/10">
              ✈️
            </div>
            <div>
              <h1 className="font-outfit font-bold text-base leading-tight tracking-wide bg-gradient-to-r from-skyAccent to-indigoPrimary bg-clip-text text-transparent">
                AeroTranslate AI
              </h1>
              <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
                Production-grade Engine
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              Live Connected
            </span>
          </div>
        </div>
      </header>

      {/* Main Layout Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
          
          {/* Left Sidebar: Session / Auth info */}
          <div className="lg:col-span-1 space-y-6">
            <AuthForms
              token={token}
              setToken={setToken}
              userEmail={userEmail}
              setUserEmail={setUserEmail}
              apiUrl={API_URL}
            />
            
            <div className="glass-panel p-4 rounded-xl border border-glassBorder text-xs text-slate-500 leading-relaxed hidden lg:block">
              <h4 className="font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">Backend Config</h4>
              <p>Target URL: <code className="text-skyAccent">{API_URL}</code></p>
              <p className="mt-1">Supported Vocab: {languages.length} dialects active</p>
            </div>
          </div>

          {/* Right Main Panel: Dashboard Content */}
          <div className="lg:col-span-3 space-y-6">
            
            {/* Nav tabs */}
            <div className="glass-panel p-1.5 rounded-xl border border-glassBorder flex flex-wrap gap-1">
              <button
                onClick={() => setActiveTab('text')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider outline-none transition ${
                  activeTab === 'text'
                    ? 'bg-gradient-to-r from-skyAccent to-indigoPrimary text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Languages className="w-3.5 h-3.5" />
                Text Translate
              </button>

              <button
                onClick={() => setActiveTab('document')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider outline-none transition ${
                  activeTab === 'document'
                    ? 'bg-gradient-to-r from-skyAccent to-indigoPrimary text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                Documents
              </button>

              <button
                onClick={() => setActiveTab('audio')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider outline-none transition ${
                  activeTab === 'audio'
                    ? 'bg-gradient-to-r from-skyAccent to-indigoPrimary text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Mic className="w-3.5 h-3.5" />
                Voice & Audio
              </button>

              <button
                onClick={() => setActiveTab('history')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider outline-none transition ${
                  activeTab === 'history'
                    ? 'bg-gradient-to-r from-skyAccent to-indigoPrimary text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <History className="w-3.5 h-3.5" />
                Database History
              </button>
            </div>

            {/* Active view rendering */}
            <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-glassBorder min-h-[350px]">
              {activeTab === 'text' && (
                <TextTranslator languages={languages} token={token} apiUrl={API_URL} />
              )}
              {activeTab === 'document' && (
                <DocumentTranslator languages={languages} token={token} apiUrl={API_URL} />
              )}
              {activeTab === 'audio' && (
                <AudioTranslator languages={languages} token={token} apiUrl={API_URL} />
              )}
              {activeTab === 'history' && (
                <HistoryLogs token={token} apiUrl={API_URL} />
              )}
            </div>

          </div>
        </div>
      </main>

      {/* Footer footer */}
      <footer className="border-t border-slate-900 mt-auto bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-xs text-slate-600">
          AeroTranslate © 2026. Made with FastAPI, React, and Tailwind CSS.
        </div>
      </footer>

    </div>
  );
}
