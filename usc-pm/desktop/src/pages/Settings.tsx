import { useEffect, useState } from "react";
import { getBackend, setBackend, clearToken } from "../lib/auth";

export default function Settings() {
  const [url, setUrl] = useState("");
  useEffect(() => { getBackend().then((u) => setUrl(u ?? "")); }, []);
  return (
    <div className="space-y-4 max-w-xl">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <label className="block">
        <span className="text-sm text-neutral-400">Backend URL</span>
        <input
          className="mt-1 w-full rounded bg-neutral-900 border border-neutral-800 px-3 py-2"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://usc-pm.fly.dev"
        />
      </label>
      <button
        className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700"
        onClick={async () => { await setBackend(url); alert("Saved"); }}
      >
        Save
      </button>
      <button
        className="px-4 py-2 rounded bg-red-600/20 hover:bg-red-600/40 text-red-300 ml-2"
        onClick={async () => { await clearToken(); location.reload(); }}
      >
        Sign out
      </button>
    </div>
  );
}
