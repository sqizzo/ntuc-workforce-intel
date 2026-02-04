"use client";

import React, { useState } from "react";
import {
  HypothesisAnalysis,
  PrimarySignal,
  SupportingSignal,
  OverallRiskScore,
} from "@/types";

interface HypothesisViewerProps {
  companyName?: string;
  dumpFilename?: string;
}

export default function HypothesisViewer({
  companyName,
  dumpFilename,
}: HypothesisViewerProps) {
  const [analysis, setAnalysis] = useState<HypothesisAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPrimarySignal, setSelectedPrimarySignal] =
    useState<PrimarySignal | null>(null);
  const [searchCompany, setSearchCompany] = useState(companyName || "");

  const performAnalysis = async () => {
    if (!searchCompany.trim()) {
      setError("Please enter a company name");
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const backendUrl =
        process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/hypothesis/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: searchCompany,
          dump_filename: dumpFilename,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 404) {
          throw new Error(
            `No data found for "${searchCompany}". Please scrape company data first using the main scraper.`,
          );
        }
        throw new Error(errorData.detail || "Analysis failed");
      }

      const data: HypothesisAnalysis = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

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

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case "catastrophic":
        return "text-red-900 bg-red-200 border-red-500";
      case "severe":
        return "text-red-700 bg-red-100 border-red-400";
      case "high":
        return "text-orange-700 bg-orange-100 border-orange-400";
      case "moderate":
        return "text-yellow-700 bg-yellow-100 border-yellow-400";
      case "low":
        return "text-green-700 bg-green-100 border-green-400";
      case "minimal":
        return "text-blue-700 bg-blue-100 border-blue-400";
      default:
        return "text-gray-600 bg-gray-100 border-gray-300";
    }
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 80) return "text-red-700 font-bold";
    if (score >= 60) return "text-orange-700 font-bold";
    if (score >= 40) return "text-yellow-700 font-semibold";
    if (score >= 20) return "text-green-700 font-semibold";
    return "text-blue-700";
  };

  const getSupportingSignals = (
    primarySignal: PrimarySignal,
  ): SupportingSignal[] => {
    if (!analysis) return [];
    return analysis.supporting_signals.filter((ss) =>
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
      <div className="mt-4">
        <p className="text-sm font-medium text-gray-700 mb-2">
          Source Distribution:
        </p>
        <div className="w-full h-6 flex rounded-lg overflow-hidden">
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
        <div className="flex gap-4 mt-2 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span>News ({distribution.News})</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-purple-500 rounded"></div>
            <span>Social ({distribution.Social})</span>
          </div>
          {distribution.Financial > 0 && (
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 rounded"></div>
              <span>Financial ({distribution.Financial})</span>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Risk Hypothesis Engine
        </h1>
        <p className="text-gray-600 mb-2">
          Analyze company risk based on news, social forums, and financial data
        </p>
        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800">
          <i className="fas fa-info-circle mr-2"></i>
          <strong>Note:</strong> This analysis requires existing company data
          from previous scraping. If no data is found, please scrape the company
          first using the{" "}
          <a href="/" className="underline hover:text-blue-900 font-medium">
            main scraper
          </a>
          .
        </div>

        <div className="flex gap-4">
          <input
            type="text"
            value={searchCompany}
            onChange={(e) => setSearchCompany(e.target.value)}
            placeholder="Enter company name..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            onClick={performAnalysis}
            disabled={loading || !searchCompany.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? "Analyzing..." : "Analyze Risk"}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <i className="fas fa-exclamation-circle text-red-600 text-xl mt-0.5"></i>
              <div className="flex-1">
                <p className="text-red-700 font-medium mb-2">{error}</p>
                {error.includes("No data found") && (
                  <div className="text-sm text-red-600">
                    <p className="mb-2">
                      To analyze this company, you need to first scrape data:
                    </p>
                    <ol className="list-decimal ml-5 space-y-1">
                      <li>
                        Go to the{" "}
                        <a
                          href="/"
                          className="underline hover:text-red-800 font-medium"
                        >
                          main scraper page
                        </a>
                      </li>
                      <li>
                        Select <strong>Company Mode</strong> or{" "}
                        <strong>Financial Mode</strong>
                      </li>
                      <li>Enter the company name or ticker symbol</li>
                      <li>Click "Start Scraping" to collect data</li>
                      <li>Return here to run the hypothesis analysis</li>
                    </ol>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {analysis && !loading && (
        <div className="space-y-6">
          {/* Overall Risk Score - Featured Section */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-8 border-2 border-blue-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-3xl font-bold text-gray-800">
                Overall Risk Assessment
              </h2>
              <div
                className={`px-6 py-3 rounded-full text-xl font-bold border-3 ${getRiskLevelColor(analysis.overall_risk_score.level)}`}
              >
                {analysis.overall_risk_score.level.toUpperCase()}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white rounded-lg p-6 shadow-md border border-gray-200">
                <p className="text-sm font-medium text-gray-600 mb-2">
                  Risk Score
                </p>
                <p
                  className={`text-5xl font-bold ${getRiskScoreColor(analysis.overall_risk_score.score)}`}
                >
                  {analysis.overall_risk_score.score}
                  <span className="text-2xl text-gray-500">/100</span>
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-md border border-gray-200">
                <p className="text-sm font-medium text-gray-600 mb-2">
                  Confidence
                </p>
                <p className="text-3xl font-bold text-blue-700 uppercase">
                  {analysis.overall_risk_score.confidence.replace("_", " ")}
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-md border border-gray-200">
                <p className="text-sm font-medium text-gray-600 mb-2">
                  Company
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {analysis.company_name}
                </p>
              </div>
            </div>

            <div className="bg-white rounded-lg p-6 shadow-md border border-gray-200">
              <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center">
                <i className="fas fa-brain mr-2 text-purple-600"></i>
                AI Risk Analysis
              </h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.overall_risk_score.reasoning}
              </p>
            </div>
          </div>

          {/* Major Hypothesis - Key Insight */}
          <div className="bg-white rounded-lg shadow-lg p-8 border-l-4 border-purple-500">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <i className="fas fa-lightbulb mr-3 text-yellow-500"></i>
              Major Hypothesis
            </h2>
            <div className="bg-purple-50 rounded-lg p-6 border border-purple-200">
              <p className="text-gray-800 text-lg leading-relaxed">
                {analysis.major_hypothesis}
              </p>
            </div>
          </div>

          {/* Risk Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Risk Assessment: {analysis.company_name}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div
                className={`p-4 rounded-lg border-2 ${getRiskColor(analysis.risk_summary.overall_risk)}`}
              >
                <p className="text-sm font-medium">Overall Risk</p>
                <p className="text-2xl font-bold uppercase">
                  {analysis.risk_summary.overall_risk}
                </p>
              </div>
              <div className="p-4 rounded-lg border-2 border-gray-300 bg-gray-50">
                <p className="text-sm font-medium text-gray-700">
                  Primary Signals
                </p>
                <p className="text-2xl font-bold text-gray-900">
                  {analysis.risk_summary.primary_signal_count}
                </p>
              </div>
              <div className="p-4 rounded-lg border-2 border-gray-300 bg-gray-50">
                <p className="text-sm font-medium text-gray-700">Confidence</p>
                <p className="text-2xl font-bold text-gray-900 uppercase">
                  {analysis.risk_summary.confidence}
                </p>
              </div>
            </div>
            <div className="mb-4">
              <p className="text-gray-700 mb-2">
                {analysis.risk_summary.summary}
              </p>
              <p className="text-sm text-gray-600 italic">
                {analysis.risk_summary.recommendation}
              </p>
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <p>
                Data Sources: {analysis.data_sources.news_count} news articles,{" "}
                {analysis.data_sources.social_count} social posts
              </p>
              <p>
                Analysis Time:{" "}
                {new Date(analysis.analysis_timestamp).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Primary Signals */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              Primary Risk Signals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis.primary_signals.map((primarySignal) => (
                <div
                  key={primarySignal.id}
                  className="border-2 border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedPrimarySignal(primarySignal)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h4 className="font-bold text-lg text-gray-800 mb-1">
                        {primarySignal.title}
                      </h4>
                      <div className="flex items-center gap-3">
                        <span
                          className={`text-3xl ${getRiskScoreColor(primarySignal.risk_score)}`}
                        >
                          {primarySignal.risk_score}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(
                            primarySignal.risk_level,
                          )}`}
                        >
                          {primarySignal.risk_level.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {primarySignal.description}
                  </p>
                  <div className="bg-gray-50 rounded p-3 mb-3 border border-gray-200">
                    <p className="text-xs font-semibold text-gray-700 mb-1">
                      Risk Analysis:
                    </p>
                    <p className="text-xs text-gray-700 italic">
                      {primarySignal.risk_reasoning}
                    </p>
                  </div>
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-700 mb-1">
                      Key Indicators:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {primarySignal.key_indicators.map((indicator, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {indicator}
                        </span>
                      ))}
                    </div>
                  </div>
                  {renderSourceDistribution(primarySignal.source_distribution)}
                  <button className="mt-3 text-sm text-blue-600 hover:text-blue-800 font-medium">
                    View {primarySignal.supporting_signal_ids.length} Supporting
                    Signals →
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Modal for Supporting Signals */}
          {selectedPrimarySignal && (
            <div
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
              onClick={() => setSelectedPrimarySignal(null)}
            >
              <div
                className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="sticky top-0 bg-white border-b border-gray-200 p-6">
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
                      className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
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
                        <div className="flex-1">
                          <h5 className="font-semibold text-gray-800 mb-1">
                            {signal.title}
                          </h5>
                          <div className="flex items-center gap-2">
                            <span
                              className={`text-2xl ${getRiskScoreColor(signal.risk_score)}`}
                            >
                              {signal.risk_score}
                            </span>
                            <span
                              className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(
                                signal.severity,
                              )}`}
                            >
                              {signal.severity}
                            </span>
                          </div>
                        </div>
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
                      <div className="bg-blue-50 rounded p-3 mb-2 border border-blue-200">
                        <p className="text-xs font-semibold text-gray-700 mb-1">
                          AI Risk Analysis:
                        </p>
                        <p className="text-xs text-gray-700">
                          {signal.risk_reasoning}
                        </p>
                      </div>
                      <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                        <span className="font-medium">Evidence: </span>
                        {signal.evidence}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
