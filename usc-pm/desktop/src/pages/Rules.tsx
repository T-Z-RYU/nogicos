import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Rules() {
  const [rules, setRules] = useState<any[]>([]);
  const [scenario, setScenario] = useState("");
  const [template, setTemplate] = useState("");
  const [autoSend, setAutoSend] = useState(false);

  async function load() { setRules(await api.rules.list()); }
  useEffect(() => { load(); }, []);

  async function add() {
    if (!scenario || !template) return;
    await api.rules.create({ scenario, template, auto_send: autoSend });
    setScenario(""); setTemplate(""); setAutoSend(false);
    load();
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-semibold">Reply Rules</h2>

      <div className="border border-neutral-800 rounded p-4 space-y-3">
        <div>
          <label className="text-sm text-neutral-400">When (plain English scenario)</label>
          <input
            className="mt-1 w-full rounded bg-neutral-900 border border-neutral-800 px-3 py-2 text-sm"
            placeholder="e.g. Professor asks me to confirm attendance for office hours"
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
          />
        </div>
        <div>
          <label className="text-sm text-neutral-400">Reply with</label>
          <textarea
            className="mt-1 w-full rounded bg-neutral-900 border border-neutral-800 px-3 py-2 text-sm h-24"
            placeholder="Yes, I'll be there. Thanks! — [name]"
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
          />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={autoSend} onChange={(e) => setAutoSend(e.target.checked)} />
          Auto-send without confirmation (otherwise queues for your approval)
        </label>
        <button onClick={add} className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700">
          Add Rule
        </button>
      </div>

      <div className="space-y-2">
        {rules.map((r) => (
          <div key={r.id} className="border border-neutral-800 rounded p-3 flex justify-between items-start">
            <div className="text-sm">
              <div className="font-medium">{r.scenario}</div>
              <div className="text-neutral-400 mt-1">→ {r.template}</div>
              {r.auto_send ? <span className="text-xs text-yellow-400">AUTO-SEND</span> : null}
            </div>
            <button
              onClick={async () => { await api.rules.delete(r.id); setRules(rules.filter(x => x.id !== r.id)); }}
              className="text-xs text-red-400 hover:text-red-300"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
