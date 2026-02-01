"use client";

import React, { useState, useEffect } from "react";

interface DumpEntry {
  id: number;
  filename: string;
  timestamp: string;
  dump_type: string;
  record_count: number;
  size_bytes: number;
  metadata?: Record<string, any>;
}

interface DumpSummary {
  total_dumps: number;
  total_records: number;
  total_size_mb: number;
  dumps_by_type: Record<string, number>;
  oldest_dump: string | null;
  newest_dump: string | null;
}

interface JSONDumpManagerProps {
  currentData?: any;
  mode?: "GENERAL" | "COMPANY";
  companyName?: string;
  onLoadDump?: (data: any) => void;
}

const JSONDumpManager: React.FC<JSONDumpManagerProps> = ({
  currentData,
  mode,
  companyName,
  onLoadDump,
}) => {
  const [checklist, setChecklist] = useState<DumpEntry[]>([]);
  const [summary, setSummary] = useState<DumpSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [dumpSettings, setDumpSettings] = useState({
    enabled: true,
    auto_dump: false,
  });

  useEffect(() => {
    loadChecklist();
    loadSummary();
    loadSettings();
  }, []);

  const loadChecklist = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/dumps/checklist");
      const data = await response.json();
      setChecklist(data.dumps || []);
    } catch (error) {
      console.error("Error loading checklist:", error);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/dumps/summary");
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error("Error loading summary:", error);
    }
  };

  const loadSettings = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/config/dump-settings",
      );
      const data = await response.json();
      setDumpSettings({
        enabled: data.enabled ?? true,
        auto_dump: data.auto_dump ?? false,
      });
    } catch (error) {
      console.error("Error loading settings:", error);
    }
  };

  const toggleAutoDump = async () => {
    const newSettings = { ...dumpSettings, auto_dump: !dumpSettings.auto_dump };
    try {
      await fetch("http://localhost:8000/api/config/dump-settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newSettings),
      });
      setDumpSettings(newSettings);
    } catch (error) {
      console.error("Error updating settings:", error);
    }
  };

  const deleteDump = async (filename: string) => {
    if (!confirm(`Delete ${filename}?`)) return;

    try {
      await fetch(`http://localhost:8000/api/dumps/${filename}`, {
        method: "DELETE",
      });
      loadChecklist();
      loadSummary();
    } catch (error) {
      console.error("Error deleting dump:", error);
    }
  };

  const downloadDump = async (filename: string) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/dumps/load/${filename}`,
      );
      const data = await response.json();

      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading dump:", error);
    }
  };

  const loadDump = async (filename: string) => {
    if (!onLoadDump) {
      alert("Load functionality not available");
      return;
    }

    try {
      const response = await fetch(
        `/api/dumps/load/${encodeURIComponent(filename)}`,
      );
      if (!response.ok) {
        throw new Error("Failed to load dump");
      }
      const data = await response.json();
      onLoadDump(data);
      alert(`Loaded ${filename} successfully!`);
    } catch (error) {
      console.error("Error loading dump:", error);
      alert("Failed to load dump file");
    }
  };

  const clearAllDumps = async () => {
    if (
      !confirm(
        "Are you sure you want to delete ALL dumps? This cannot be undone!",
      )
    )
      return;

    try {
      await fetch("http://localhost:8000/api/dumps/clear-all", {
        method: "DELETE",
      });
      loadChecklist();
      loadSummary();
    } catch (error) {
      console.error("Error clearing dumps:", error);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const manualDump = async () => {
    if (!currentData) {
      alert("No data available to dump. Please scrape data first.");
      return;
    }

    setLoading(true);
    try {
      const dumpType = mode === "COMPANY" ? "company" : "general";
      const metadata: Record<string, any> = {
        mode: mode || "GENERAL",
        manual_dump: true,
      };

      if (mode === "COMPANY" && companyName) {
        metadata.company_name = companyName;
      }

      const response = await fetch("http://localhost:8000/api/dumps/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          data: currentData,
          dump_type: dumpType,
          metadata: metadata,
        }),
      });

      if (response.ok) {
        await loadChecklist();
        await loadSummary();
        alert("Manual dump created successfully!");
      } else {
        throw new Error("Failed to create dump");
      }
    } catch (error) {
      console.error("Error creating manual dump:", error);
      alert("Failed to create manual dump. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-slate-900 flex items-center">
          <i className="fas fa-database text-blue-600 mr-2"></i>
          JSON Dump Manager
        </h2>
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-2 text-sm cursor-pointer">
            <input
              type="checkbox"
              checked={dumpSettings.auto_dump ?? false}
              onChange={toggleAutoDump}
              className="rounded border-slate-300"
            />
            <span className="text-slate-700">Auto-dump</span>
          </label>
          <button
            onClick={clearAllDumps}
            className="text-xs text-red-600 hover:text-red-700 font-bold"
          >
            <i className="fas fa-trash mr-1"></i>
            Clear All
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-xs text-blue-600 font-bold mb-1">
              Total Dumps
            </div>
            <div className="text-2xl font-bold text-blue-900">
              {summary.total_dumps}
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-xs text-green-600 font-bold mb-1">
              Total Records
            </div>
            <div className="text-2xl font-bold text-green-900">
              {summary.total_records}
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-xs text-purple-600 font-bold mb-1">
              Total Size
            </div>
            <div className="text-2xl font-bold text-purple-900">
              {summary.total_size_mb} MB
            </div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-xs text-orange-600 font-bold mb-1">Types</div>
            <div className="text-2xl font-bold text-orange-900">
              {summary.dumps_by_type
                ? Object.keys(summary.dumps_by_type).length
                : 0}
            </div>
          </div>
        </div>
      )}

      {/* Dump List */}
      <div className="space-y-3">
        {checklist.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <i className="fas fa-inbox text-4xl mb-3 opacity-20"></i>
            <p className="text-sm">No dumps yet</p>
            <p className="text-xs mt-1">
              Enable auto-dump or manually save scraping results
            </p>
          </div>
        ) : (
          checklist.map((dump) => (
            <div
              key={dump.id}
              className="flex items-start justify-between gap-3 p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-all"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-2 flex-wrap">
                  <i className="fas fa-file-code text-blue-600 flex-shrink-0"></i>
                  <span className="font-mono text-sm font-bold text-slate-900 truncate">
                    {dump.filename}
                  </span>
                  <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full font-bold flex-shrink-0">
                    {dump.dump_type}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-xs text-slate-500 flex-wrap">
                  <span className="flex-shrink-0">
                    <i className="fas fa-clock mr-1"></i>
                    {formatDate(dump.timestamp)}
                  </span>
                  <span className="flex-shrink-0">
                    <i className="fas fa-database mr-1"></i>
                    {dump.record_count} records
                  </span>
                  <span className="flex-shrink-0">
                    <i className="fas fa-file mr-1"></i>
                    {formatBytes(dump.size_bytes)}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-2 flex-shrink-0">
                <button
                  onClick={() => loadDump(dump.filename)}
                  className="text-green-600 hover:text-green-700 p-2 rounded-lg hover:bg-green-50 transition-colors"
                  title="Load to Dashboard"
                >
                  <i className="fas fa-upload"></i>
                </button>
                <button
                  onClick={() => downloadDump(dump.filename)}
                  className="text-blue-600 hover:text-blue-700 p-2 rounded-lg hover:bg-blue-50 transition-colors"
                  title="Download"
                >
                  <i className="fas fa-download"></i>
                </button>
                <button
                  onClick={() => deleteDump(dump.filename)}
                  className="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors"
                  title="Delete"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 pt-4 border-t border-slate-200 space-y-3">
        <button
          onClick={manualDump}
          disabled={!currentData || loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold py-2 px-4 rounded-lg text-sm transition-all flex items-center justify-center"
        >
          <i className="fas fa-save mr-2"></i>
          {loading ? "Saving..." : "Manual Dump"}
        </button>
        <button
          onClick={() => {
            loadChecklist();
            loadSummary();
          }}
          className="w-full bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-2 px-4 rounded-lg text-sm transition-all"
        >
          <i className="fas fa-sync-alt mr-2"></i>
          Refresh
        </button>
      </div>
    </div>
  );
};

export default JSONDumpManager;
