import { useEffect, useState } from 'react';
import { api } from '../../lib/client.js';
import Badge from '../../components/ui/Badge.jsx';

const readable = value => value.replaceAll('_', ' ');

export default function Today({ onExpired }) {
  const [page, setPage] = useState(null);
  const [error, setError] = useState('');
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState(null);
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setPage(null); setError(''); setSelected(null);
    api(`/obligations?limit=10&offset=${offset}`, { signal: controller.signal })
      .then(setPage).catch(err => {
        if (err.name === 'AbortError') return;
        if (err.status === 401) onExpired();
        else setError(err.message);
      });
    return () => controller.abort();
  }, [offset, refresh, onExpired]);
  return <main className="mx-auto max-w-6xl px-6 py-10">
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div><p className="eyebrow">YOUR WORKSPACE</p><h1 className="mt-2 text-4xl font-semibold">Today</h1>
        <p className="mt-3 text-slate-600">Your authorized obligations, ordered by saved deadline.</p></div>
      <button className="secondary" onClick={() => setRefresh(n => n + 1)}>Refresh</button>
    </div>
    <div className="my-7 flex flex-wrap justify-between gap-3 rounded-xl bg-teal-950 px-6 py-5 text-white">
      <span>Shared obligation register <span className="ml-2 text-teal-200">/ Foundation preview</span></span>
      <span className="text-sm text-teal-100">{page ? `Demo business date: ${new Intl.DateTimeFormat('en-IN', { timeZone: 'Asia/Kolkata' }).format(new Date(page.business_at))}` : 'Loading business time…'}</span>
    </div>
    {error && <p role="alert" className="panel p-5 text-red-700">{error}</p>}
    {!page && !error && <p role="status">Loading obligations…</p>}
    {page && <section className="panel overflow-hidden" aria-label="Obligations">
      <div className="border-b border-slate-100 px-6 py-4 text-sm text-slate-500">{page.total} visible obligations · permissions applied by the server</div>
      {page.items.length === 0 && <p className="p-8">No obligations in your assigned scope.</p>}
      {page.items.map(item => <button key={item.id} onClick={() => setSelected(item)} className="flex w-full flex-wrap items-center justify-between gap-4 border-b border-slate-100 px-6 py-5 text-left hover:bg-slate-50">
        <div><span className="font-semibold capitalize">{readable(item.kind)}</span><p className="mt-1 text-sm text-slate-500">{item.region} · Case {item.application_id.slice(-4)}</p></div>
        <div className="flex items-center gap-5"><span className="text-sm capitalize text-slate-500">{readable(item.state)}</span>
          <Badge className={item.deadline_severity === 'overdue' ? 'bg-red-50 text-red-800' : 'bg-amber-50 text-amber-900'}>{item.days_remaining < 0 ? `${-item.days_remaining} days overdue` : item.days_remaining === 0 ? 'Due today' : `${item.days_remaining} days remaining`}</Badge><span aria-hidden="true">↗</span></div>
      </button>)}
      <div className="flex items-center justify-between px-6 py-4"><button className="secondary" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - 10))}>Previous</button>
        <span className="text-sm text-slate-500">Page {Math.floor(offset / 10) + 1}</span><button className="secondary" disabled={offset + 10 >= page.total} onClick={() => setOffset(offset + 10)}>Next</button></div>
    </section>}
    {selected && <section className="panel mt-6 p-6" aria-label="Obligation details">
      <div className="flex justify-between"><h2 className="text-xl font-semibold capitalize">{readable(selected.kind)}</h2><button className="secondary" onClick={() => setSelected(null)}>Close</button></div>
      <dl className="mt-5 grid gap-4 text-sm sm:grid-cols-2">
        <div><dt className="text-slate-500">Pinned rule</dt><dd>{selected.rule_id} · version {selected.rule_version}</dd></div>
        <div><dt className="text-slate-500">Evidence status</dt><dd>{readable(selected.evidence_state)}</dd></div>
        <div><dt className="text-slate-500">Due date (India)</dt><dd>{new Intl.DateTimeFormat('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'long' }).format(new Date(selected.active_due_at))}</dd></div>
        <div><dt className="text-slate-500">Record version</dt><dd>{selected.version}</dd></div>
      </dl><p className="mt-5 text-sm text-slate-500">This preview is read-only. Processing actions and the full case timeline are the next milestone.</p>
    </section>}
    <p className="mt-7 text-sm text-slate-500">Demo calendar-day rules, not official policy. Notifications and the 30-day strip arrive with the deadline engine.</p>
  </main>;
}
