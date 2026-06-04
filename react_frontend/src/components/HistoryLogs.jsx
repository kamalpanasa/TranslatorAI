import React, { useState, useEffect } from 'react';
import { Trash2, Bookmark, Clock, AlertTriangle } from 'lucide-react';

export default function HistoryLogs({ token, apiUrl }) {
  const [activeSubTab, setActiveSubTab] = useState('history'); // history vs favorites
  const [historyItems, setHistoryItems] = useState([]);
  const [favoriteItems, setFavoriteItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchHistory = async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to fetch history logs.');
      setHistoryItems(data);
    } catch (err) {
      setError(err.message || 'Error fetching history.');
    } finally {
      setLoading(false);
    }
  };

  const fetchFavorites = async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${apiUrl}/favorites`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to fetch bookmarks.');
      setFavoriteItems(data);
    } catch (err) {
      setError(err.message || 'Error fetching favorites.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      if (activeSubTab === 'history') {
        fetchHistory();
      } else {
        fetchFavorites();
      }
    }
  }, [token, activeSubTab]);

  const handleDeleteHistory = async (id) => {
    try {
      const res = await fetch(`${apiUrl}/history/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setHistoryItems((prev) => prev.filter((item) => item.id !== id));
      } else {
        const data = await res.json();
        throw new Error(data.detail || 'Deletion failed.');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteFavorite = async (id) => {
    try {
      const res = await fetch(`${apiUrl}/favorites/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setFavoriteItems((prev) => prev.filter((item) => item.id !== id));
      } else {
        const data = await res.json();
        throw new Error(data.detail || 'Remove favorite failed.');
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const formatDate = (isoString) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return isoString;
    }
  };

  if (!token) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-500 bg-slate-950/20 border border-slate-900 rounded-xl">
        <AlertTriangle className="w-10 h-10 text-amber-500 mb-3" />
        <p className="text-sm font-medium text-slate-300">Authentication Required</p>
        <p className="text-xs mt-1">Please sign in on the left sidebar to view translation records.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sub tabs */}
      <div className="flex gap-4 border-b border-slate-800 pb-px">
        <button
          onClick={() => setActiveSubTab('history')}
          className={`flex items-center gap-2 pb-3 font-semibold text-xs uppercase tracking-wider outline-none transition border-b-2 ${
            activeSubTab === 'history'
              ? 'border-skyAccent text-skyAccent'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-3.5 h-3.5" />
          Translation History ({historyItems.length})
        </button>

        <button
          onClick={() => setActiveSubTab('favorites')}
          className={`flex items-center gap-2 pb-3 font-semibold text-xs uppercase tracking-wider outline-none transition border-b-2 ${
            activeSubTab === 'favorites'
              ? 'border-skyAccent text-skyAccent'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Bookmark className="w-3.5 h-3.5" />
          Bookmarked Favorites ({favoriteItems.length})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-10 text-slate-500 text-sm">
          <span>Loading database logs...</span>
        </div>
      ) : activeSubTab === 'history' ? (
        // History List
        <div className="space-y-4">
          {historyItems.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No past translation logs found.</p>
          ) : (
            historyItems.map((item) => (
              <div
                key={item.id}
                className="glass-panel p-4 rounded-xl border border-glassBorder flex justify-between items-start gap-4 text-sm"
              >
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-skyAccent bg-skyAccent/10 px-2 py-0.5 rounded">
                      {item.file_type}
                    </span>
                    <span className="text-[10px] text-slate-500 font-medium">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                  {item.file_name && (
                    <p className="text-xs text-slate-400 font-medium">File: {item.file_name}</p>
                  )}
                  <p className="text-slate-300">
                    <strong className="text-[10px] uppercase text-slate-500 mr-1.5">{item.source_lang}</strong>
                    {item.input_text}
                  </p>
                  <p className="text-slate-100">
                    <strong className="text-[10px] uppercase text-indigo-400 mr-1.5">{item.target_lang}</strong>
                    {item.translated_text}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteHistory(item.id)}
                  className="text-slate-600 hover:text-red-400 transition p-1"
                  title="Remove log entry"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      ) : (
        // Favorites Bookmarks List
        <div className="space-y-4">
          {favoriteItems.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No bookmarked translations found.</p>
          ) : (
            favoriteItems.map((item) => (
              <div
                key={item.id}
                className="glass-panel p-4 rounded-xl border border-glassBorder flex justify-between items-start gap-4 text-sm"
              >
                <div className="space-y-2 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded">
                      bookmarked
                    </span>
                    <span className="text-[10px] text-slate-500 font-medium">
                      {formatDate(item.created_at)}
                    </span>
                  </div>
                  <p className="text-slate-300">
                    <strong className="text-[10px] uppercase text-slate-500 mr-1.5">{item.source_lang}</strong>
                    {item.input_text}
                  </p>
                  <p className="text-slate-100">
                    <strong className="text-[10px] uppercase text-indigo-400 mr-1.5">{item.target_lang}</strong>
                    {item.translated_text}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteFavorite(item.id)}
                  className="text-slate-600 hover:text-red-400 transition p-1"
                  title="Remove bookmark"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
