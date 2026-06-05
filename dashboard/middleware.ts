import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SESSION_COOKIE = "reeltok_session";

function authRequired(): boolean {
  if (process.env.NEXT_PUBLIC_AUTH_REQUIRED === "true") {
    return true;
  }
  if (process.env.NEXT_PUBLIC_AUTH_REQUIRED === "false") {
    return false;
  }
  // Prod : API_URL distante → auth obligatoire
  return (
    !API_URL.includes("localhost") &&
    !API_URL.includes("127.0.0.1") &&
    !API_URL.includes("placeholder.invalid")
  );
}

export async function middleware(request: NextRequest) {
  if (!authRequired()) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;

  if (
    pathname.startsWith("/login") ||
    pathname.startsWith("/api/auth") ||
    pathname.startsWith("/api/user-images")
  ) {
    return NextResponse.next();
  }

  const session = request.cookies.get(SESSION_COOKIE);
  if (!session?.value) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
