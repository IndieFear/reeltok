import { NextRequest, NextResponse } from "next/server";

function backendUrl(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const res = await fetch(`${backendUrl()}/api/user-images/${id}`, {
    headers: { cookie: request.headers.get("cookie") ?? "" },
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    return NextResponse.json(data, { status: res.status });
  }
  const blob = await res.blob();
  const contentType = res.headers.get("content-type") ?? "image/jpeg";
  return new NextResponse(blob, {
    status: 200,
    headers: { "Content-Type": contentType, "Cache-Control": "private, max-age=3600" },
  });
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const res = await fetch(`${backendUrl()}/api/user-images/${id}`, {
    method: "DELETE",
    headers: { cookie: request.headers.get("cookie") ?? "" },
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
