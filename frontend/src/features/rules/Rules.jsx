import { useEffect, useState } from 'react';
import { api } from '../../lib/client.js';

export default function Rules({ onExpired }) {
  const [rules, setRules] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    api('/rules', { signal: controller.signal }).then(setRules).catch(err => {
      if (err.name === 'AbortError') return;
      if (err.status === 401) onExpired(); else setError(err.message);
    });
    return () => controller.abort();
  }, [onExpired]);
  return <main className="mx-auto max-w-5xl px-6 py-10"><p className="eyebrow">ADMINISTRATION</p><h1 className="mt-2 text-4xl font-semibold">Published rules</h1>
    <p className="my-5 text-slate-600">Read-only published demo configuration. Editing, simulation and publication controls are not yet available.</p>
    {error && <p role="alert">{error}</p>}
    {rules.map(rule => <section key={`${rule.rule_id}:${rule.version}`} className="panel mb-5 p-6"><h2 className="text-xl font-semibold">{rule.rule_id} · v{rule.version}</h2><p className="my-3">{rule.label}</p>
      <dl className="space-y-3">{Object.entries(rule.routes).map(([name, stages]) => <div key={name}><dt className="text-sm text-slate-500">{name}</dt><dd>{stages.join(' → ')}</dd></div>)}</dl></section>)}
  </main>;
}
