const form = document.getElementById("contact-form");
const panel = document.getElementById("contact-form-panel");
const button = document.getElementById("contact-submit");
const status = document.getElementById("contact-status");
const fields = form.querySelector("fieldset");
const config = window.contactFormConfig;
const language = document.documentElement.lang;

let messages = {};
let token = "";
let widgetId;
let loading = false;
let sending = false;

async function initContactForm() {
  try {
    const response = await fetch("locales/" + language + ".json");
    if (!response.ok) return;
    messages = await response.json();
  } catch {
    return;
  }

  if (!config.turnstileSiteKey) {
    showStatus("INTERNAL_ERROR", "error");
    return;
  }

  form.addEventListener("input", validateWhitespace);
  panel.addEventListener("toggle", loadTurnstile);
  form.addEventListener("submit", submitContactForm);
  if (panel.open) loadTurnstile();
}

function validateWhitespace(event) {
  const input = event.target;
  if (input.name !== "name" && input.name !== "message") return;
  input.setCustomValidity(input.value && !input.value.trim() ? messages.whitespace : "");
}

function loadTurnstile() {
  if (!panel.open || sending || loading) return;
  if (widgetId !== undefined) {
    if (!token) {
      showStatus("verification", "verification");
      window.turnstile.reset(widgetId);
    }
    return;
  }

  loading = true;
  showStatus("verification", "verification");
  if (window.turnstile) return renderVerification();

  window.onMedforgeTurnstileLoad = renderVerification;
  const script = document.createElement("script");
  script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=onMedforgeTurnstileLoad";
  script.async = true;
  script.onerror = verificationScriptFailed;
  document.head.append(script);
}

function renderVerification() {
  try {
    widgetId = window.turnstile.render("#contact-verification", {
      sitekey: config.turnstileSiteKey,
      action: "contact", language, theme: "light", size: "flexible",
      callback: verificationCompleted,
      "expired-callback": verificationExpired,
      "error-callback": verificationFailed,
    });
  } catch {
    showStatus("CAPTCHA_VERIFICATION_UNAVAILABLE", "error");
  }
  loading = false;
}

function verificationCompleted(value) {
  token = value;
  button.disabled = sending || !token;
  if (status.dataset.state === "verification") showStatus("");
}

function verificationExpired() {
  token = "";
  button.disabled = true;
  if (!sending) showStatus("verification", "verification");
}

function verificationFailed() {
  token = "";
  button.disabled = true;
  if (!sending) showStatus("CAPTCHA_VERIFICATION_FAILED", "verification");
}

function verificationScriptFailed(event) {
  loading = false;
  event.currentTarget.remove();
  showStatus("CAPTCHA_VERIFICATION_UNAVAILABLE", "error");
}

async function submitContactForm(event) {
  event.preventDefault();
  if (sending || !form.reportValidity()) return;
  if (!token) return showStatus("verification", "verification");

  const payload = {};
  for (const name of ["name", "email", "message"]) {
    payload[name] = form.elements.namedItem(name).value.trim();
    if (!payload[name]) return showStatus("whitespace", "error");
  }

  setSending(true);
  showStatus("sending");
  const controller = new AbortController();
  const timeout = setTimeout(controller.abort.bind(controller), 15000);
  try {
    const response = await fetch(config.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, turnstileToken: token, language }),
      signal: controller.signal,
    });
    if (!response.ok) {
      const body = await response.json().catch(() => null);
      const code = body?.code;
      const messageKey =
        typeof code === "string" &&
        Object.hasOwn(messages, code)
          ? code
          : "INTERNAL_ERROR";
      return showStatus(messageKey, "error");
    }
    if ((await response.json()).success !== true) return showStatus("INTERNAL_ERROR", "error");
    form.reset();
    showStatus("success", "success");
  } catch {
    showStatus("uncertain", "error");
  } finally {
    clearTimeout(timeout);
    token = "";
    setSending(false);
    window.turnstile.reset(widgetId);
  }
}

function showStatus(key, state = "info") {
  status.textContent = messages[key] || "";
  status.dataset.state = state;
}

function setSending(value) {
  sending = value;
  fields.disabled = value;
  button.disabled = value || !token;
  button.textContent = messages[value ? "sending" : "send"];
  form.setAttribute("aria-busy", String(value));
}

initContactForm();
