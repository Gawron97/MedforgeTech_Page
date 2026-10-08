export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/debug") {
      return Response.json({
        hasTurnstileSecret: Boolean(env.TURNSTILE_SECRET)
      });
    }

    if (url.pathname === "/api/contact") {
      return Response.json({
        success: false,
        error: "Contact API not implemented yet"
      }, {
        status: 501
      });
    }

    return env.ASSETS.fetch(request);
  }
};