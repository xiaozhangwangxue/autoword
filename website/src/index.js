const downloadableFiles = new Set([
  "AutoWord-android.apk",
  "AutoWord-macos.dmg",
  "AutoWord-windows.zip",
  "AutoWord-linux.tar.gz",
]);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname.startsWith("/downloads/")) {
      if (request.method !== "GET" && request.method !== "HEAD") {
        return new Response("Method Not Allowed", { status: 405, headers: { Allow: "GET, HEAD" } });
      }

      const key = decodeURIComponent(url.pathname.slice("/downloads/".length));
      if (!downloadableFiles.has(key)) return new Response("Not Found", { status: 404 });

      const object = await env.DOWNLOADS.get(key);
      if (!object) return new Response("Download is being prepared", { status: 503 });

      const headers = new Headers();
      object.writeHttpMetadata(headers);
      headers.set("etag", object.httpEtag);
      headers.set("cache-control", "public, max-age=3600");
      headers.set("content-disposition", `attachment; filename="${key}"`);
      headers.set("x-content-type-options", "nosniff");

      return new Response(request.method === "HEAD" ? null : object.body, { headers });
    }

    const response = await env.ASSETS.fetch(request);
    const headers = new Headers(response.headers);
    headers.set("x-content-type-options", "nosniff");
    headers.set("referrer-policy", "strict-origin-when-cross-origin");
    headers.set("permissions-policy", "camera=(), microphone=(), geolocation=()");
    return new Response(response.body, { status: response.status, statusText: response.statusText, headers });
  },
};
