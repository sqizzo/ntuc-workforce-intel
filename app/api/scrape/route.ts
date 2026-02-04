import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export const maxDuration = 1800;

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { mode, keywords, companyName, before_date, enable_smart_filtering } =
      body;

    console.log("Forwarding scrape request to Python backend:", {
      mode,
      keywords,
      companyName,
      before_date,
      enable_smart_filtering,
    });

    // Forward request to Python FastAPI backend using axios with proper timeout
    const response = await axios.post(
      `${PYTHON_BACKEND_URL}/api/scrape`,
      {
        mode,
        keywords,
        companyName,
        max_articles: 10,
        before_date,
        enable_smart_filtering,
      },
      {
        timeout: 1800000, // 30 minutes
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    const results = response.data;

    // Handle both array (signals only) and object (with financial_data) responses
    const signalCount = Array.isArray(results)
      ? results.length
      : results.signals?.length || 0;

    console.log(
      `Successfully received ${signalCount} signals from Python backend`,
    );

    return NextResponse.json(results);
  } catch (error) {
    console.error("Scraping Error:", error);

    // Handle axios errors
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message;
      return NextResponse.json(
        { error: message },
        { status: error.response?.status || 500 },
      );
    }

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to scrape data",
      },
      { status: 500 },
    );
  }
}
