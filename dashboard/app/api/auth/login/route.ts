import { NextRequest, NextResponse } from "next/server";
import { parentCookieDomain } from "@/lib/cookie-domain";

const SESSION_COOKIE = "reeltok_session";
const SESSION_MAX_AGE = 7 * 24 * 3600;

function backendUrl(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => null);
  const password = body?.password;
  if (!password || typeof password !== "string") {
    return NextResponse.json({ detail: "Mot de passe requis" }, { status: 400 });
  }

  const origin = request.headers.get("origin") ?? request.nextUrl.origin;

  const backendRes = await fetch(`${backendUrl()}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Origin: origin,
    },
    body: JSON.stringify({ password }),
  });

  const data = await backendRes.json().catch(() => ({}));

  if (!backendRes.ok) {
    return NextResponse.json(
      { detail: data.detail || "Connexion impossible" },
      { status: backendRes.status },
    );
  }

  const token = data.token as string | undefined;
  if (!token) {
    return NextResponse.json(
      { detail: "Session non créée — vérifie APP_PASSWORD sur le backend." },
      { status: 503 },
    );
  }

  const res = NextResponse.json({ ok: true });
  const domain =
    process.env.COOKIE_DOMAIN?.trim() ||
    parentCookieDomain(request.headers.get("host"));
  const secure = request.nextUrl.protocol === "https:";

  res.cookies.set(SESSION_COOKIE, token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE,
    ...(domain ? { domain } : {}),
  });

  return res;
}
