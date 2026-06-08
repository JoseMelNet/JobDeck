importScripts("linkedin-job-helpers.js");

const API_BASE = "http://localhost:8001";
const ACTIVE_TASK_KEY = "activeAnalysisTasks";
const LINKEDIN_HELPERS = globalThis.LinkedInJobHelpers;

function normalizarUrlVacante(url) {
  return LINKEDIN_HELPERS.normalizeLink(url);
}

function resolverClaveVacante({ vacancyKey, link, pageUrl }) {
  return (
    vacancyKey ||
    LINKEDIN_HELPERS.buildVacancyKey(link) ||
    LINKEDIN_HELPERS.buildVacancyKey(pageUrl) ||
    normalizarUrlVacante(link) ||
    normalizarUrlVacante(pageUrl)
  );
}

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

  if (request.action === "clearActiveTask") {
    const targetKey = resolverClaveVacante(request);
    chrome.storage.local.get(ACTIVE_TASK_KEY, (result) => {
      const tasks = result[ACTIVE_TASK_KEY] || {};
      if (targetKey) {
        delete tasks[targetKey];
        chrome.storage.local.set({ [ACTIVE_TASK_KEY]: tasks }, () => sendResponse({ success: true }));
        return;
      }
      chrome.storage.local.remove(ACTIVE_TASK_KEY, () => sendResponse({ success: true }));
    });
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

  const vacancyKey = resolverClaveVacante({
    vacancyKey: payload.vacancyKey,
    link: payload.link,
    pageUrl: payload.pageUrl,
  });

  const activeTask = {
    taskId: data.task_id || data.job_id,
    vacancyId: data.id,
    status: data.status,
    message: data.message,
    pageUrl: normalizarUrlVacante(payload.link),
    vacancyKey,
    savedAt: new Date().toISOString(),
  };
  const storage = await chrome.storage.local.get(ACTIVE_TASK_KEY);
  const tasks = storage[ACTIVE_TASK_KEY] || {};
  tasks[vacancyKey] = activeTask;
  await chrome.storage.local.set({ [ACTIVE_TASK_KEY]: tasks });
  return activeTask;
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
    taskId: null,
    vacancyId: data.id,
    status: "completed",
    message: "Vacante guardada. La API local no soporta analisis en segundo plano todavia.",
    legacyMode: true,
    vacancyKey: resolverClaveVacante({
      vacancyKey: payload.vacancyKey,
      link: payload.link,
      pageUrl: payload.pageUrl,
    }),
    savedAt: new Date().toISOString(),
  };
}
