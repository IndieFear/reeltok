import { NextRequest, NextResponse } from "next/server";
import { parentCookieDomain } from "@/lib/cookie-domain";

const SESSION_COOKIE = "reeltok_session";

function backendUrl(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

export async function POST(request: NextRequest) {
  try {
    await fetch(`${backendUrl()}/api/auth/logout`, {
      method: "POST",
      headers: { cookie: request.headers.get("cookie") ?? "" },
    });
  } catch {
    // ignore
  }

  const res = NextResponse.json({ ok: true });
  const domain =
    process.env.COOKIE_DOMAIN?.trim() ||
    parentCookieDomain(request.headers.get("host"));

  res.cookies.set(SESSION_COOKIE, "", {
    httpOnly: true,
    secure: request.nextUrl.protocol === "https:",
    sameSite: "lax",
    path: "/",
    maxAge: 0,
    ...(domain ? { domain } : {}),
  });

  return res;
}
