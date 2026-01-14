import { NextRequest, NextResponse } from "next/server";
import { readFile, writeFile, mkdir } from "fs/promises";
import { join } from "path";

interface WaitlistEntry {
  email: string;
  timestamp: string;
  source: string;
}

const DATA_DIR = join(process.cwd(), "data");
const WAITLIST_FILE = join(DATA_DIR, "waitlist.json");

async function ensureDataDir() {
  try {
    await mkdir(DATA_DIR, { recursive: true });
  } catch {
    // Directory may already exist
  }
}

async function getWaitlist(): Promise<WaitlistEntry[]> {
  try {
    const data = await readFile(WAITLIST_FILE, "utf-8");
    return JSON.parse(data);
  } catch {
    return [];
  }
}

async function saveWaitlist(entries: WaitlistEntry[]): Promise<void> {
  await ensureDataDir();
  await writeFile(WAITLIST_FILE, JSON.stringify(entries, null, 2));
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email } = body;

    // Validate email
    if (!email || typeof email !== "string") {
      return NextResponse.json(
        { success: false, message: "Email is required" },
        { status: 400 }
      );
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { success: false, message: "Invalid email format" },
        { status: 400 }
      );
    }

    // Get existing waitlist
    const waitlist = await getWaitlist();

    // Check for duplicate
    if (waitlist.some((entry) => entry.email.toLowerCase() === email.toLowerCase())) {
      return NextResponse.json(
        { success: true, message: "You're already on the list!" },
        { status: 200 }
      );
    }

    // Add new entry
    const newEntry: WaitlistEntry = {
      email: email.toLowerCase(),
      timestamp: new Date().toISOString(),
      source: "landing-page",
    };

    waitlist.push(newEntry);
    await saveWaitlist(waitlist);

    return NextResponse.json(
      {
        success: true,
        message: "Successfully joined the waitlist!",
        count: waitlist.length,
      },
      { status: 201 }
    );
  } catch (error) {
    console.error("Waitlist API error:", error);
    return NextResponse.json(
      { success: false, message: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    const waitlist = await getWaitlist();
    return NextResponse.json({
      success: true,
      count: waitlist.length,
    });
  } catch (error) {
    console.error("Waitlist API error:", error);
    return NextResponse.json(
      { success: false, message: "Internal server error" },
      { status: 500 }
    );
  }
}






