interface Env {
  ASSETS: Fetcher;
}

function assetRequest(request: Request, pathname: string): Request {
  const url = new URL(request.url);
  url.pathname = pathname;
  url.search = "";
  return new Request(url, request);
}

const worker = {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === "/" || url.pathname === "/index.html") {
      const response = await env.ASSETS.fetch(assetRequest(request, "/dashboard.html"));
      if (!response.ok) return response;

      const headers = new Headers(response.headers);
      headers.set("content-type", "text/html; charset=utf-8");
      const html = (await response.text()).replaceAll(
        'content="./og-evergreen.png"',
        `content="${url.origin}/og-evergreen.png"`,
      );
      return new Response(html, { status: response.status, headers });
    }

    return env.ASSETS.fetch(request);
  },
};

export default worker;
