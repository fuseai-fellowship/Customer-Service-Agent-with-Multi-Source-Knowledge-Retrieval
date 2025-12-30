// src/pages/Restaurant.jsx
import React, { useState, useEffect, useCallback } from "react";
import { Box, Tab, Tabs } from "@mui/material";
import {
  getRestaurant,
  getKnowledge,
  createKnowledge,
  updateKnowledge,
  deleteKnowledge,
} from "../lib/api";
import KnowledgeTable from "../components/KnowledgeTable";
import KnowledgeFormModal from "../components/KnowledgeFormModal";

const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function Restaurant() {
  const [tab, setTab] = useState(0);
  const [restaurantData, setRestaurantData] = useState(null);

  // Knowledge Base State
  const [kbRows, setKbRows] = useState([]);
  const [kbLoading, setKbLoading] = useState(false);
  const [isKbModalOpen, setKbModalOpen] = useState(false);
  const [editingKb, setEditingKb] = useState(null);

  // Load Restaurant Info (Run once)
  useEffect(() => {
    getRestaurant().then(setRestaurantData);
  }, []);

  // Load KB Data
  const loadKb = useCallback(async () => {
    setKbLoading(true);
    try {
      const data = await getKnowledge();
      setKbRows(data);
    } catch (error) {
      console.error("Failed to load KB", error);
    } finally {
      setKbLoading(false);
    }
  }, []);

  // Load KB initially so it's available for the read-only view too
  useEffect(() => {
    loadKb();
  }, [loadKb]);

  // --- KB Handlers ---
  const handleKbCrud = (action, data) => {
    if (action === "create") {
      setEditingKb(null);
      setKbModalOpen(true);
    } else if (action === "edit") {
      setEditingKb(data);
      setKbModalOpen(true);
    } else if (action === "delete") {
      if (window.confirm(`Delete topic "${data.topic}"?`)) {
        deleteKnowledge(data.id).then(loadKb);
      }
    }
  };

  const handleKbSubmit = async (formData) => {
    try {
      if (editingKb) {
        await updateKnowledge(editingKb.id, formData);
      } else {
        await createKnowledge(formData);
      }
      setKbModalOpen(false);
      loadKb();
    } catch (err) {
      alert("Failed to save. Check console.");
      console.error(err);
    }
  };

  // Helper to group adjacent days with same hours
  const getGroupedHours = (hours) => {
    if (!hours || hours.length === 0) return [];
    const sorted = [...hours].sort((a, b) => a.day_of_week - b.day_of_week);

    const groups = [];
    let currentGroup = {
      startDay: sorted[0].day_of_week,
      endDay: sorted[0].day_of_week,
      time: `${sorted[0].open_time}–${sorted[0].close_time}`,
    };

    for (let i = 1; i < sorted.length; i++) {
      const h = sorted[i];
      const timeStr = `${h.open_time}–${h.close_time}`;
      if (
        timeStr === currentGroup.time &&
        h.day_of_week === currentGroup.endDay + 1
      ) {
        currentGroup.endDay = h.day_of_week;
      } else {
        groups.push(currentGroup);
        currentGroup = {
          startDay: h.day_of_week,
          endDay: h.day_of_week,
          time: timeStr,
        };
      }
    }
    groups.push(currentGroup);
    return groups;
  };

  // Helper to format the day range string (e.g. "Everyday" or "Mon-Fri")
  const formatDayRange = (start, end) => {
    if (start === 0 && end === 6) return "Everyday";
    if (start === end) return dayNames[start];
    return `${dayNames[start]}–${dayNames[end]}`;
  };

  return (
    <div className="space-y-4">
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="General Info" />
          <Tab label="Knowledge Base (admin)" />
        </Tabs>
      </Box>

      {/* --- Tab 0: General Info (Read Only) --- */}
      {tab === 0 && restaurantData ? (
        <div className="space-y-6 animate-in fade-in duration-500">
          <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            {/* Header */}
            <div className="mb-6">
              <h2 className="text-2xl font-semibold">{restaurantData.name}</h2>
              {restaurantData.slogan && (
                <p className="text-slate-500 mt-1">{restaurantData.slogan}</p>
              )}
            </div>

            {/* 3-Column Grid: Address | Phone | Hours */}
            <div className="grid md:grid-cols-3 gap-4">
              {/* Address Card */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-center">
                <div className="text-slate-500 text-xs uppercase font-bold mb-1">
                  Address
                </div>
                <div className="font-medium text-slate-900">
                  {restaurantData.address || "-"}
                </div>
              </div>

              {/* Phone Card */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex flex-col justify-center">
                <div className="text-slate-500 text-xs uppercase font-bold mb-1">
                  Phone
                </div>
                <div className="font-medium text-slate-900">
                  {restaurantData.phone || "-"}
                </div>
              </div>

              {/* Opening Hours Card */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <div className="text-slate-500 text-xs uppercase font-bold mb-2">
                  Opening Hours
                </div>
                <div className="space-y-1 text-sm">
                  {getGroupedHours(restaurantData.hours).map((group, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between text-slate-700"
                    >
                      <span className="font-medium">
                        {formatDayRange(group.startDay, group.endDay)}
                      </span>
                      <span>{group.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* About Section */}
            {restaurantData.about && (
              <div className="mt-6">
                <div className="text-slate-500 text-xs uppercase font-bold mb-2">
                  About
                </div>
                <p className="text-slate-700 leading-relaxed text-sm">
                  {restaurantData.about}
                </p>
              </div>
            )}
          </section>

          {/* Knowledge Base Read-Only Section */}
          <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="mb-6 border-b border-slate-100 pb-4">
              <h3 className="text-lg font-semibold text-slate-900">
                AI Knowledge Base
              </h3>
              <p className="text-slate-500 text-sm">
                Basic Information.
                Switch to the "Knowledge Base" tab to edit these entries.
              </p>
            </div>

            <div className="grid gap-4">
              {kbRows.length === 0 ? (
                <div className="text-center py-8 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                  <p className="text-slate-400 italic">
                    No knowledge base entries found.
                  </p>
                </div>
              ) : (
                kbRows.map((item) => (
                  <div
                    key={item.id}
                    className="group bg-slate-50 p-4 rounded-xl border border-slate-100 hover:border-slate-200 transition-colors"
                  >
                    <h4 className="font-medium text-slate-900 mb-1 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                      {item.topic || "Untitled Topic"}
                    </h4>
                    <div className="text-slate-600 text-sm leading-relaxed whitespace-pre-wrap pl-3.5 border-l-2 border-slate-200">
                      {item.content}
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>
        </div>
      ) : (
        tab === 0 && (
          <div className="p-8 text-center text-slate-500">Loading info...</div>
        )
      )}

      {/* --- Tab 1: Knowledge Base Management (Editable) --- */}
      {tab === 1 && (
        <div className="animate-in fade-in duration-500">
          <KnowledgeTable
            rows={kbRows}
            onCrud={handleKbCrud}
            loading={kbLoading}
          />
          <KnowledgeFormModal
            open={isKbModalOpen}
            onClose={() => setKbModalOpen(false)}
            onSubmit={handleKbSubmit}
            initialData={editingKb}
          />
        </div>
      )}
    </div>
  );
}
