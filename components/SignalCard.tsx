"use client";

import React from "react";
import { WorkforceSignal } from "@/types";

interface SignalCardProps {
  signal: WorkforceSignal;
  onClick?: () => void;
}

const SignalCard: React.FC<SignalCardProps> = ({ signal, onClick }) => {
  const getConfidenceColor = (level?: string) => {
    switch (level?.toLowerCase()) {
      case "high":
        return "bg-green-100 text-green-700 border-green-200";
      case "medium":
        return "bg-yellow-100 text-yellow-700 border-yellow-200";
      case "low":
        return "bg-red-100 text-red-700 border-red-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  const getRelevanceBadgeColor = (label?: string) => {
    switch (label) {
      case "WORKFORCE_NEGATIVE":
        return "bg-red-100 text-red-700 border-red-200";
      case "WORKFORCE_POSITIVE":
        return "bg-green-100 text-green-700 border-green-200";
      case "WORKFORCE_NEUTRAL":
        return "bg-blue-100 text-blue-700 border-blue-200";
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  const getRelevanceBadgeText = (label?: string) => {
    switch (label) {
      case "WORKFORCE_NEGATIVE":
        return "Negative";
      case "WORKFORCE_POSITIVE":
        return "Positive";
      case "WORKFORCE_NEUTRAL":
        return "Neutral";
      default:
        return label || "N/A";
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case "news":
        return "fa-newspaper";
      case "gov":
        return "fa-building-columns";
      case "social":
        return "fa-share-nodes";
      case "forum":
        return "fa-comments";
      default:
        return "fa-link";
    }
  };

  return (
    <div
      onClick={onClick}
      className="bg-white border border-slate-200 rounded-xl overflow-hidden hover:shadow-lg transition-all duration-300 flex flex-col h-full group cursor-pointer"
    >
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <i
            className={`fas ${getSourceIcon(signal.source_type)} text-slate-400`}
          ></i>
          <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">
            {signal.source_type}
          </span>
          <span className="text-xs text-slate-400">•</span>
          <span className="text-xs font-medium text-slate-600 truncate max-w-[200px]">
            {signal.source_name}
          </span>
        </div>
        <div className="flex flex-col items-end gap-0.5">
          <span
            className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
              (signal as any).published_date ||
              signal.metadata?.publish_date ||
              signal.metadata?.published_date
                ? "text-blue-600 bg-blue-50"
                : "text-slate-500 bg-slate-50"
            }`}
          >
            <i className="fas fa-calendar-day mr-1"></i>
            {(signal as any).published_date ||
            signal.metadata?.publish_date ||
            signal.metadata?.published_date
              ? new Date(
                  (signal as any).published_date ||
                    signal.metadata?.publish_date ||
                    signal.metadata?.published_date,
                ).toLocaleDateString("en-SG", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })
              : "Unknown"}
          </span>
          <span className="text-[10px] font-mono text-slate-400">
            Scraped: {new Date(signal.ingestion_timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="p-5 flex-grow">
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-bold text-slate-900 line-clamp-2 leading-snug group-hover:text-blue-600 transition-colors text-base">
            {signal.metadata?.title ||
              signal.company_name ||
              signal.extracted_text.substring(0, 80) + "..."}
          </h3>
          <div className="flex flex-col gap-1 ml-2">
            {signal.confidence_note && (
              <span
                className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase ${getConfidenceColor(signal.confidence_note)}`}
              >
                {signal.confidence_note}
              </span>
            )}
            {signal.relevance?.secondary_label &&
              signal.relevance.secondary_label !== "NONE" && (
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full border font-bold uppercase whitespace-nowrap ${getRelevanceBadgeColor(signal.relevance.secondary_label)}`}
                >
                  {getRelevanceBadgeText(signal.relevance.secondary_label)}
                </span>
              )}
          </div>
        </div>

        {signal.company_name && (
          <p className="text-xs text-slate-500 mb-2 font-medium">
            <span className="text-slate-400">Company:</span>{" "}
            {signal.company_name}
          </p>
        )}

        {signal.parent_company && (
          <p className="text-xs text-slate-500 mb-2 font-medium">
            <span className="text-slate-400">Group:</span>{" "}
            {signal.parent_company}
          </p>
        )}

        <p className="text-sm text-slate-600 line-clamp-3 mb-4 italic leading-relaxed">
          &ldquo;
          {signal.extracted_text
            .replace(/<[^>]*>/g, "")
            .replace(/&nbsp;/g, " ")
            .trim()}
          &rdquo;
        </p>

        <div className="space-y-3">
          {signal.matched_keywords && signal.matched_keywords.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {signal.matched_keywords.map((kw, idx) => (
                <span
                  key={idx}
                  className="bg-slate-50 text-slate-500 text-[10px] px-2 py-0.5 rounded border border-slate-100 font-medium"
                >
                  {kw}
                </span>
              ))}
            </div>
          )}

          {signal.relevance?.rationale && (
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-2">
              <p className="text-xs text-blue-700 italic">
                <i className="fas fa-robot mr-1.5"></i>
                {signal.relevance.rationale}
              </p>
            </div>
          )}

          <div className="pt-3 border-t border-slate-50">
            <p className="text-xs font-bold text-slate-700">
              <i className="fas fa-radar-alt mr-1.5 text-blue-500"></i>
              {signal.inferred_workforce_theme ||
                signal.workforce_signal_type ||
                "Potential Risk Signal"}
            </p>
          </div>
        </div>
      </div>

      <div className="p-4 bg-slate-50/50 mt-auto flex items-center justify-between">
        <span className="text-xs font-medium text-blue-600 hover:text-blue-800 flex items-center">
          Click for details{" "}
          <i className="fas fa-chevron-right ml-1.5 text-[10px]"></i>
        </span>
        <a
          href={signal.source_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center group-hover:underline"
        >
          Verify Source{" "}
          <i className="fas fa-external-link-alt ml-1.5 text-[10px]"></i>
        </a>
      </div>
    </div>
  );
};

export default SignalCard;
