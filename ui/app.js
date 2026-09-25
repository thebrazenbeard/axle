const motion = document.querySelector("#motion");
const ai = document.querySelector("#ai");
const uplink = document.querySelector("#uplink");
const policyText = document.querySelector("#policyText");
const prompt = document.querySelector("#prompt");
const send = document.querySelector("#send");
const form = document.querySelector("#askForm");
const conversation = document.querySelector("#conversation");
const voiceButton = document.querySelector("#voiceButton");

let voiceState = "disabled";
let voiceReady = false;
let motionState = "unknown";

function pill(el, text, ok, warn = false) {
  el.textContent = text;
  el.classList.toggle("ok", ok);
  el.classList.toggle("warn", warn);
}

function message(kind, text) {
  const node = document.createElement("div");
  node.className = `message ${kind}`;
  node.textContent = text;
  conversation.appendChild(node);
  conversation.scrollTop = conversation.scrollHeight;
}

function updateVoiceButton() {
  const listening = voiceState === "listening";
  voiceButton.disabled = listening ? false : !(voiceReady && motionState === "parked");
  voiceButton.querySelector("strong").textContent = listening ? "Stop & respond" : "Push to talk";
  voiceButton.querySelector("small").textContent = listening
    ? "Recording locally through PipeWire."
    : voiceReady
      ? "Touch trigger is parked-only. Hardware/wake triggers may operate hands-free."
      : "Local voice models or runtime are not configured.";
}
async function refresh() {
  try {
    const response = await fetch("/api/status", { cache: "no-store" });
    const status = await response.json();

    motionState = status.motion;
    voiceState = status.voice.state;
    voiceReady = status.voice.enabled && status.voice.configured;

    pill(motion, `MOTION ${status.motion.toUpperCase()}`,
      status.motion === "parked", status.motion !== "parked");
    pill(ai, status.local_ai.healthy ? "AI LOCAL" : "AI OFFLINE",
      status.local_ai.healthy, !status.local_ai.healthy);
    pill(uplink, status.network.uplink ? "UPLINK READY" : "UPLINK NONE",
      status.network.uplink);

    policyText.textContent = status.policy.reason;
    prompt.disabled = !status.policy.manual_text_enabled;
    send.disabled = !status.policy.manual_text_enabled;
    prompt.placeholder = status.policy.manual_text_enabled
      ? "Ask AXLE…"
      : "Manual input locked while moving or motion is unknown";
    updateVoiceButton();
  } catch {
    pill(ai, "CORE OFFLINE", false, true);
    voiceButton.disabled = true;
  }
}

async function postJson(path, body) {
  const options = { method: "POST", headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  const payload = await response.json();
  return { response, payload };
}
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = prompt.value.trim();
  if (!text) return;

  message("user", text);
  prompt.value = "";
  send.disabled = true;

  try {
    const { response, payload } = await postJson("/api/assistant", { text });
    if (!response.ok) {
      message("error", payload.message || payload.error || "AXLE request failed.");
    } else {
      message("assistant", payload.answer);
    }
  } catch {
    message("error", "AXLE Core is unreachable.");
  } finally {
    await refresh();
  }
});

voiceButton.addEventListener("click", async () => {
  voiceButton.disabled = true;
  try {
    if (voiceState === "listening") {
      const { response, payload } = await postJson("/api/voice/stop");
      if (!response.ok) {
        message("error", payload.message || payload.detail || payload.error);
      } else if (payload.transcript) {
        message("user", `🎙 ${payload.transcript}`);
        if (payload.answer) message("assistant", payload.answer);
      } else {
        message("system", "No speech was detected.");
      }
    } else {
      const { response, payload } = await postJson(
        "/api/voice/start", { trigger: "touch" });
      if (!response.ok) {
        message("error", payload.message || payload.error);
      } else {
        message("system", "Listening locally…");
      }
    }
  } catch {
    message("error", "Voice runtime is unreachable.");
  } finally {
    await refresh();
  }
});

refresh();
setInterval(refresh, 2000);
