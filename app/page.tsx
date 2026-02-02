"use client";

import React, { useState, useCallback, useMemo } from "react";
import Header from "@/components/Header";
import SignalCard from "@/components/SignalCard";
import SignalModal from "@/components/SignalModal";
import NewsSourcesManager from "@/components/NewsSourcesManager";
import FinancialChart from "@/components/FinancialChart";
import AIInsights from "@/components/AIInsights";
import JSONDumpManager from "@/components/JSONDumpManager";
import {
  ScraperMode,
  WorkforceSignal,
  FinancialData,
  HypothesisAnalysis,
  PrimarySignal,
  SupportingSignal,
} from "@/types";
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
  const [hypothesisAnalysis, setHypothesisAnalysis] =
    useState<HypothesisAnalysis | null>(null);
  const [hypothesisLoading, setHypothesisLoading] = useState(false);
  const [selectedPrimarySignal, setSelectedPrimarySignal] =
    useState<PrimarySignal | null>(null);

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

  const runHypothesisAnalysis = async (
    company: string,
    signalsData?: any[],
    financialInfo?: any,
  ) => {
    if (!company) return;

    setHypothesisLoading(true);
    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/hypothesis/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: company,
          signals: signalsData,
          financial_data: financialInfo,
        }),
      });

      if (response.ok) {
        const analysis: HypothesisAnalysis = await response.json();
        setHypothesisAnalysis(analysis);
      } else {
        console.log("Hypothesis analysis not available for this company");
        setHypothesisAnalysis(null);
      }
    } catch (error) {
      console.error("Error running hypothesis analysis:", error);
      setHypothesisAnalysis(null);
    } finally {
      setHypothesisLoading(false);
    }
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
        // Auto-run hypothesis analysis for company mode with the scraped data
        if (companyName) {
          runHypothesisAnalysis(
            companyName,
            results.signals,
            results.financial_data,
          );
        }
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

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "high":
        return "text-red-600 bg-red-100 border-red-300";
      case "medium":
        return "text-yellow-600 bg-yellow-100 border-yellow-300";
      case "low":
        return "text-green-600 bg-green-100 border-green-300";
      default:
        return "text-gray-600 bg-gray-100 border-gray-300";
    }
  };

  const getSupportingSignals = (
    primarySignal: PrimarySignal,
  ): SupportingSignal[] => {
    if (!hypothesisAnalysis) return [];
    return hypothesisAnalysis.supporting_signals.filter((ss) =>
      primarySignal.supporting_signal_ids.includes(ss.id),
    );
  };

  const renderSourceDistribution = (distribution: {
    News: number;
    Social: number;
    Financial: number;
  }) => {
    const total =
      distribution.News + distribution.Social + distribution.Financial;
    if (total === 0) return null;

    const newsPercent = (distribution.News / total) * 100;
    const socialPercent = (distribution.Social / total) * 100;
    const financialPercent = (distribution.Financial / total) * 100;

    return (
      <div className="mt-3">
        <p className="text-xs font-medium text-gray-700 mb-2">
          Source Distribution:
        </p>
        <div className="w-full h-5 flex rounded-lg overflow-hidden">
          {newsPercent > 0 && (
            <div
              className="bg-blue-500 flex items-center justify-center text-xs text-white font-medium"
              style={{ width: `${newsPercent}%` }}
              title={`News: ${distribution.News}`}
            >
              {newsPercent > 15 && `News ${distribution.News}`}
            </div>
          )}
          {socialPercent > 0 && (
            <div
              className="bg-purple-500 flex items-center justify-center text-xs text-white font-medium"
              style={{ width: `${socialPercent}%` }}
              title={`Social: ${distribution.Social}`}
            >
              {socialPercent > 15 && `Social ${distribution.Social}`}
            </div>
          )}
          {financialPercent > 0 && (
            <div
              className="bg-green-500 flex items-center justify-center text-xs text-white font-medium"
              style={{ width: `${financialPercent}%` }}
              title={`Financial: ${distribution.Financial}`}
            >
              {financialPercent > 15 && `Financial ${distribution.Financial}`}
            </div>
          )}
        </div>
        <div className="flex gap-3 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-blue-500 rounded"></div>
            <span>News ({distribution.News})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-purple-500 rounded"></div>
            <span>Social ({distribution.Social})</span>
          </div>
          {distribution.Financial > 0 && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded"></div>
              <span>Financial ({distribution.Financial})</span>
            </div>
          )}
        </div>
      </div>
    );
  };

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

                  {/* Hypothesis Analysis - Primary & Supporting Signals */}
                  {hypothesisLoading && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                      <div className="flex items-center justify-center py-8">
                        <div className="text-center">
                          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                          <p className="text-gray-600">
                            Analyzing risk signals...
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {hypothesisAnalysis && !hypothesisLoading && (
                    <>
                      {/* Risk Summary */}
                      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                        <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
                          <i className="fas fa-exclamation-triangle text-slate-600 mr-2"></i>
                          Risk Assessment Summary
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                          <div
                            className={`p-3 rounded-lg border-2 ${getRiskColor(hypothesisAnalysis.risk_summary.overall_risk)}`}
                          >
                            <p className="text-xs font-medium">Overall Risk</p>
                            <p className="text-xl font-bold uppercase">
                              {hypothesisAnalysis.risk_summary.overall_risk}
                            </p>
                          </div>
                          <div className="p-3 rounded-lg border-2 border-gray-300 bg-gray-50">
                            <p className="text-xs font-medium text-gray-700">
                              Primary Signals
                            </p>
                            <p className="text-xl font-bold text-gray-900">
                              {
                                hypothesisAnalysis.risk_summary
                                  .primary_signal_count
                              }
                            </p>
                          </div>
                          <div className="p-3 rounded-lg border-2 border-gray-300 bg-gray-50">
                            <p className="text-xs font-medium text-gray-700">
                              Confidence
                            </p>
                            <p className="text-xl font-bold text-gray-900 uppercase">
                              {hypothesisAnalysis.risk_summary.confidence}
                            </p>
                          </div>
                        </div>
                        <div className="text-sm">
                          <p className="text-gray-700 mb-2">
                            {hypothesisAnalysis.risk_summary.summary}
                          </p>
                          <p className="text-xs text-gray-600 italic">
                            {hypothesisAnalysis.risk_summary.recommendation}
                          </p>
                        </div>
                      </div>

                      {/* Primary Signals */}
                      {hypothesisAnalysis.primary_signals.length > 0 && (
                        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
                            <i className="fas fa-signal text-slate-600 mr-2"></i>
                            Primary Risk Signals
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {hypothesisAnalysis.primary_signals.map(
                              (primarySignal) => (
                                <div
                                  key={primarySignal.id}
                                  className="border-2 border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                                  onClick={() =>
                                    setSelectedPrimarySignal(primarySignal)
                                  }
                                >
                                  <div className="flex justify-between items-start mb-2">
                                    <h4 className="font-bold text-base text-gray-800">
                                      {primarySignal.title}
                                    </h4>
                                    <span
                                      className={`px-2 py-1 rounded-full text-xs font-semibold ${getRiskColor(
                                        primarySignal.risk_level,
                                      )}`}
                                    >
                                      {primarySignal.risk_level.toUpperCase()}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-600 mb-3">
                                    {primarySignal.description}
                                  </p>
                                  <div className="mb-3">
                                    <p className="text-xs font-medium text-gray-700 mb-1">
                                      Key Indicators:
                                    </p>
                                    <div className="flex flex-wrap gap-1">
                                      {primarySignal.key_indicators.map(
                                        (indicator, idx) => (
                                          <span
                                            key={idx}
                                            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                                          >
                                            {indicator}
                                          </span>
                                        ),
                                      )}
                                    </div>
                                  </div>
                                  {renderSourceDistribution(
                                    primarySignal.source_distribution,
                                  )}
                                  <button className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium">
                                    View{" "}
                                    {primarySignal.supporting_signal_ids.length}{" "}
                                    Supporting Signals →
                                  </button>
                                </div>
                              ),
                            )}
                          </div>
                        </div>
                      )}
                    </>
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

      {/* Supporting Signals Modal */}
      {selectedPrimarySignal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedPrimarySignal(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold text-gray-800">
                    {selectedPrimarySignal.title}
                  </h3>
                  <p className="text-gray-600 mt-1">
                    {selectedPrimarySignal.description}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPrimarySignal(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl font-bold ml-4"
                >
                  ×
                </button>
              </div>
              {renderSourceDistribution(
                selectedPrimarySignal.source_distribution,
              )}
            </div>

            <div className="p-6 space-y-4">
              <h4 className="text-lg font-bold text-gray-800 mb-3">
                Supporting Signals
              </h4>
              {getSupportingSignals(selectedPrimarySignal).map((signal) => (
                <div
                  key={signal.id}
                  className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-semibold text-gray-800">
                      {signal.title}
                    </h5>
                    <span
                      className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(
                        signal.severity,
                      )}`}
                    >
                      {signal.severity}
                    </span>
                  </div>
                  <div className="flex gap-4 text-xs text-gray-600 mb-2">
                    <span className="flex items-center gap-1">
                      <span className="font-medium">Source:</span>
                      {signal.source_type}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="font-medium">Timeframe:</span>
                      {signal.timeframe}
                    </span>
                  </div>
                  <div className="mt-2">
                    <p className="text-xs font-medium text-gray-700 mb-1">
                      Evidence:
                    </p>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      {signal.evidence}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
