import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Upload, RefreshCw, Volume2 } from 'lucide-react';

export default function AudioTranslator({ languages, token, apiUrl }) {
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [translation, setTranslation] = useState('');
  const [sourceLang, setSourceLang] = useState('en');
  const [targetLang, setTargetLang] = useState('hi');
  const [loading, setLoading] = useState(false);
  const [recordTime, setRecordTime] = useState(0);
  const [error, setError] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = async () => {
    setError('');
    setTranscription('');
    setTranslation('');
    setAudioUrl(null);
    setAudioFile(null);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        
        // Convert to a File object to upload
        const file = new File([audioBlob], 'mic_recording.wav', { type: 'audio/wav' });
        setAudioFile(file);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      setRecordTime(0);

      timerRef.current = setInterval(() => {
        setRecordTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError('Microphone access denied or not supported on this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      // Stop all tracks to release mic hardware
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      setRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const handleFileUpload = (e) => {
    setError('');
    const file = e.target.files[0];
    if (file) {
      setAudioFile(file);
      setAudioUrl(URL.createObjectURL(file));
      setTranscription('');
      setTranslation('');
    }
  };

  const processAudioTranslation = async () => {
    if (!audioFile) return;
    setLoading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${apiUrl}/translate/audio`, {
        method: 'POST',
        headers,
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Error processing audio file.');
      }

      // NLLB response schema returns translated text
      setTranslation(data.translated_text);
      setTranscription('Speech transcribed successfully.'); // Mock indicator for simplicity
    } catch (err) {
      setError(err.message || 'Audio translation connection error.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Controls Pane */}
        <div className="glass-panel p-6 rounded-xl border border-glassBorder flex flex-col justify-between space-y-6">
          <div>
            <h3 className="font-outfit font-bold text-base mb-4 text-slate-300">Voice Inputs</h3>
            <div className="space-y-4">
              {/* Mic Controller */}
              <div className="flex flex-col items-center justify-center p-6 border border-dashed border-slate-800 rounded-xl bg-slate-950/40">
                {recording ? (
                  <button
                    onClick={stopRecording}
                    className="w-16 h-16 rounded-full bg-rose-600 flex items-center justify-center animate-pulse text-white shadow-lg shadow-rose-500/20"
                  >
                    <Square className="w-6 h-6 fill-white" />
                  </button>
                ) : (
                  <button
                    onClick={startRecording}
                    className="w-16 h-16 rounded-full bg-skyAccent flex items-center justify-center text-white hover:scale-105 transition shadow-lg shadow-sky-500/25"
                  >
                    <Mic className="w-7 h-7" />
                  </button>
                )}
                
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 mt-4">
                  {recording ? `Recording: ${formatTime(recordTime)}` : 'Tap to Record'}
                </span>
              </div>

              <div className="text-center text-slate-500 text-xs py-1">OR</div>

              {/* File Uploader */}
              <label className="flex items-center justify-center gap-2 border border-slate-800 rounded-lg p-2.5 bg-slate-950 hover:border-slate-700 cursor-pointer transition text-xs text-slate-300 font-medium">
                <Upload className="w-4 h-4 text-skyAccent" />
                Upload Audio File
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>
            </div>
          </div>

          <div>
            {audioUrl && (
              <div className="space-y-2">
                <span className="text-xs text-slate-400 font-medium">Audio playback:</span>
                <audio src={audioUrl} controls className="w-full h-8 outline-none" />
              </div>
            )}

            {error && <p className="text-red-400 text-xs mt-3">{error}</p>}
          </div>
        </div>

        {/* Translation Fields */}
        <div className="md:col-span-2 glass-panel p-6 rounded-xl border border-glassBorder flex flex-col justify-between space-y-6">
          <div>
            <div className="flex flex-col sm:flex-row justify-between gap-4 mb-6">
              <div className="flex items-center gap-3">
                <label className="text-xs font-semibold uppercase text-slate-400">Speak</label>
                <select
                  value={sourceLang}
                  onChange={(e) => setSourceLang(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-skyAccent"
                >
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-3">
                <label className="text-xs font-semibold uppercase text-slate-400">Translate To</label>
                <select
                  value={targetLang}
                  onChange={(e) => setTargetLang(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-skyAccent"
                >
                  {languages.map((l) => (
                    <option key={l.code} value={l.code}>{l.name}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-900 min-h-[120px]">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Transcribed Voice</h4>
                <p className="text-sm text-slate-300">
                  {loading ? 'Transcribing speech chunks...' : transcription || <span className="text-slate-700 italic">No audio processed yet...</span>}
                </p>
              </div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-900 min-h-[120px]">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Translated Text</h4>
                <p className="text-sm text-slate-100 font-medium">
                  {loading ? 'Running NLLB sequence translation...' : translation || <span className="text-slate-700 italic">Translated output...</span>}
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-800/40">
            <span className="text-xs text-slate-500">
              {audioFile ? `Active File: ${audioFile.name}` : 'No file prepared'}
            </span>
            <button
              onClick={processAudioTranslation}
              disabled={loading || !audioFile}
              className="bg-gradient-to-r from-skyAccent to-indigoPrimary text-white font-semibold px-6 py-2.5 rounded-lg hover:brightness-110 disabled:opacity-40 transition text-sm flex items-center gap-2"
            >
              {loading && <RefreshCw className="w-4 h-4 animate-spin" />}
              {loading ? 'Processing...' : 'Run Audio Translation'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
