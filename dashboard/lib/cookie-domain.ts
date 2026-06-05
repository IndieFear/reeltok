export function parentCookieDomain(host: string | null | undefined): string | undefined {
  if (!host) return undefined;
  const hostname = host.split(":")[0];
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    return undefined;
  }
  const parts = hostname.split(".");
  if (parts.length < 2) return undefined;
  return `.${parts.slice(-2).join(".")}`;
}
