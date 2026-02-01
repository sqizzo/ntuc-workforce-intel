"use client";

import React from "react";

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 p-2 rounded-lg">
            <i className="fas fa-briefcase text-white text-xl"></i>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              NTUC Workforce Intelligence
            </h1>
          </div>
        </div>
        <nav className="hidden md:flex items-center space-x-6">
          <a
            href="#"
            className="text-sm font-semibold text-blue-600 border-b-2 border-blue-600 pb-1"
          >
            Scraper
          </a>
          <a
            href="#"
            className="text-sm font-semibold text-slate-600 hover:text-blue-600 transition-colors"
          >
            Risk Dashboard
          </a>
          <a
            href="#"
            className="text-sm font-semibold text-slate-600 hover:text-blue-600 transition-colors"
          >
            Methodology
          </a>
        </nav>
      </div>
    </header>
  );
};

export default Header;
