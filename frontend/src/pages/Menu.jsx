import React from "react";
import { getMenu } from "../lib/api";

function Tag({ children }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 text-xs">
      {children}
    </span>
  );
}

export default function Menu() {
  const [items, setItems] = React.useState([]);
  const [q, setQ] = React.useState("");
  const [tag, setTag] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  async function load() {
    setLoading(true);
    const data = await getMenu({ q: q || undefined, tag: tag || undefined });
    setItems(data);
    setLoading(false);
  }
  React.useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-4">
      <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-slate-400"
            placeholder="Search (e.g., momo, soup, grilled)"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <input
            className="sm:w-56 rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-slate-400"
            placeholder="Tag (e.g., vegan)"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
          />
          <button
            onClick={load}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </div>
      </div>

      {items.length === 0 && !loading ? (
        <p className="text-slate-500">No items found.</p>
      ) : (
        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((it) => (
            <li
              key={it.id}
              className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-3">
                <h4 className="font-semibold">{it.name}</h4>
                <span
                  className={`text-sm px-2 py-0.5 rounded-md ${
                    it.availability
                      ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                      : "bg-rose-50 text-rose-700 border border-rose-200"
                  }`}
                >
                  {it.availability ? "Available" : "Unavailable"}
                </span>
              </div>
              {it.description && (
                <p className="text-sm text-slate-600 mt-1">{it.description}</p>
              )}
              <div className="mt-3 flex items-center justify-between">
                <div className="flex flex-wrap gap-1">
                  {(it.tags || "")
                    .split(",")
                    .filter(Boolean)
                    .map((t) => (
                      <Tag key={t}>{t.trim()}</Tag>
                    ))}
                </div>
                <div className="font-semibold">NPR {it.price_npr}</div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
