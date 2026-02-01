"use client";

import React, { useState, useEffect } from "react";

interface GeneralSource {
  name: string;
  url: string;
  enabled: boolean;
}

interface CompanySource {
  name: string;
  search_url: string;
  enabled: boolean;
}

const NewsSourcesManager: React.FC = () => {
  const [generalSources, setGeneralSources] = useState<GeneralSource[]>([]);
  const [companySources, setCompanySources] = useState<CompanySource[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<"general" | "company">("general");
  const [showAddForm, setShowAddForm] = useState(false);
  const [newGeneralSource, setNewGeneralSource] = useState({
    name: "",
    url: "",
    enabled: true,
  });
  const [newCompanySource, setNewCompanySource] = useState({
    name: "",
    search_url: "",
    enabled: true,
  });

  const fetchSources = async () => {
    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/config/news-sources`);
      if (response.ok) {
        const data = await response.json();
        setGeneralSources(data.general_sources || []);
        setCompanySources(data.company_sources || []);
      }
    } catch (error) {
      console.error("Failed to fetch news sources:", error);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleAddGeneralSource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGeneralSource.name.trim() || !newGeneralSource.url.trim()) return;

    setLoading(true);
    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/config/news-sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newGeneralSource, type: "general" }),
      });

      if (response.ok) {
        await fetchSources();
        setNewGeneralSource({ name: "", url: "", enabled: true });
        setShowAddForm(false);
      }
    } catch (error) {
      console.error("Failed to add general source:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCompanySource = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCompanySource.name.trim() || !newCompanySource.search_url.trim())
      return;

    setLoading(true);
    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/config/news-sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newCompanySource, type: "company" }),
      });

      if (response.ok) {
        await fetchSources();
        setNewCompanySource({ name: "", search_url: "", enabled: true });
        setShowAddForm(false);
      }
    } catch (error) {
      console.error("Failed to add company source:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSource = async (
    sourceType: "general" | "company",
    index: number,
  ) => {
    const sources = sourceType === "general" ? generalSources : companySources;
    const source = sources[index];
    const updatedSource = { ...source, enabled: !source.enabled };

    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/config/news-sources/${sourceType}/${index}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedSource),
        },
      );

      if (response.ok) {
        await fetchSources();
      }
    } catch (error) {
      console.error("Failed to toggle source:", error);
    }
  };

  const handleDeleteSource = async (
    sourceType: "general" | "company",
    index: number,
  ) => {
    if (!confirm("Are you sure you want to delete this news source?")) return;

    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(
        `${backendUrl}/api/config/news-sources/${sourceType}/${index}`,
        {
          method: "DELETE",
        },
      );

      if (response.ok) {
        await fetchSources();
      }
    } catch (error) {
      console.error("Failed to delete source:", error);
    }
  };

  const renderSourcesList = (sourceType: "general" | "company") => {
    const sources = sourceType === "general" ? generalSources : companySources;
    const urlKey = sourceType === "general" ? "url" : "search_url";

    return (
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {sources.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">
            No {sourceType} sources configured
          </p>
        ) : (
          sources.map((source, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-gray-900 truncate text-sm">
                  {source.name}
                </h4>
                <p className="text-xs text-gray-500 truncate">
                  {(source as any)[urlKey]}
                </p>
                {sourceType === "company" && (
                  <p className="text-xs text-blue-600 mt-1">
                    Use {"{query}"} for search parameter
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 ml-2">
                <button
                  onClick={() => handleToggleSource(sourceType, index)}
                  className={`px-2 py-1 text-xs rounded-full ${
                    source.enabled
                      ? "bg-green-100 text-green-700"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {source.enabled ? "Active" : "Inactive"}
                </button>
                <button
                  onClick={() => handleDeleteSource(sourceType, index)}
                  className="text-red-600 hover:text-red-800 p-1"
                >
                  <i className="fas fa-trash text-xs"></i>
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    );
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-gray-900 text-sm flex items-center">
          <i className="fas fa-newspaper mr-2 text-blue-600"></i>
          News Sources
        </h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="text-xs bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700 transition-colors"
        >
          {showAddForm ? "Cancel" : "+ Add Source"}
        </button>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 mb-4 border-b border-gray-200">
        <button
          onClick={() => {
            setActiveTab("general");
            setShowAddForm(false);
          }}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === "general"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          General News
          <span className="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
            {generalSources.length}
          </span>
        </button>
        <button
          onClick={() => {
            setActiveTab("company");
            setShowAddForm(false);
          }}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === "company"
              ? "text-blue-600 border-b-2 border-blue-600"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Company Search
          <span className="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded-full">
            {companySources.length}
          </span>
        </button>
      </div>

      {/* Add Form */}
      {showAddForm && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          {activeTab === "general" ? (
            <form onSubmit={handleAddGeneralSource} className="space-y-2">
              <input
                type="text"
                placeholder="Source name (e.g., Straits Times)"
                value={newGeneralSource.name}
                onChange={(e) =>
                  setNewGeneralSource({
                    ...newGeneralSource,
                    name: e.target.value,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
              />
              <input
                type="url"
                placeholder="URL (e.g., https://www.straitstimes.com/singapore)"
                value={newGeneralSource.url}
                onChange={(e) =>
                  setNewGeneralSource({
                    ...newGeneralSource,
                    url: e.target.value,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Adding..." : "Add General Source"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleAddCompanySource} className="space-y-2">
              <input
                type="text"
                placeholder="Source name (e.g., Straits Times Search)"
                value={newCompanySource.name}
                onChange={(e) =>
                  setNewCompanySource({
                    ...newCompanySource,
                    name: e.target.value,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
              />
              <input
                type="text"
                placeholder="Search URL with {query} placeholder"
                value={newCompanySource.search_url}
                onChange={(e) =>
                  setNewCompanySource({
                    ...newCompanySource,
                    search_url: e.target.value,
                  })
                }
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg"
              />
              <p className="text-xs text-gray-600">
                Example: https://www.straitstimes.com/search?searchkey=
                {"{query}"}&sort=relevancydate
              </p>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? "Adding..." : "Add Company Search Source"}
              </button>
            </form>
          )}
        </div>
      )}

      {/* Sources List */}
      {renderSourcesList(activeTab)}
    </div>
  );
};

export default NewsSourcesManager;
