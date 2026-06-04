import React, { useState } from 'react';
import { Upload, FileText, ArrowRight, Download, RefreshCw, AlertCircle } from 'lucide-react';

export default function DocumentTranslator({ languages, token, apiUrl }) {
  const [file, setFile] = useState(null);
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('fr');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloadUrl, setDownloadUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const uploadedFile = e.dataTransfer.files[0];
    validateAndSetFile(uploadedFile);
  };

  const handleChange = (e) => {
    const uploadedFile = e.target.files[0];
    validateAndSetFile(uploadedFile);
  };

  const validateAndSetFile = (uploadedFile) => {
    setError('');
    setDownloadUrl('');
    if (!uploadedFile) return;

    const allowedExtensions = ['pdf', 'docx', 'xlsx', 'csv'];
    const extension = uploadedFile.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(extension)) {
      setError(`Unsupported file format. Supported formats: ${allowedExtensions.join(', ')}`);
      setFile(null);
      return;
    }

    // Limit file size to 50MB (matching settings)
    if (uploadedFile.size > 50 * 1024 * 1024) {
      setError('File exceeds maximum size limit of 50MB.');
      setFile(null);
      return;
    }

    setFile(uploadedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError('');
    setDownloadUrl('');

    const extension = file.name.split('.').pop().toLowerCase();
    // Map Excel extension to API route name
    const formatName = extension === 'xlsx' ? 'excel' : extension;
    const endpoint = `${apiUrl}/translate/${formatName}`;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Document translation execution failed.');
      }

      let resultUrl = data.translated_file_url;
      // If URL is local, append base domain
      if (resultUrl.startsWith('/exports')) {
        const domain = apiUrl.replace('/api/v1', '');
        resultUrl = `${domain}${resultUrl}`;
      }

      setDownloadUrl(resultUrl);
    } catch (err) {
      setError(err.message || 'File processing error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Upload Column */}
        <div className="md:col-span-2 space-y-4">
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-8 transition min-h-[250px] bg-slate-950/20 ${
              dragActive ? 'border-skyAccent bg-skyAccent/5' : 'border-slate-800 hover:border-slate-700'
            }`}
          >
            <Upload className="w-10 h-10 text-skyAccent mb-4 animate-bounce" />
            <p className="text-sm text-slate-300 font-medium mb-1">
              Drag & Drop your document here
            </p>
            <p className="text-xs text-slate-500 mb-4">
              Supports PDF, DOCX, XLSX, and CSV (Max 50MB)
            </p>

            <label className="bg-slate-900 border border-slate-700 hover:bg-slate-800 text-slate-200 font-medium text-xs px-4 py-2 rounded-lg cursor-pointer transition">
              Select Document
              <input
                type="file"
                accept=".pdf,.docx,.xlsx,.csv"
                onChange={handleChange}
                className="hidden"
              />
            </label>
          </div>

          {file && (
            <div className="flex items-center gap-3 p-3 bg-slate-900/40 rounded-lg border border-glassBorder text-sm">
              <FileText className="w-5 h-5 text-skyAccent shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-slate-200 font-medium truncate">{file.name}</p>
                <p className="text-slate-500 text-xs">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              </div>
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-950/20 text-red-400 rounded-lg border border-red-900/30 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Translation parameters & outputs */}
        <div className="glass-panel p-6 rounded-xl border border-glassBorder flex flex-col justify-between space-y-6">
          <div>
            <h3 className="font-outfit font-bold text-base mb-4 text-slate-300">File Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">From</label>
                <select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-skyAccent"
                >
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">To</label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-skyAccent"
                >
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {downloadUrl && (
              <a
                href={downloadUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-2 w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 rounded-lg text-sm shadow-lg shadow-emerald-500/10 transition"
              >
                <Download className="w-4 h-4" />
                Download Result
              </a>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              className="flex items-center justify-center gap-2 w-full bg-gradient-to-r from-skyAccent to-indigoPrimary text-white font-semibold py-2.5 rounded-lg hover:brightness-110 disabled:opacity-40 transition text-sm"
            >
              {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
              {loading ? 'Translating File...' : 'Translate File'}
            </button>
          </div>
        </div>

      </form>
    </div>
  );
}
