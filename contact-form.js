async function initContactForm() {
  const form = document.getElementById("contact-form");
  const panel = document.getElementById("contact-form-panel");
  const button = document.getElementById("contact-submit");
  const status = document.getElementById("contact-status");
  const fields = form.querySelector("fieldset");
  const config = window.contactFormConfig;
  const language = document.documentElement.lang;
  let messages, token = "", widgetId, loading = false, sending = false;

  const openLinkedForm = () => {
    if (location.hash === "#contact-form-panel") panel.open = true;
  };
  window.addEventListener("hashchange", openLinkedForm);
  document.querySelectorAll('a[href="#contact-form-panel"]').forEach((link) => {
    link.addEventListener("click", () => { panel.open = true; });
  });
  openLinkedForm();

  try {
    const response = await fetch(`locales/${language}.json`);
    if (!response.ok) return;
    messages = await response.json();
  } catch {
    // The HTML already shows a localized fallback; sending stays disabled.
    return;
  }

  const show = (key, state = "info") => {
    status.textContent = messages[key] || "";
    status.dataset.state = state;
  };
  const setSending = (value) => {
    sending = value;
    fields.disabled = value;
    button.disabled = value || !token;
    button.textContent = messages[value ? "sending" : "send"];
    form.setAttribute("aria-busy", String(value));
  };
  const invalidateToken = (key) => {
    token = "";
    button.disabled = true;
    if (!sending) show(key, "verification");
  };

  if (!config.turnstileSiteKey) {
    show("unavailable", "error");
    return;
  }

  for (const name of ["name", "message"]) {
    const input = form.elements.namedItem(name);
    input.addEventListener("input", () => {
      input.setCustomValidity(input.value && !input.value.trim() ? messages.whitespace : "");
    });
  }

  const prepareVerification = () => {
    if (sending || loading) return;
    if (widgetId !== undefined) {
      if (!token) {
        show("verification", "verification");
        window.turnstile.reset(widgetId);
      }
      return;
    }
    loading = true;
    show("verification", "verification");
    const render = () => {
      try {
        widgetId = window.turnstile.render("#contact-verification", {
          sitekey: config.turnstileSiteKey,
          action: "contact", language, theme: "light", size: "flexible",
          callback: (value) => {
            token = value;
            button.disabled = sending || !token;
            if (status.dataset.state === "verification") show("");
          },
          "expired-callback": () => invalidateToken("verification"),
          "error-callback": () => invalidateToken("verificationError"),
        });
      } catch {
        show("verificationError", "error");
      }
      loading = false;
    };
    if (window.turnstile) return render();
    window.onMedforgeTurnstileLoad = render;
    const script = document.createElement("script");
    script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=onMedforgeTurnstileLoad";
    script.async = true;
    script.onerror = () => {
      loading = false;
      script.remove();
      show("verificationError", "error");
    };
    document.head.append(script);
  };
  panel.addEventListener("toggle", () => {
    if (panel.open) prepareVerification();
  });
  if (panel.open) prepareVerification();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (sending || !form.reportValidity()) return;
    if (!token) return show("verification", "verification");
    const payload = Object.fromEntries(
      ["name", "email", "message"].map((name) => [name, form.elements.namedItem(name).value.trim()]),
    );
    if (Object.values(payload).some((value) => !value)) return show("invalid", "error");
    setSending(true);
    show("sending");
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(config.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...payload, turnstileToken: token, language }),
        signal: controller.signal,
      });
      if (!response.ok) {
        const errors = { 400: "invalid", 422: "invalid", 403: "verification", 429: "rateLimit" };
        return show(errors[response.status] || "error", "error");
      }
      if ((await response.json()).success !== true) return show("error", "error");
      form.reset();
      show("success", "success");
    } catch {
      show("uncertain", "error");
    } finally {
      clearTimeout(timeout);
      token = "";
      setSending(false);
      window.turnstile.reset(widgetId);
    }
  });
}

initContactForm();
