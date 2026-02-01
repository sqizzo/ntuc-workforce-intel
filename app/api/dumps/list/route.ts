import { NextResponse } from "next/server";

const PYTHON_BACKEND_URL =
  process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${PYTHON_BACKEND_URL}/api/dumps/list`);

    if (!response.ok) {
      throw new Error("Failed to fetch dump list");
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error fetching dump list:", error);
    return NextResponse.json(
      { error: "Failed to fetch dump list" },
      { status: 500 },
    );
  }
}
