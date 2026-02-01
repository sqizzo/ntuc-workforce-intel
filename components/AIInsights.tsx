"use client";

import React from "react";
import { AIFinancialAnalysis } from "@/types";

interface AIInsightsProps {
  analysis: AIFinancialAnalysis;
  companyName: string;
}

const AIInsights: React.FC<AIInsightsProps> = ({ analysis, companyName }) => {
  const getRiskColor = (rating: string) => {
    if (rating.includes("LOW"))
      return "text-green-600 bg-green-50 border-green-200";
    if (rating.includes("MEDIUM"))
      return "text-yellow-600 bg-yellow-50 border-yellow-200";
    if (rating.includes("HIGH")) return "text-red-600 bg-red-50 border-red-200";
    return "text-slate-600 bg-slate-50 border-slate-200";
  };

  const getRatingColor = (rating: string) => {
    if (rating === "Excellent") return "text-green-600";
    if (rating === "Good") return "text-blue-600";
    if (rating === "Fair") return "text-yellow-600";
    if (rating === "Poor") return "text-red-600";
    return "text-slate-600";
  };

  const getTrendIcon = (trend: string) => {
    if (trend === "Bullish") return "fa-arrow-trend-up text-green-600";
    if (trend === "Bearish") return "fa-arrow-trend-down text-red-600";
    return "fa-minus text-slate-600";
  };

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-900 mb-1 flex items-center">
            <i className="fas fa-brain text-blue-600 mr-2"></i>
            AI Financial Analyst Insights
          </h3>
          <p className="text-sm text-slate-500">{companyName}</p>
        </div>
        <div
          className={`px-3 py-1 rounded-lg border text-xs font-bold ${getRiskColor(analysis.risk_rating)}`}
        >
          {analysis.risk_rating}
        </div>
      </div>

      {/* Executive Summary */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-xl">
        <div className="text-sm text-slate-700 leading-relaxed">
          <i className="fas fa-quote-left text-blue-400 text-xs mr-2"></i>
          {analysis.summary}
          <i className="fas fa-quote-right text-blue-400 text-xs ml-2"></i>
        </div>
      </div>

      {/* Financial Health */}
      <div className="mb-6">
        <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center">
          <i className="fas fa-heart-pulse text-red-500 mr-2"></i>
          Financial Health
        </h4>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500">Rating:</span>
            <span
              className={`text-sm font-bold ${getRatingColor(analysis.financial_health.rating)}`}
            >
              {analysis.financial_health.rating}
            </span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed pl-4 border-l-2 border-slate-200">
            {analysis.financial_health.assessment}
          </p>
          <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg">
            <strong>Key Metrics:</strong>{" "}
            {analysis.financial_health.key_metrics_summary}
          </div>
        </div>
      </div>

      {/* Stock Performance */}
      <div className="mb-6">
        <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center">
          <i
            className={`fas ${getTrendIcon(analysis.stock_performance.trend)} mr-2`}
          ></i>
          Stock Performance - {analysis.stock_performance.trend}
        </h4>
        <div className="space-y-2">
          <p className="text-sm text-slate-700 leading-relaxed pl-4 border-l-2 border-slate-200">
            {analysis.stock_performance.trend_explanation}
          </p>
          <div className="grid grid-cols-2 gap-3 mt-3">
            <div className="text-xs bg-slate-50 p-3 rounded-lg">
              <div className="text-slate-500 mb-1">Volatility</div>
              <div className="font-bold text-slate-900">
                {analysis.stock_performance.volatility_assessment}
              </div>
            </div>
            <div className="text-xs bg-slate-50 p-3 rounded-lg">
              <div className="text-slate-500 mb-1">Investor Confidence</div>
              <div className="font-bold text-slate-900">
                {analysis.stock_performance.investor_confidence}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Workforce Implications */}
      <div className="mb-6 p-4 bg-purple-50 border border-purple-100 rounded-xl">
        <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center">
          <i className="fas fa-users text-purple-600 mr-2"></i>
          Workforce Implications
        </h4>
        <div className="space-y-3">
          <div>
            <div className="text-xs text-purple-700 font-bold mb-1">
              Employment Stability:
            </div>
            <p className="text-sm text-slate-700">
              {analysis.workforce_implications.employment_stability}
            </p>
          </div>
          <div>
            <div className="text-xs text-purple-700 font-bold mb-1">
              Hiring Outlook:
            </div>
            <p className="text-sm text-slate-700">
              {analysis.workforce_implications.hiring_outlook}
            </p>
          </div>
          {analysis.workforce_implications.risk_factors.length > 0 && (
            <div>
              <div className="text-xs text-red-700 font-bold mb-2">
                Risk Factors:
              </div>
              <ul className="space-y-1">
                {analysis.workforce_implications.risk_factors.map(
                  (risk, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-slate-700 flex items-start"
                    >
                      <i className="fas fa-exclamation-triangle text-red-500 text-[10px] mr-2 mt-0.5"></i>
                      {risk}
                    </li>
                  ),
                )}
              </ul>
            </div>
          )}
          {analysis.workforce_implications.opportunities.length > 0 && (
            <div>
              <div className="text-xs text-green-700 font-bold mb-2">
                Opportunities:
              </div>
              <ul className="space-y-1">
                {analysis.workforce_implications.opportunities.map(
                  (opp, idx) => (
                    <li
                      key={idx}
                      className="text-xs text-slate-700 flex items-start"
                    >
                      <i className="fas fa-lightbulb text-green-500 text-[10px] mr-2 mt-0.5"></i>
                      {opp}
                    </li>
                  ),
                )}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Key Insights */}
      <div>
        <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center">
          <i className="fas fa-lightbulb text-yellow-500 mr-2"></i>
          Key Insights & Recommendations
        </h4>
        <ul className="space-y-2">
          {analysis.key_insights.map((insight, idx) => (
            <li
              key={idx}
              className="text-sm text-slate-700 flex items-start bg-slate-50 p-3 rounded-lg"
            >
              <span className="text-blue-600 font-bold mr-2">{idx + 1}.</span>
              {insight}
            </li>
          ))}
        </ul>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-slate-100">
        <p className="text-[10px] text-slate-400 text-center uppercase tracking-widest">
          <i className="fas fa-robot mr-1"></i>
          AI-Powered Analysis • For Reference Only
        </p>
      </div>
    </div>
  );
};

export default AIInsights;
