"use client";

import React, { useState, useCallback, useMemo } from "react";
import Header from "@/components/Header";
import SignalCard from "@/components/SignalCard";
import SignalModal from "@/components/SignalModal";
import NewsSourcesManager from "@/components/NewsSourcesManager";
import FinancialChart from "@/components/FinancialChart";
import AIInsights from "@/components/AIInsights";
import JSONDumpManager from "@/components/JSONDumpManager";
import { ScraperMode, WorkforceSignal, FinancialData } from "@/types";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const INITIAL_KEYWORDS = [
  "layoffs",
  "retrenchment",
  "hiring freeze",
  "restructuring",
  "productivity",
  "automation",
  "AI adoption",
  "cost-cutting",
  "manpower shortage",
  "wage pressure",
];

export default function Home() {
  const [mode, setMode] = useState<ScraperMode>(ScraperMode.GENERAL);
  const [keywords, setKeywords] = useState<string[]>(INITIAL_KEYWORDS);
  const [newKeyword, setNewKeyword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [signals, setSignals] = useState<WorkforceSignal[]>([]);
  const [financialData, setFinancialData] = useState<FinancialData | null>(
    null,
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressMsg, setProgressMsg] = useState("");
  const [selectedSignal, setSelectedSignal] = useState<WorkforceSignal | null>(
    null,
  );
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAddKeyword = (e: React.FormEvent) => {
    e.preventDefault();
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      setKeywords([...keywords, newKeyword.trim()]);
      setNewKeyword("");
    }
  };

  const removeKeyword = (kw: string) => {
    setKeywords(keywords.filter((k) => k !== kw));
  };

  const handleScrape = async () => {
    setLoading(true);
    setError(null);
    setFinancialData(null);
    setProgressMsg("Connecting to NTUC scraping nodes...");

    try {
      setTimeout(
        () => setProgressMsg("Bypassing restricted gateways..."),
        1500,
      );
      setTimeout(
        () => setProgressMsg("Structuring workforce signals..."),
        3000,
      );

      const response = await fetch("/api/scrape", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mode,
          keywords: mode === ScraperMode.GENERAL ? keywords : undefined,
          companyName: mode === ScraperMode.COMPANY ? companyName : undefined,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to scrape data");
      }

      const results = await response.json();

      // Handle financial data separately if in company mode
      if (mode === ScraperMode.COMPANY && results.financial_data) {
        setFinancialData(results);
        setSignals(results.signals || []);
      } else {
        setSignals(results);
      }
    } catch (err) {
      setError(
        "Scraping session failed. Please check network connectivity and API status.",
      );
      console.error(err);
    } finally {
      setLoading(false);
      setProgressMsg("");
    }
  };

  const handleLoadDump = (data: any) => {
    // Handle loaded dump data - check for nested structure first
    let actualData = data;

    // If data has dump_info wrapper, extract the actual data
    if (data.data) {
      actualData = data.data;
    }

    if (Array.isArray(actualData)) {
      // Array of signals
      setSignals(actualData);
      setFinancialData(null);
    } else if (actualData.signals) {
      // Object with signals and possibly financial data
      setSignals(actualData.signals);
      if (actualData.financial_data || actualData.ticker) {
        setFinancialData(actualData);
      } else {
        setFinancialData(null);
      }
    } else {
      setSignals([]);
      setFinancialData(null);
    }
    setError(null);
  };

  const chartData = useMemo(() => {
    const counts: Record<string, number> = {};
    signals.forEach((s) => {
      const label = s.source_type || "other";
      counts[label] = (counts[label] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [signals]);

  const COLORS = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"];

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="grow max-w-7xl mx-auto w-full px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Sidebar: Controls */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center">
              <i className="fas fa-sliders text-blue-600 mr-2"></i>
              Scraper Configuration
            </h2>

            <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
              <button
                onClick={() => setMode(ScraperMode.GENERAL)}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${mode === ScraperMode.GENERAL ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}
              >
                General Mode
              </button>
              <button
                onClick={() => setMode(ScraperMode.COMPANY)}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${mode === ScraperMode.COMPANY ? "bg-white text-blue-600 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}
              >
                Company Mode
              </button>
            </div>

            {mode === ScraperMode.GENERAL ? (
              <div className="space-y-4">
                <label className="block text-sm font-bold text-slate-700">
                  Target Keywords
                </label>
                <form onSubmit={handleAddKeyword} className="flex gap-2">
                  <input
                    type="text"
                    value={newKeyword}
                    onChange={(e) => setNewKeyword(e.target.value)}
                    placeholder="Add keyword..."
                    className="grow px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                  />
                  <button
                    type="submit"
                    className="bg-slate-900 text-white p-2 rounded-lg hover:bg-slate-800"
                  >
                    <i className="fas fa-plus"></i>
                  </button>
                </form>
                <div className="flex flex-wrap gap-2 pt-2">
                  {keywords.map((kw) => (
                    <span
                      key={kw}
                      className="inline-flex items-center bg-blue-50 text-blue-600 text-xs font-bold px-2.5 py-1 rounded-md border border-blue-100"
                    >
                      {kw}
                      <button
                        onClick={() => removeKeyword(kw)}
                        className="ml-1.5 hover:text-blue-800"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <label className="block text-sm font-bold text-slate-700">
                  Target Company
                </label>
                <input
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="Enter company name (e.g. Grab, Keppel)..."
                  className="w-full px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all"
                />
                <p className="text-xs text-slate-500 italic">
                  * Scraper will look for external mentions and public
                  announcements linked to this entity.
                </p>
              </div>
            )}

            <button
              onClick={handleScrape}
              disabled={
                loading || (mode === ScraperMode.COMPANY && !companyName)
              }
              className="w-full mt-8 bg-blue-600 text-white py-3 rounded-xl font-bold flex items-center justify-center space-x-2 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-all shadow-md active:scale-95"
            >
              {loading ? (
                <>
                  <i className="fas fa-circle-notch animate-spin"></i>
                  <span>Scraping Data...</span>
                </>
              ) : (
                <>
                  <i className="fas fa-bolt"></i>
                  <span>Initialize Scraper</span>
                </>
              )}
            </button>
          </div>

          {/* Analytics Mini-View */}
          {signals.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-4 uppercase tracking-widest">
                Source Distribution
              </h3>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                      stroke="#f1f5f9"
                    />
                    <XAxis
                      dataKey="name"
                      axisLine={false}
                      tickLine={false}
                      fontSize={10}
                      tick={{ fill: "#94a3b8" }}
                    />
                    <Tooltip
                      cursor={{ fill: "#f8fafc" }}
                      contentStyle={{
                        borderRadius: "12px",
                        border: "none",
                        boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                      }}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* News Sources Manager */}
          <NewsSourcesManager />

          {/* JSON Dump Manager */}
          <JSONDumpManager
            currentData={financialData || signals}
            mode={mode}
            companyName={companyName}
            onLoadDump={handleLoadDump}
          />
        </div>

        {/* Right Content Area: Results */}
        <div className="lg:col-span-8">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 flex items-center">
              <i className="fas fa-exclamation-triangle mr-3"></i>
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 bg-white border border-slate-200 border-dashed rounded-3xl">
              <div className="relative mb-6">
                <div className="h-20 w-20 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
                <i className="fas fa-radar text-blue-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-xl"></i>
              </div>
              <p className="text-lg font-bold text-slate-800 mb-2">
                Analyzing Workforce Ecosystem
              </p>
              <p className="text-sm text-slate-500 font-mono animate-pulse">
                {progressMsg}
              </p>
            </div>
          ) : signals.length > 0 || financialData ? (
            <div className="space-y-6">
              {/* Financial Data Section */}
              {financialData && financialData.financial_data && (
                <div className="space-y-6">
                  {/* Company Analysis Header */}
                  <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg">
                    <div className="flex items-start justify-between">
                      <div>
                        <h2 className="text-3xl font-bold mb-2">
                          {companyName} Analysis
                        </h2>
                        {financialData.ai_detection && (
                          <div className="text-sm bg-white/10 px-3 py-2 rounded-lg inline-block mb-3">
                            {financialData.ai_detection.parent_company ? (
                              <>
                                <i className="fas fa-building mr-2"></i>
                                Analyzing via parent company:{" "}
                                <span className="font-bold">
                                  {financialData.ai_detection.parent_company}
                                </span>
                              </>
                            ) : (
                              <>
                                <i className="fas fa-chart-line mr-2"></i>
                                Publicly traded company
                              </>
                            )}
                          </div>
                        )}
                        <div className="flex items-center space-x-4 text-sm opacity-90">
                          <span className="bg-white/20 px-3 py-1 rounded-lg font-mono">
                            {financialData.ticker}
                          </span>
                          <span>
                            {financialData.financial_data.summary.sector}
                          </span>
                          <span>•</span>
                          <span>
                            {financialData.financial_data.summary.industry}
                          </span>
                          {financialData.financial_data.summary.employees && (
                            <>
                              <span>•</span>
                              <span>
                                <i className="fas fa-users mr-1"></i>
                                {financialData.financial_data.summary.employees.toLocaleString()}{" "}
                                employees
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs opacity-75 mb-1">
                          Market Cap
                        </div>
                        <div className="text-lg font-bold">
                          {financialData.financial_data.summary.market_cap
                            ? `$${(financialData.financial_data.summary.market_cap / 1e9).toFixed(2)}B`
                            : "N/A"}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Financial Chart */}
                  {financialData.financial_data.history_data &&
                    financialData.financial_data.history_data.length > 0 && (
                      <FinancialChart
                        data={financialData.financial_data.history_data}
                        companyName={
                          financialData.financial_data.summary.company_name
                        }
                        ticker={financialData.ticker}
                        summary={financialData.financial_data.summary}
                        actualWorkforce={financialData.actual_workforce}
                      />
                    )}

                  {/* AI Insights */}
                  {financialData.ai_analysis && (
                    <AIInsights
                      analysis={financialData.ai_analysis}
                      companyName={
                        financialData.financial_data.summary.company_name
                      }
                    />
                  )}

                  {/* Company Description */}
                  {financialData.financial_data.summary.description &&
                    financialData.financial_data.summary.description !==
                      "N/A" && (
                      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                        <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center">
                          <i className="fas fa-building text-slate-600 mr-2"></i>
                          Company Overview
                        </h3>
                        <p className="text-sm text-slate-700 leading-relaxed">
                          {financialData.financial_data.summary.description}
                        </p>
                      </div>
                    )}
                </div>
              )}

              {/* Workforce Signals */}
              {signals.length > 0 && (
                <>
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-900">
                      Detected Signals
                      <span className="ml-2 bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded-full">
                        {signals.length} findings
                      </span>
                    </h2>
                    <div className="flex items-center space-x-2 text-xs text-slate-400 font-medium">
                      <i className="fas fa-info-circle"></i>
                      <span>Signals sorted by chronological extraction</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {signals.map((signal) => (
                      <SignalCard
                        key={signal.id}
                        signal={signal}
                        onClick={() => {
                          setSelectedSignal(signal);
                          setIsModalOpen(true);
                        }}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-center px-12 bg-white border border-slate-200 border-dashed rounded-3xl">
              <div className="bg-slate-50 h-24 w-24 rounded-full flex items-center justify-center mb-6">
                <i className="fas fa-satellite-dish text-slate-300 text-4xl"></i>
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">
                Awaiting Scraping Instructions
              </h3>
              <p className="text-slate-500 text-sm max-w-md">
                Configure keywords or specify a target company in the control
                panel to begin collecting workforce intelligence signals from
                public sources.
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Persistent Footer */}
      <footer className="bg-slate-900 text-slate-400 py-6 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-center text-[10px] uppercase tracking-widest font-bold">
          <div className="text-slate-500">
            NTUC WORKFORCE INTELLIGENCE PLATFORM &copy;{" "}
            {new Date().getFullYear()} &bull; PROPRIETARY SYSTEM
          </div>
        </div>
      </footer>

      {/* Signal Details Modal */}
      <SignalModal
        signal={selectedSignal}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedSignal(null);
        }}
      />
    </div>
  );
}
