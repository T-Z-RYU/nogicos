import { getBackend, getToken } from "../lib/auth";

export default function Onboarding() {
  async function connectDiscord() {
    const base = await getBackend();
    if (!base) return alert("Set Backend URL in Settings first.");
    const url = `${base}/auth/discord/start`;
    const w = window as any;
    if (w.electronAPI?.openExternal) w.electronAPI.openExternal(url);
    else window.open(url, "_blank");
  }
  async function connectGmail() {
    const base = await getBackend();
    const token = await getToken();
    if (!base || !token) return alert("Connect Discord first.");
    const url = `${base}/auth/gmail/start?state=${encodeURIComponent(token)}`;
    const w = window as any;
    if (w.electronAPI?.openExternal) w.electronAPI.openExternal(url);
    else window.open(url, "_blank");
  }
  return (
    <div className="max-w-xl space-y-6">
      <h2 className="text-2xl font-semibold">Connect your accounts</h2>
      <p className="text-neutral-400 text-sm">
        Your tokens are encrypted and stored only on your backend. The desktop app
        only holds a session token.
      </p>
      <div className="space-y-3">
        <button onClick={connectDiscord}
                className="w-full px-4 py-3 rounded bg-indigo-600 hover:bg-indigo-700 text-left">
          1. Connect Discord →
        </button>
        <button onClick={connectGmail}
                className="w-full px-4 py-3 rounded bg-red-600 hover:bg-red-700 text-left">
          2. Connect Gmail →
        </button>
      </div>
      <p className="text-xs text-neutral-500">
        After approving in your browser, the app will reopen automatically.
      </p>
    </div>
  );
}
