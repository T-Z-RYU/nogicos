import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Guild = { guild_id: string; guild_name: string; channels: { channel_id: string; channel_name: string }[] };

export default function Channels() {
  const [guilds, setGuilds] = useState<Guild[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [g, current] = await Promise.all([api.servers(), api.channels.list()]);
        setGuilds(g);
        setSelected(new Set(current.map((c: any) => c.channel_id)));
      } catch (e: any) { alert(e.message); }
      setLoading(false);
    })();
  }, []);

  function toggle(id: string) {
    const s = new Set(selected);
    s.has(id) ? s.delete(id) : s.add(id);
    setSelected(s);
  }

  async function save() {
    const flat: any[] = [];
    for (const g of guilds)
      for (const c of g.channels)
        if (selected.has(c.channel_id))
          flat.push({ guild_id: g.guild_id, guild_name: g.guild_name,
                      channel_id: c.channel_id, channel_name: c.channel_name });
    await api.channels.save(flat);
    alert(`Saved ${flat.length} channels`);
  }

  if (loading) return <div>Loading…</div>;
  if (guilds.length === 0)
    return <div className="text-neutral-400">
      No servers found. Make sure the bot is invited to at least one server you're in.
    </div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Channels to monitor</h2>
        <button onClick={save} className="px-4 py-2 rounded bg-blue-600 hover:bg-blue-700">
          Save ({selected.size})
        </button>
      </div>
      {guilds.map((g) => (
        <div key={g.guild_id} className="border border-neutral-800 rounded p-4">
          <h3 className="font-medium mb-2">{g.guild_name}</h3>
          <div className="space-y-1">
            {g.channels.map((c) => (
              <label key={c.channel_id} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selected.has(c.channel_id)}
                  onChange={() => toggle(c.channel_id)}
                />
                #{c.channel_name}
              </label>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
