import Layout from './Layout.jsx';
import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/client.js';
import Login from '../features/auth/Login.jsx';
import Today from '../features/today/Today.jsx';
import Rules from '../features/rules/Rules.jsx';

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const expired = useCallback(() => setUser(null), []);
  useEffect(() => {
    const controller = new AbortController();
    api('/auth/me', { signal: controller.signal }).then(setUser).catch(err => {
      if (err.status !== 401 && err.name !== 'AbortError') setError(err.message);
    }).finally(() => setLoading(false));
    return () => controller.abort();
  }, []);
  async function logout() {
    try { await api('/auth/logout', { method: 'POST', body: {} }); setUser(null); setError(''); }
    catch (err) { if (err.status === 401) setUser(null); else setError(err.message); }
  }
  return <Layout user={user} onLogout={logout}>
  {error && <p role="alert" className="mx-auto mt-4 max-w-5xl rounded-lg bg-red-50 p-4 text-red-800">{error}</p>}
  {loading ? <p role="status" className="p-10">Opening workspace…</p> : !user ? <Login onLogin={value => { setUser(value); setError(''); }} /> : user.role === 'admin' ? <Rules onExpired={expired} /> : <Today onExpired={expired} />}
  </Layout>;
}
