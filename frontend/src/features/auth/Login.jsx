import { useState } from 'react';
import { api } from '../../lib/client.js';

export default function Login({ onLogin }) {
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setBusy(true); setError('');
    const form = event.currentTarget;
    try {
      const result = await api('/auth/login', { method: 'POST', body: {
        username: form.elements.username.value, password: form.elements.password.value,
      } });
      form.reset();
      onLogin(result.user);
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return <main className="mx-auto grid max-w-5xl gap-12 px-6 py-20 md:grid-cols-2">
    <section><p className="eyebrow">APPROVALS · OBLIGATIONS · DEADLINES</p>
      <h1 className="mt-5 text-5xl font-semibold leading-tight">Every deadline.<br /><span className="text-teal-700">An accountable next step.</span></h1>
      <p className="mt-6 max-w-md text-lg text-slate-600">A shared workspace for institutions, regional officers and committees to keep approval work moving.</p>
      <div className="mt-10 border-l-2 border-teal-600 pl-5 text-sm text-slate-600">Development demonstration. All records and timelines are fictional. Statutory decisions remain with authorized people.</div>
    </section>
    <form onSubmit={submit} className="panel self-start p-8">
      <h2 className="text-2xl font-semibold">Sign in to ClockWork</h2>
      <p className="mt-2 mb-7 text-sm text-slate-500">Use your assigned development account.</p>
      <label className="label" htmlFor="username">Username</label>
      <input id="username" name="username" autoComplete="username" required maxLength={100} className="input" />
      <label className="label mt-5" htmlFor="password">Password</label>
      <input id="password" name="password" type="password" autoComplete="current-password" required maxLength={256} className="input" />
      {error && <p role="alert" className="mt-4 text-sm text-red-700">{error}</p>}
      <button disabled={busy} className="primary mt-7 w-full">{busy ? 'Signing in…' : 'Sign in'}</button>
    </form>
  </main>;
}
