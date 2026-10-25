import Badge from '../components/ui/Badge.jsx';

export default function Layout({ user, onLogout, children }) {
  return <><header className="border-b border-slate-200 bg-white"><div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-6 py-5">
    <div className="flex items-center gap-3"><span className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-800 text-xl text-white" aria-hidden="true">◷</span><span className="text-xl font-bold tracking-tight">ClockWork</span><Badge className="bg-slate-100 text-slate-500">DEMO</Badge></div>
    {user && <div className="flex items-center gap-4"><span className="text-sm text-slate-600">{user.username} · {user.role.replaceAll('_', ' ')}</span><button className="secondary" onClick={onLogout}>Sign out</button></div>}
  </div></header>{children}</>;
}
