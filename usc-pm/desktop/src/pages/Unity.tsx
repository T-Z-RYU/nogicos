import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Unity() {
  const [entries, setEntries] = useState<any[]>([]);
  const [text, setText] = useState("");

  async function load() { setEntries(await api.unity.list()); }
  useEffect(() => { load(); }, []);

  async function add() {
    if (!text.trim()) return;
    await api.unity.add(text.trim());
    setText("");
    load();
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-semibold">Unity Progress</h2>
      <div className="border border-neutral-800 rounded p-4 space-y-3">
        <textarea
          className="w-full rounded bg-neutral-900 border border-neutral-800 px-3 py-2 text-sm h-24"
          placeholder="What did you ship today? e.g. Implemented enemy AI v2 with patrol states"
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button onClick={add} className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700">
          Log Progress
        </button>
      </div>
      <div className="space-y-2">
        {entries.map((e) => (
          <div key={e.id} className="border border-neutral-800 rounded p-3">
            <div className="text-xs text-neutral-400">{e.created_at}</div>
            <div className="text-sm">{e.entry}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
