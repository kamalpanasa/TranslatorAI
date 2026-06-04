import React, { useState } from 'react';

export default function AuthForms({ token, setToken, userEmail, setUserEmail, apiUrl }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    const endpoint = isLogin ? `${apiUrl}/auth/login` : `${apiUrl}/auth/register`;
    const payload = { email, password };

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication operation failed.');
      }

      if (isLogin) {
        setToken(data.access_token);
        setUserEmail(email);
        setSuccess('Logged in successfully!');
      } else {
        setSuccess('Account created successfully! You can now log in.');
        setIsLogin(true);
        setPassword('');
      }
    } catch (err) {
      setError(err.message || 'Server connection error.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await fetch(`${apiUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (e) {
      console.warn("Logout failed:", e);
    }
    setToken(null);
    setUserEmail(null);
    setEmail('');
    setPassword('');
    setSuccess('Logged out successfully.');
    setLoading(false);
  };

  if (token) {
    return (
      <div className="glass-panel p-6 rounded-xl border border-glassBorder max-w-sm w-full mx-auto">
        <h3 className="font-outfit font-bold text-lg mb-2 bg-gradient-to-r from-skyAccent to-indigoPrimary bg-clip-text text-transparent">
          User Session
        </h3>
        <p className="text-sm text-slate-300 mb-4">
          Logged in as: <span className="font-semibold text-slate-100">{userEmail}</span>
        </p>
        <button
          onClick={handleLogout}
          disabled={loading}
          className="w-full bg-gradient-to-r from-red-500 to-rose-600 text-white font-medium py-2 rounded-lg hover:brightness-110 disabled:opacity-50 transition"
        >
          {loading ? 'Logging out...' : 'Sign Out'}
        </button>
        {success && <p className="text-green-400 text-xs mt-3 text-center">{success}</p>}
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-xl border border-glassBorder max-w-sm w-full mx-auto">
      <h3 className="font-outfit font-bold text-xl mb-4 text-center bg-gradient-to-r from-skyAccent to-indigoPrimary bg-clip-text text-transparent">
        {isLogin ? 'Welcome Back' : 'Create Account'}
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full glass-input rounded-lg px-3 py-2 text-slate-200 outline-none text-sm placeholder:text-slate-600"
            placeholder="user@example.com"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full glass-input rounded-lg px-3 py-2 text-slate-200 outline-none text-sm placeholder:text-slate-600"
            placeholder="••••••••"
          />
        </div>

        {error && <p className="text-red-400 text-xs text-center">{error}</p>}
        {success && <p className="text-green-400 text-xs text-center">{success}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-gradient-to-r from-skyAccent to-indigoPrimary text-white font-semibold py-2.5 rounded-lg hover:brightness-110 disabled:opacity-50 transition text-sm"
        >
          {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Sign Up'}
        </button>
      </form>

      <div className="mt-4 pt-4 border-t border-slate-800 text-center">
        <button
          onClick={() => {
            setIsLogin(!isLogin);
            setError('');
            setSuccess('');
          }}
          className="text-xs text-skyAccent hover:underline focus:outline-none"
        >
          {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
        </button>
      </div>
    </div>
  );
}
