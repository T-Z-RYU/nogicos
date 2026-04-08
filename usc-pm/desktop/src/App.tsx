import { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { getBackend, getToken, setBackend, setToken } from "./lib/auth";
import Onboarding from "./pages/Onboarding";
import Channels from "./pages/Channels";
import Rules from "./pages/Rules";
import Dashboard from "./pages/Dashboard";
import Unity from "./pages/Unity";
import Settings from "./pages/Settings";

export default function App() {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const backend = await getBackend();
      const token = await getToken();
      setAuthed(!!backend && !!token);
      setReady(true);
    })();

    // Accept ?token=... in URL after OAuth redirect (browser fallback)
    const params = new URLSearchParams(window.location.search);
    const t = params.get("token");
    if (t) {
      setToken(t).then(() => { setAuthed(true); navigate("/channels"); });
    }

    // Electron deep-link: usc-pm://auth?token=...
    const w = window as any;
    if (w.electronAPI?.onDeepLink) {
      w.electronAPI.onDeepLink(async (url: string) => {
        try {
          const u = new URL(url);
          const tok = u.searchParams.get("token");
          if (tok) {
            await setToken(tok);
            setAuthed(true);
            navigate("/channels");
          }
        } catch {}
      });
    }
  }, []);

  if (!ready) return <div className="p-8">Loading…</div>;

  return (
    <div className="flex h-full">
      <nav className="w-48 border-r border-neutral-800 p-4 space-y-2">
        <h1 className="text-lg font-semibold mb-4">USC PM</h1>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/channels">Channels</NavLink>
        <NavLink to="/rules">Reply Rules</NavLink>
        <NavLink to="/unity">Unity Progress</NavLink>
        <NavLink to="/onboarding">Connect Accounts</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </nav>
      <main className="flex-1 overflow-auto p-6">
        <Routes>
          <Route path="/" element={authed ? <Dashboard /> : <Onboarding />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/channels" element={<Channels />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/unity" element={<Unity />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  return (
    <Link to={to} className="block px-3 py-2 rounded hover:bg-neutral-800 text-sm">
      {children}
    </Link>
  );
}
