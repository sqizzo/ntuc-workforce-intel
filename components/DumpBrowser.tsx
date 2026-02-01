"use client";

import React, { useState, useEffect } from "react";

interface DumpFile {
  filename: string;
  size: number;
  created: number;
  modified: number;
  metadata: {
    mode?: string;
    keywords?: string[];
    company_name?: string;
    signal_count?: number;
  };
  signal_count: number;
}

interface DumpBrowserProps {
  onLoadDump: (data: any) => void;
}

const DumpBrowser: React.FC<DumpBrowserProps> = ({ onLoadDump }) => {
  const [dumps, setDumps] = useState<DumpFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedDump, setSelectedDump] = useState<string | null>(null);

  const fetchDumps = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/dumps/list");
      const data = await response.json();
      setDumps(data.dumps || []);
    } catch (error) {
      console.error("Error fetching dumps:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadDump = async (filename: string) => {
    try {
      setLoading(true);
      setSelectedDump(filename);
      const response = await fetch(
        `/api/dumps/load/${encodeURIComponent(filename)}`,
      );
      const data = await response.json();
      onLoadDump(data);
      setIsOpen(false);
    } catch (error) {
      console.error("Error loading dump:", error);
      alert("Failed to load dump file");
    } finally {
      setLoading(false);
      setSelectedDump(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  useEffect(() => {
    if (isOpen) {
      fetchDumps();
    }
  }, [isOpen]);

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-purple-600 hover:bg-purple-700 text-white rounded-full p-4 shadow-lg transition-all z-40 flex items-center space-x-2"
        title="Browse saved dumps"
      >
        <i className="fas fa-folder-open text-xl"></i>
        <span className="font-medium">Load Dump</span>
      </button>

      {/* Dump Browser Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  Browse Saved Dumps
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Load previously saved scraping results
                </p>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {loading && dumps.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <i className="fas fa-spinner fa-spin text-4xl text-purple-600 mb-4"></i>
                    <p className="text-gray-600">Loading dumps...</p>
                  </div>
                </div>
              ) : dumps.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <i className="fas fa-folder-open text-6xl text-gray-300 mb-4"></i>
                    <p className="text-gray-600">No saved dumps found</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  {dumps.map((dump) => (
                    <div
                      key={dump.filename}
                      className={`border border-gray-200 rounded-lg p-4 hover:border-purple-300 hover:shadow-md transition-all cursor-pointer ${
                        selectedDump === dump.filename
                          ? "bg-purple-50 border-purple-400"
                          : "bg-white"
                      }`}
                      onClick={() => loadDump(dump.filename)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            <i className="fas fa-file-code text-purple-600 text-lg"></i>
                            <h3 className="font-semibold text-gray-900">
                              {dump.filename}
                            </h3>
                          </div>

                          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600 mb-2">
                            <div>
                              <span className="font-medium">Signals:</span>{" "}
                              {dump.signal_count}
                            </div>
                            <div>
                              <span className="font-medium">Size:</span>{" "}
                              {formatFileSize(dump.size)}
                            </div>
                            <div className="col-span-2">
                              <span className="font-medium">Modified:</span>{" "}
                              {formatDate(dump.modified)}
                            </div>
                          </div>

                          {/* Metadata badges */}
                          <div className="flex flex-wrap gap-2">
                            {dump.metadata.mode && (
                              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {dump.metadata.mode}
                              </span>
                            )}
                            {dump.metadata.company_name && (
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                                {dump.metadata.company_name}
                              </span>
                            )}
                            {dump.metadata.keywords &&
                              dump.metadata.keywords.length > 0 && (
                                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">
                                  {dump.metadata.keywords.join(", ")}
                                </span>
                              )}
                          </div>
                        </div>

                        <div className="ml-4">
                          {selectedDump === dump.filename ? (
                            <i className="fas fa-spinner fa-spin text-purple-600 text-xl"></i>
                          ) : (
                            <i className="fas fa-chevron-right text-gray-400 text-xl"></i>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
              <button
                onClick={fetchDumps}
                disabled={loading}
                className="text-sm text-purple-600 hover:text-purple-700 font-medium disabled:opacity-50"
              >
                <i className="fas fa-sync-alt mr-2"></i>
                Refresh
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DumpBrowser;
