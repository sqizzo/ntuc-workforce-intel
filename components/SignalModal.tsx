"use client";

import React from "react";
import { WorkforceSignal } from "../types";

interface SignalModalProps {
  signal: WorkforceSignal | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function SignalModal({
  signal,
  isOpen,
  onClose,
}: SignalModalProps) {
  if (!isOpen || !signal) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {signal.metadata?.title || "Workforce Signal Details"}
            </h2>
            <div className="flex flex-wrap gap-2">
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                {signal.source_type}
              </span>
              {signal.inferred_workforce_theme && (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                  {signal.inferred_workforce_theme}
                </span>
              )}
              {signal.workforce_signal_type && (
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                  {signal.workforce_signal_type}
                </span>
              )}
              {signal.relevance?.primary_label === "WORKFORCE_RELEVANT" && (
                <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full">
                  <i className="fas fa-check-circle mr-1"></i>
                  AI Verified
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {/* Source Information */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">
              Source Information
            </h3>
            <div className="space-y-1 text-sm">
              <div>
                <span className="font-medium text-gray-700">Source:</span>{" "}
                <span className="text-gray-600">{signal.source_name}</span>
              </div>
              {signal.metadata?.author && (
                <div>
                  <span className="font-medium text-gray-700">Author:</span>{" "}
                  <span className="text-gray-600">
                    {signal.metadata.author}
                  </span>
                </div>
              )}
              <div>
                <span className="font-medium text-gray-700">Published:</span>{" "}
                <span
                  className={
                    signal.metadata?.publish_date
                      ? "text-blue-600 font-semibold"
                      : "text-gray-400 italic"
                  }
                >
                  <i className="fas fa-calendar-day mr-1"></i>
                  {signal.metadata?.publish_date
                    ? new Date(signal.metadata.publish_date).toLocaleDateString(
                        "en-US",
                        {
                          year: "numeric",
                          month: "long",
                          day: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        },
                      )
                    : "Unknown"}
                </span>
              </div>
              <div>
                <span className="font-medium text-gray-700">URL:</span>{" "}
                <a
                  href={signal.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline break-all"
                >
                  {signal.source_url}
                </a>
              </div>
              <div>
                <span className="font-medium text-gray-700">Ingested:</span>{" "}
                <span className="text-gray-600">
                  {new Date(signal.ingestion_timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </div>

          {/* AI Relevance Analysis */}
          {signal.relevance && signal.relevance.rationale && (
            <div className="mb-6 p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg border border-indigo-200">
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                <i className="fas fa-robot mr-2 text-indigo-600"></i>
                AI Relevance Analysis
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-start">
                  <span className="font-medium text-gray-700 min-w-[100px]">
                    Assessment:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        signal.relevance.primary_label === "WORKFORCE_RELEVANT"
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {signal.relevance.primary_label === "WORKFORCE_RELEVANT"
                        ? "✓ Workforce Relevant"
                        : "Not Workforce Relevant"}
                    </span>
                    {signal.relevance.secondary_label !== "NONE" && (
                      <span
                        className={`px-2 py-1 text-xs rounded-full ${
                          signal.relevance.secondary_label ===
                          "WORKFORCE_NEGATIVE"
                            ? "bg-red-100 text-red-800"
                            : signal.relevance.secondary_label ===
                                "WORKFORCE_POSITIVE"
                              ? "bg-green-100 text-green-800"
                              : "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {signal.relevance.secondary_label.replace(
                          "WORKFORCE_",
                          "",
                        )}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="font-medium text-gray-700 min-w-[100px]">
                    Rationale:
                  </span>
                  <span className="text-gray-600 flex-1">
                    {signal.relevance.rationale}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Company Information */}
          {(signal.company_name || signal.parent_company) && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">
                Company Information
              </h3>
              <div className="space-y-1 text-sm">
                {signal.company_name && (
                  <div>
                    <span className="font-medium text-gray-700">Company:</span>{" "}
                    <span className="text-gray-600">{signal.company_name}</span>
                  </div>
                )}
                {signal.parent_company && (
                  <div>
                    <span className="font-medium text-gray-700">
                      Parent Company:
                    </span>{" "}
                    <span className="text-gray-600">
                      {signal.parent_company}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Keywords */}
          {signal.matched_keywords && signal.matched_keywords.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Matched Keywords
              </h3>
              <div className="flex flex-wrap gap-2">
                {signal.matched_keywords.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">Content</h3>

            {/* Social/Reddit structured display */}
            {signal.source_type === "social" && (signal as any).post_title ? (
              <div className="space-y-4">
                {/* Original Post */}
                <div className="border-l-4 border-blue-500 bg-blue-50 rounded-r-lg p-5 shadow-sm">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <i className="fas fa-user-circle text-blue-600 text-2xl"></i>
                      </div>
                      <div>
                        <span className="font-semibold text-gray-900 block">
                          {signal.metadata?.author || "Anonymous"}
                        </span>
                        <span className="text-xs text-gray-500">
                          Original Poster
                        </span>
                      </div>
                    </div>
                    {signal.metadata?.comment_count && (
                      <span className="text-sm text-gray-600 bg-white px-3 py-1 rounded-full border border-gray-200">
                        <i className="fas fa-comments mr-1 text-blue-600"></i>
                        {signal.metadata.comment_count} comments
                      </span>
                    )}
                  </div>

                  <h4 className="text-lg font-bold text-gray-900 mb-3">
                    {(signal as any).post_title}
                  </h4>

                  {(signal as any).post_text && (
                    <p className="text-gray-800 leading-relaxed whitespace-pre-wrap bg-white p-3 rounded border border-blue-100">
                      {(signal as any).post_text}
                    </p>
                  )}
                </div>

                {/* Comments Section */}
                {(signal as any).comments &&
                  (signal as any).comments.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-gray-900 flex items-center">
                          <i className="fas fa-comment-dots mr-2 text-blue-600"></i>
                          Top Comments ({(signal as any).comments.length})
                        </h4>
                        <span className="text-xs text-gray-500">
                          Sorted by score
                        </span>
                      </div>

                      <div className="space-y-2">
                        {(signal as any).comments.map(
                          (comment: any, idx: number) => (
                            <div
                              key={idx}
                              className="border-l-3 border-gray-300 bg-gray-50 rounded-r-lg p-4 hover:bg-gray-100 transition-all duration-150 hover:shadow-sm"
                            >
                              <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-2">
                                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                                    <i className="fas fa-user text-gray-600 text-sm"></i>
                                  </div>
                                  <span className="font-medium text-gray-800">
                                    {comment.author || "Anonymous"}
                                  </span>
                                </div>
                                {comment.score !== undefined && (
                                  <div className="bg-white px-3 py-1 rounded border border-gray-200">
                                    <span className="text-sm font-semibold text-gray-700">
                                      {comment.score}
                                    </span>
                                  </div>
                                )}
                              </div>
                              <p className="text-sm text-gray-700 leading-relaxed pl-10">
                                {comment.text || comment.body}
                              </p>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  )}
              </div>
            ) : (
              /* Regular content display for non-social sources */
              <div className="prose max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {signal.metadata?.full_content || signal.extracted_text}
              </div>
            )}
          </div>

          {/* Metrics */}
          {signal.metrics && Object.keys(signal.metrics).length > 0 && (
            <div className="mb-6 p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">
                Metrics & Data
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                {Object.entries(signal.metrics).map(([key, value]) => (
                  <div key={key}>
                    <span className="font-medium text-gray-700">{key}:</span>{" "}
                    <span className="text-gray-600">
                      {typeof value === "object"
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Confidence Note */}
          {signal.confidence_note && (
            <div className="mb-4 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <h3 className="font-semibold text-gray-900 mb-2">
                ⚠️ Confidence Note
              </h3>
              <p className="text-sm text-gray-700">{signal.confidence_note}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            onClick={() => window.open(signal.source_url, "_blank")}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            View Original
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
