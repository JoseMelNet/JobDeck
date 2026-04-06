const API_BASE = "http://localhost:8001";
const ACTIVE_JOB_KEY = "activeAnalysisJob";

if (chrome.sidePanel?.setPanelBehavior) {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
}

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.action === "guardarVacanteBackground") {
    guardarVacanteEnSegundoPlano(request.payload)
      .then((result) => sendResponse({ success: true, ...result }))
      .catch((error) => sendResponse({ success: false, error: error.message || "Error desconocido" }));
    return true;
  }

  if (request.action === "clearActiveJob") {
    chrome.storage.local.remove(ACTIVE_JOB_KEY, () => sendResponse({ success: true }));
    return true;
  }

  return false;
});

async function guardarVacanteEnSegundoPlano(payload) {
  const res = await fetch(`${API_BASE}/vacantes/async`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (res.status === 404) {
    return guardarVacanteConApiLegacy(payload);
  }

  const data = await res.json();
  if (!res.ok || !data.success) {
    throw new Error(data.detail || data.message || "No se pudo guardar la vacante");
  }

  const activeJob = {
    jobId: data.job_id,
    vacancyId: data.id,
    status: data.status,
    message: data.message,
    savedAt: new Date().toISOString(),
  };
  await chrome.storage.local.set({ [ACTIVE_JOB_KEY]: activeJob });
  return activeJob;
}

async function guardarVacanteConApiLegacy(payload) {
  const res = await fetch(`${API_BASE}/vacantes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok || !data.success) {
    throw new Error(data.detail || data.message || "No se pudo guardar la vacante");
  }

  return {
    jobId: null,
    vacancyId: data.id,
    status: "completed",
    message: "Vacante guardada. La API local no soporta analisis en segundo plano todavia.",
    legacyMode: true,
    savedAt: new Date().toISOString(),
  };
}
