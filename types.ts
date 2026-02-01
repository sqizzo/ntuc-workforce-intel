export enum ScraperMode {
  GENERAL = "GENERAL",
  COMPANY = "COMPANY",
}

export type SourceType =
  | "news"
  | "social"
  | "forum"
  | "blog"
  | "gov"
  | "financial";

export interface WorkforceSignal {
  id: string;
  source_type: SourceType;
  source_name: string;
  source_url: string;
  ingestion_timestamp: string;
  extracted_text: string;
  // Specific to General Mode
  matched_keywords?: string[];
  inferred_workforce_theme?: string;
  // Specific to Company Mode
  company_name?: string;
  parent_company?: string;
  workforce_signal_type?: string;
  confidence_note?: "low" | "medium" | "high";
  // Additional data
  metadata?: {
    title?: string;
    author?: string;
    publish_date?: string;
    full_content?: string;
    [key: string]: any;
  };
  metrics?: {
    [key: string]: any;
  };
  // AI Relevance Filtering
  relevance?: {
    is_relevant: boolean;
    primary_label: string;
    secondary_label: string;
    rationale: string;
  };
}

export interface FinancialData {
  ticker: string;
  company_name: string;
  signals: WorkforceSignal[];
  metadata: {
    sector: string;
    industry: string;
    market_cap: number;
    scrape_timestamp: string;
  };
  financial_data?: {
    ticker: string;
    info: Record<string, any>;
    summary: {
      company_name: string;
      sector: string;
      industry: string;
      employees: number;
      market_cap: number;
      pe_ratio: number;
      revenue: number;
      profit_margin: number;
      current_price: number;
      currency: string;
      country: string;
      description: string;
    };
    history_data?: HistoricalPriceData[];
    history_summary?: {
      first_close: number;
      last_close: number;
      price_change: number;
      price_change_percent: number;
      highest_price: number;
      lowest_price: number;
      average_price: number;
      volatility: number;
      data_points: number;
    };
  };
  actual_workforce?: {
    employee_count: number;
    affected_workers?: number;
    source_confidence: string;
    data_source: string;
    context: string;
    is_subsidiary_data: boolean;
  };
  ai_analysis?: AIFinancialAnalysis;
  ai_detection?: {
    company_name: string;
    is_publicly_traded: boolean;
    parent_company: string | null;
    publicly_traded_entity: string;
    yahoo_symbol: string;
    exchange: string;
    confidence: string;
    reasoning: string;
  };
}

export interface HistoricalPriceData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface AIFinancialAnalysis {
  financial_health: {
    assessment: string;
    rating: string;
    key_metrics_summary: string;
  };
  workforce_implications: {
    employment_stability: string;
    hiring_outlook: string;
    risk_factors: string[];
    opportunities: string[];
  };
  stock_performance: {
    trend: string;
    trend_explanation: string;
    volatility_assessment: string;
    investor_confidence: string;
  };
  key_insights: string[];
  risk_rating: string;
  summary: string;
}

export interface ScrapingConfig {
  mode: ScraperMode;
  keywords: string[];
  companyName?: string;
}

export interface GroundingSource {
  title: string;
  uri: string;
}
