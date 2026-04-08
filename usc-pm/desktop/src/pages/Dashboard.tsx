import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);

  async function load() { setData(await api.macro()); }
  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, []);

  if (!data) return <div>Loading…</div>;

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-semibold">Macro Dashboard</h2>

      <Section title={`⏰ Deadlines (${data.deadlines.length})`}>
        {data.deadlines.length === 0 && <Empty />}
        {data.deadlines.map((d: any) => (
          <Card key={d.id}>
            <div className="font-medium">{d.title}</div>
            <div className="text-xs text-neutral-400">{d.course} · due {d.due_at ?? "TBD"}</div>
            <div className="text-sm mt-1">{d.summary}</div>
          </Card>
        ))}
      </Section>

      <Section title={`✉️ Pending Replies (${data.pending_replies.length})`}>
        {data.pending_replies.length === 0 && <Empty />}
        {data.pending_replies.map((p: any) => (
          <Card key={p.id}>
            <div className="text-xs text-neutral-400">{p.context}</div>
            <div className="text-sm mt-1 whitespace-pre-wrap">{p.draft_body}</div>
            <div className="mt-2 flex gap-2">
              <button onClick={async () => { await api.approve(p.id); load(); }}
                      className="px-3 py-1 rounded bg-green-600/30 hover:bg-green-600/50 text-xs">Approve</button>
              <button onClick={async () => { await api.reject(p.id); load(); }}
                      className="px-3 py-1 rounded bg-red-600/30 hover:bg-red-600/50 text-xs">Reject</button>
            </div>
          </Card>
        ))}
      </Section>

      <Section title="🎮 Recent Unity Progress">
        {data.unity.length === 0 && <Empty />}
        {data.unity.map((u: any) => (
          <Card key={u.id}>
            <div className="text-xs text-neutral-400">{u.created_at}</div>
            <div className="text-sm">{u.entry}</div>
          </Card>
        ))}
      </Section>
    </div>
  );
}

function Section({ title, children }: any) {
  return (
    <div>
      <h3 className="text-sm uppercase tracking-wide text-neutral-400 mb-2">{title}</h3>
      <div className="space-y-2">{children}</div>
    </div>
  );
}
function Card({ children }: any) {
  return <div className="border border-neutral-800 rounded p-3">{children}</div>;
}
function Empty() { return <div className="text-xs text-neutral-500 italic">Nothing yet.</div>; }
