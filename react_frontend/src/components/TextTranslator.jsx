import React, { useState } from 'react';
import { Star, RefreshCw } from 'lucide-react';

export default function TextTranslator({ languages, token, apiUrl }) {
  const [text, setText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('fr');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [bookmarked, setBookmarked] = useState(false);

  const handleTranslate = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError('');
    setBookmarked(false);

    try {
      const res = await fetch(`${apiUrl}/translate/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          source_lang: sourceLang,
          target_lang: targetLang
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Failed to translate.');
      }

      setTranslatedText(data.translated_text);
    } catch (err) {
      setError(err.message || 'Translation engine error.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddFavorite = async () => {
    if (!translatedText || bookmarked || !token) return;

    try {
      const res = await fetch(`${apiUrl}/favorites`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          input_text: text,
          translated_text: translatedText,
          source_lang: sourceLang,
          target_lang: targetLang
        }),
      });

      if (res.ok) {
        setBookmarked(true);
      } else {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to bookmark.');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-900/60 p-4 rounded-xl border border-glassBorder">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">From</label>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className="flex-1 sm:flex-initial bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-skyAccent"
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">To</label>
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="flex-1 sm:flex-initial bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-skyAccent"
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source Text Area */}
        <div className="flex flex-col">
          <div className="flex justify-between items-center mb-2 px-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Source Content</span>
            <span className="text-xs text-slate-600">{text.length} chars</span>
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter source sentences to translate..."
            rows={8}
            className="w-full glass-input rounded-xl p-4 text-slate-200 outline-none text-sm placeholder:text-slate-600 resize-none"
          />
        </div>

        {/* Target Translation Area */}
        <div className="flex flex-col">
          <div className="flex justify-between items-center mb-2 px-1">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Translation</span>
            {token && translatedText && (
              <button
                onClick={handleAddFavorite}
                className={`flex items-center gap-1.5 text-xs ${
                  bookmarked ? 'text-amber-400' : 'text-slate-500 hover:text-amber-400'
                } transition`}
              >
                <Star className={`w-3.5 h-3.5 ${bookmarked ? 'fill-amber-400' : ''}`} />
                {bookmarked ? 'Bookmarked' : 'Add to Favorites'}
              </button>
            )}
          </div>
          <div className="w-full bg-slate-950/80 border border-slate-900 rounded-xl p-4 text-slate-100 text-sm min-h-[170px] flex flex-col justify-between">
            {loading ? (
              <div className="flex justify-center items-center h-28 text-slate-500">
                <RefreshCw className="w-6 h-6 animate-spin mr-2" />
                <span>Translating chunks via NLLB AI...</span>
              </div>
            ) : (
              <p className="whitespace-pre-wrap leading-relaxed">
                {translatedText || <span className="text-slate-600 italic">Translated result will appear here...</span>}
              </p>
            )}
            
            {error && <p className="text-red-400 text-xs mt-4">{error}</p>}
          </div>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleTranslate}
          disabled={loading || !text.trim()}
          className="bg-gradient-to-r from-skyAccent to-indigoPrimary text-white font-semibold px-8 py-3 rounded-xl hover:brightness-110 disabled:opacity-40 transition shadow-lg shadow-sky-500/10 text-sm"
        >
          {loading ? 'Translating...' : 'Translate Content'}
        </button>
      </div>
    </div>
  );
}
