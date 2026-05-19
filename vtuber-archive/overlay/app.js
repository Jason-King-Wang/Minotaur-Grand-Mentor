(function () {
  "use strict";

  const FALLBACK_MANIFEST = {
    project: "Minotaur Grand Mentor",
    version: "0.1.0",
    mode: "pngtuber-mvp",
    required_assets: [
      { id: "idle_closed", path: "assets/avatar/pngtuber/idle_closed.png", required: true },
      { id: "talk_open", path: "assets/avatar/pngtuber/talk_open.png", required: true },
      { id: "blink_closed", path: "assets/avatar/pngtuber/blink_closed.png", required: true },
      { id: "happy", path: "assets/avatar/pngtuber/happy.png", required: true }
    ],
    optional_assets: [
      { id: "angry", path: "assets/avatar/pngtuber/angry.png", required: false },
      { id: "thinking", path: "assets/avatar/pngtuber/thinking.png", required: false },
      { id: "gesture_point", path: "assets/avatar/pngtuber/gesture_point.png", required: false },
      { id: "shock", path: "assets/avatar/pngtuber/shock.png", required: false }
    ]
  };

  const params = new URLSearchParams(window.location.search);
  const state = {
    threshold: readNumberParam("threshold", 0.05),
    scale: readNumberParam("scale", 1),
    x: readSignedNumberParam("x", 0),
    y: readSignedNumberParam("y", 0),
    debug: params.get("debug") === "1",
    micEnabled: params.get("mic") !== "0",
    micStatus: "not requested",
    currentExpression: "idle_closed",
    manualExpression: "idle_closed",
    volume: 0,
    loaded: new Map(),
    missing: new Set(),
    manifest: FALLBACK_MANIFEST,
    isBlinking: false
  };

  const avatarImage = document.getElementById("avatarImage");
  const placeholder = document.getElementById("placeholder");
  const avatarWrap = document.getElementById("avatarWrap");
  const debugPanel = document.getElementById("debugPanel");
  const debugMic = document.getElementById("debugMic");
  const debugExpression = document.getElementById("debugExpression");
  const debugVolume = document.getElementById("debugVolume");
  const debugThreshold = document.getElementById("debugThreshold");
  const debugLoaded = document.getElementById("debugLoaded");
  const debugMissing = document.getElementById("debugMissing");
  const debugBlink = document.getElementById("debugBlink");
  const debugMode = document.getElementById("debugMode");

  avatarWrap.style.setProperty("--avatar-scale", String(state.scale));
  avatarWrap.style.setProperty("--avatar-x", `${state.x}px`);
  avatarWrap.style.setProperty("--avatar-y", `${state.y}px`);
  debugPanel.hidden = !state.debug;

  function readNumberParam(name, fallback) {
    const raw = params.get(name);
    if (raw === null) {
      return fallback;
    }
    const value = Number(raw);
    return Number.isFinite(value) && value > 0 ? value : fallback;
  }

  function readSignedNumberParam(name, fallback) {
    const raw = params.get(name);
    if (raw === null) {
      return fallback;
    }
    const value = Number(raw);
    return Number.isFinite(value) ? value : fallback;
  }

  function projectUrl(path) {
    return new URL(`../${path}`, window.location.href).href;
  }

  async function loadJson(path, fallback) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.warn(`Using fallback for ${path}`, error);
      return fallback;
    }
  }

  function allAssets() {
    return [
      ...(state.manifest.required_assets || []),
      ...(state.manifest.optional_assets || [])
    ];
  }

  function findAsset(id) {
    return allAssets().find((asset) => asset.id === id);
  }

  function preloadAsset(asset) {
    return new Promise((resolve) => {
      const image = new Image();
      const src = projectUrl(asset.path);
      image.onload = () => {
        state.loaded.set(asset.id, src);
        resolve();
      };
      image.onerror = () => {
        state.missing.add(asset.id);
        resolve();
      };
      image.src = src;
    });
  }

  async function preloadAssets() {
    await Promise.all(allAssets().map(preloadAsset));
  }

  function showExpression(id) {
    state.currentExpression = id;
    const src = state.loaded.get(id);
    if (src) {
      avatarImage.src = src;
      avatarImage.hidden = false;
      placeholder.hidden = true;
    } else {
      avatarImage.hidden = true;
      placeholder.hidden = false;
    }
    updateDebug();
  }

  function chooseExpression() {
    if (state.isBlinking && state.loaded.has("blink_closed")) {
      return "blink_closed";
    }
    if (state.micEnabled && state.volume >= state.threshold && state.loaded.has("talk_open")) {
      return "talk_open";
    }
    return state.manualExpression;
  }

  function renderLoop() {
    showExpression(chooseExpression());
    requestAnimationFrame(renderLoop);
  }

  function scheduleBlink() {
    const delay = 3000 + Math.random() * 4000;
    window.setTimeout(() => {
      state.isBlinking = true;
      window.setTimeout(() => {
        state.isBlinking = false;
        scheduleBlink();
      }, 140);
    }, delay);
  }

  async function setupMic() {
    if (!state.micEnabled) {
      state.micStatus = "disabled";
      updateDebug();
      return;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      state.micStatus = "unavailable";
      updateDebug();
      return;
    }

    try {
      state.micStatus = "requesting";
      updateDebug();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      const samples = new Uint8Array(analyser.fftSize);
      source.connect(analyser);
      state.micStatus = "active";

      function measure() {
        analyser.getByteTimeDomainData(samples);
        let sum = 0;
        for (const sample of samples) {
          const value = (sample - 128) / 128;
          sum += value * value;
        }
        state.volume = Math.sqrt(sum / samples.length);
        updateDebug();
        requestAnimationFrame(measure);
      }

      measure();
    } catch (error) {
      console.warn("Microphone unavailable", error);
      state.micStatus = "blocked or unavailable";
      updateDebug();
    }
  }

  function updateDebug() {
    debugMic.textContent = state.micStatus;
    debugExpression.textContent = state.currentExpression;
    debugVolume.textContent = state.volume.toFixed(3);
    debugThreshold.textContent = state.threshold.toFixed(3);
    debugLoaded.textContent = Array.from(state.loaded.keys()).join(", ") || "none";
    debugMissing.textContent = Array.from(state.missing).join(", ") || "none";
    debugBlink.textContent = String(state.isBlinking);
    debugMode.textContent = state.micEnabled ? "mic-auto" : "manual";
  }

  function setManualExpression(id) {
    const asset = findAsset(id);
    state.manualExpression = asset ? id : "idle_closed";
    updateDebug();
  }

  function setupHotkeys() {
    window.addEventListener("keydown", (event) => {
      const key = event.key.toLowerCase();
      if (key === "1") setManualExpression("idle_closed");
      if (key === "2") setManualExpression("happy");
      if (key === "3") setManualExpression("angry");
      if (key === "4") setManualExpression("thinking");
      if (key === "5") setManualExpression("gesture_point");
      if (key === "6") setManualExpression("shock");
      if (key === "0") setManualExpression("idle_closed");
      if (key === "d") {
        state.debug = !state.debug;
        debugPanel.hidden = !state.debug;
      }
      if (key === "m") {
        state.micEnabled = !state.micEnabled;
        if (state.micEnabled && state.micStatus === "disabled") {
          setupMic();
        } else if (!state.micEnabled) {
          state.volume = 0;
          state.micStatus = "disabled";
        }
        updateDebug();
      }
    });
  }

  async function boot() {
    state.manifest = await loadJson("../data/avatar-manifest.json", FALLBACK_MANIFEST);
    await preloadAssets();
    setupHotkeys();
    scheduleBlink();
    renderLoop();
    setupMic();
  }

  boot();
})();
