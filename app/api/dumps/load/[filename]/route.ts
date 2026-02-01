import { NextRequest, NextResponse } from "next/server";

const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> },
) {
  try {
    const { filename } = await params;
    const response = await fetch(
      `${PYTHON_BACKEND_URL}/api/dumps/load/${encodeURIComponent(filename)}`,
    );

    if (!response.ok) {
      throw new Error("Failed to load dump file");
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error loading dump:", error);
    return NextResponse.json(
      { error: "Failed to load dump file" },
      { status: 500 },
    );
  }
}
