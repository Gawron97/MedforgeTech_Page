// Public frontend settings. Never put secret keys or email credentials here.
window.contactFormConfig = {
  endpoint: "/api/contact",
  // Add the public site key from your Cloudflare Turnstile widget.
  // Sending stays disabled until the widget is configured and verified.
  turnstileSiteKey: "",
};
