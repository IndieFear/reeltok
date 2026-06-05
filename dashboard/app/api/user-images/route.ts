import { NextRequest, NextResponse } from "next/server";

function backendUrl(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

function forwardCookie(request: NextRequest): string {
  return request.headers.get("cookie") ?? "";
}

export async function GET(request: NextRequest) {
  const res = await fetch(`${backendUrl()}/api/user-images`, {
    headers: { cookie: forwardCookie(request) },
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const file = form.get("file");
  if (!file || typeof file === "string") {
    return NextResponse.json({ detail: "Fichier requis" }, { status: 400 });
  }

  const body = new FormData();
  body.append("file", file);

  const res = await fetch(`${backendUrl()}/api/user-images`, {
    method: "POST",
    headers: { cookie: forwardCookie(request) },
    body,
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
