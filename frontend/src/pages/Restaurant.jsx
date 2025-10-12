import React from "react";
import { getRestaurant } from "../lib/api";

const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function Restaurant() {
  const [data, setData] = React.useState(null);
  React.useEffect(() => {
    getRestaurant().then(setData);
  }, []);

  if (!data) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6">
      <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-2xl font-semibold">{data.name}</h2>
        {data.slogan && <p className="text-slate-500 mt-1">{data.slogan}</p>}
        <div className="mt-4 grid sm:grid-cols-2 gap-4 text-sm">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-500">Address</div>
            <div className="font-medium">{data.address || "-"}</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <div className="text-slate-500">Phone</div>
            <div className="font-medium">{data.phone || "-"}</div>
          </div>
        </div>
        {data.about && <p className="mt-4 text-slate-700">{data.about}</p>}
      </section>

      <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-3">Opening Hours</h3>
        <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {data.hours.map((h) => (
            <li
              key={h.day_of_week}
              className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-50 border border-slate-200"
            >
              <span className="font-medium">{dayNames[h.day_of_week]}</span>
              <span className="text-slate-600">
                {h.open_time}–{h.close_time}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
