/**
 * sidepanel.js
 * Orquesta la extraccion, guardado y seguimiento desde el panel lateral.
 */

const API_BASE = "http://localhost:8001";
const ACTIVE_TASK_KEY = "activeAnalysisTasks";
const LAST_ANALYSIS_KEY = "lastAnalysisResults";
const LINKEDIN_HELPERS = globalThis.LinkedInJobHelpers;

let pollingTimer = null;
let currentTabId = null;
let currentTabUrl = null;
let currentCanonicalLink = null;
let currentVacancyKey = null;
let currentStorageKeys = [];
let currentContext = "unsupported";
let watchersInitialized = false;

const MODALIDADES = ["Remoto", "Presencial", "Híbrido"];

const $ = (id) => document.getElementById(id);

function setStatus(estado, texto) {
  const dot = $("statusDot");
  const span = $("statusText");
  dot.className = `status-dot ${estado}`;
  span.textContent = texto;
}

function mostrarToast(tipo, mensaje) {
  const prev = document.querySelector(".toast");
  if (prev) prev.remove();

  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.style.display = "block";
  toast.textContent = mensaje;
  $("mainContent").appendChild(toast);
}

function limpiarVistaTransitoria() {
  document.querySelectorAll(".toast").forEach((toast) => toast.remove());
  const analysisPanel = document.getElementById("analysisPanel");
  if (analysisPanel) analysisPanel.remove();
}

function setGuardarEstado(texto, disabled = true) {
  const btn = $("btnGuardar");
  if (!btn) return;
  btn.disabled = disabled;
  btn.textContent = texto;
}

function runtimeSendMessage(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      resolve(response);
    });
  });
}

async function storageGet(key) {
  const result = await chrome.storage.local.get(key);
  return result[key];
}

async function storageSet(values) {
  await chrome.storage.local.set(values);
}

function normalizarUrlVacante(url) {
  return LINKEDIN_HELPERS.normalizeLink(url);
}

function esPaginaLinkedInSoportada(url) {
  return LINKEDIN_HELPERS.detectLinkedInContext(url) !== "unsupported";
}

function construirStorageKeys({ canonicalLink, tabUrl, context }) {
  const keys = [];
  const vacancyKey = LINKEDIN_HELPERS.buildVacancyKey(canonicalLink);
  const canonicalLegacy = normalizarUrlVacante(canonicalLink);
  const tabLegacy = normalizarUrlVacante(tabUrl);

  if (vacancyKey) keys.push(vacancyKey);
  if (canonicalLegacy && !keys.includes(canonicalLegacy)) keys.push(canonicalLegacy);

  const puedeUsarTabFallback = !canonicalLink || context === "job_view";
  if (puedeUsarTabFallback && tabLegacy && !keys.includes(tabLegacy)) {
    keys.push(tabLegacy);
  }

  return keys;
}

function actualizarIdentidadActual(datos, tabUrl) {
  currentContext = datos?._identity?.context || LINKEDIN_HELPERS.detectLinkedInContext(tabUrl);
  currentCanonicalLink = datos?.link || null;
  currentVacancyKey = datos?.vacancyKey || LINKEDIN_HELPERS.buildVacancyKey(currentCanonicalLink);
  currentStorageKeys = construirStorageKeys({
    canonicalLink: currentCanonicalLink,
    tabUrl,
    context: currentContext,
  });
}

function resetIdentidadActual(tabUrl) {
  currentContext = LINKEDIN_HELPERS.detectLinkedInContext(tabUrl);
  currentCanonicalLink = null;
  currentVacancyKey = null;
  currentStorageKeys = construirStorageKeys({
    canonicalLink: null,
    tabUrl,
    context: currentContext,
  });
}

function primaryStorageKey() {
  return currentStorageKeys[0] || currentVacancyKey || currentCanonicalLink || currentTabUrl || null;
}

async function guardarDatoPorClaves(storageKey, keys, value) {
  const normalizedKeys = (keys || []).filter(Boolean);
  if (!normalizedKeys.length) return;

  const current = (await storageGet(storageKey)) || {};
  current[normalizedKeys[0]] = value;
  await storageSet({ [storageKey]: current });
}

async function leerDatoPorClaves(storageKey, keys) {
  const normalizedKeys = (keys || []).filter(Boolean);
  if (!normalizedKeys.length) return null;

  const current = (await storageGet(storageKey)) || {};
  for (const key of normalizedKeys) {
    if (current[key]) return current[key];
  }
  return null;
}

async function borrarDatoPorClaves(storageKey, keys) {
  const normalizedKeys = (keys || []).filter(Boolean);
  if (!normalizedKeys.length) return;

  const current = (await storageGet(storageKey)) || {};
  let changed = false;

  for (const key of normalizedKeys) {
    if (key in current) {
      delete current[key];
      changed = true;
    }
  }

  if (changed) {
    await storageSet({ [storageKey]: current });
  }
}

function describirTarea(task) {
  if (task.status === "queued") {
    return { status: "checking", text: "Vacante guardada · analisis en cola" };
  }
  if (task.status === "running") {
    return { status: "checking", text: "Analizando vacante en segundo plano..." };
  }
  if (task.status === "completed") {
    return { status: "ok", text: "Vacante guardada y analizada" };
  }
  return { status: "error", text: "Vacante guardada, pero el analisis fallo" };
}

async function consultarEstadoTarea(taskId) {
  const res = await fetch(`${API_BASE}/vacantes/tasks/${taskId}`, { signal: AbortSignal.timeout(3000) });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "No se pudo consultar el estado del analisis");
  }
  return data;
}

async function consultarAnalisisVacante(vacancyId) {
  const res = await fetch(`${API_BASE}/vacantes/${vacancyId}/analysis`, { signal: AbortSignal.timeout(3000) });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "No se pudo cargar el analisis");
  }
  return data.analysis;
}

async function consultarVacantePorLink(link) {
  const url = new URL(`${API_BASE}/vacantes/by-link`);
  url.searchParams.set("link", normalizarUrlVacante(link));
  const res = await fetch(url, { signal: AbortSignal.timeout(3000) });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "No se pudo consultar la vacante");
  }
  return data;
}

function renderAnalisis(analysis) {
  const resumenPrevio = document.getElementById("analysisPanel");
  if (resumenPrevio) resumenPrevio.remove();

  const root = document.createElement("section");
  root.className = "analysis-panel";
  root.id = "analysisPanel";

  const fortalezas = (analysis.fortalezas_principales || []).slice(0, 3);
  const gaps = (analysis.skills_gap || []).slice(0, 4);

  root.innerHTML = `
    <h3>Analisis de la vacante</h3>
    <div class="analysis-grid">
      <article class="analysis-card">
        <div class="analysis-card-label">Score</div>
        <div class="analysis-card-value">${Math.round(analysis.score_total || 0)}</div>
      </article>
      <article class="analysis-card">
        <div class="analysis-card-label">Afinidad</div>
        <div class="analysis-card-value">${analysis.afinidad_general || "-"}</div>
      </article>
      <article class="analysis-card">
        <div class="analysis-card-label">Decision</div>
        <div class="analysis-card-value">${analysis.decision_aplicacion || "-"}</div>
      </article>
    </div>
    <div class="analysis-copy">${escHtml(analysis.resumen_analisis || analysis.justificacion_decision || "Sin resumen disponible.")}</div>
    ${fortalezas.length ? `<div class="analysis-tags">${fortalezas.map((item) => `<span class="analysis-tag">${escHtml(item)}</span>`).join("")}</div>` : ""}
    ${gaps.length ? `<div class="analysis-copy"><strong>Gaps:</strong> ${escHtml(gaps.join(", "))}</div>` : ""}
  `;

  $("mainContent").appendChild(root);
}

async function iniciarSeguimientoTarea(taskId) {
  if (pollingTimer) clearInterval(pollingTimer);

  const actualizar = async () => {
    try {
      const task = await consultarEstadoTarea(taskId);
      const status = describirTarea(task);
      setStatus(status.status, status.text);

      if (task.status === "queued" || task.status === "running") {
        setGuardarEstado(task.status === "queued" ? "⏳ Analisis en cola..." : "🤖 Analizando...", true);
        return;
      }

      if (task.status === "completed") {
        try {
          const analysis = await consultarAnalisisVacante(task.vacancy_id);
          await guardarDatoPorClaves(LAST_ANALYSIS_KEY, currentStorageKeys, {
            vacancyId: task.vacancy_id,
            pageUrl: currentCanonicalLink || currentTabUrl,
            vacancyKey: currentVacancyKey,
            analysis,
          });
          renderAnalisis(analysis);
        } catch (_) {
          // Si el analisis aun no esta visible por API, mantenemos solo el estado.
        }
        mostrarToast("success", `✅ ${task.message}`);
        setGuardarEstado("✅ Guardada y analizada", true);
      } else {
        const detalle = task.error ? `${task.message} ${task.error}` : task.message;
        mostrarToast("error", `❌ ${detalle}`);
        setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
      }

      clearInterval(pollingTimer);
      pollingTimer = null;
      await borrarDatoPorClaves(ACTIVE_TASK_KEY, currentStorageKeys);
      await runtimeSendMessage({
        action: "clearActiveTask",
        vacancyKey: currentVacancyKey,
        link: currentCanonicalLink,
        pageUrl: currentTabUrl,
      });
    } catch (_) {
      setStatus("checking", "Analisis en segundo plano. Reabre el panel para refrescar.");
    }
  };

  await actualizar();
  pollingTimer = setInterval(actualizar, 2000);
}

async function restaurarTareaActiva() {
  const activeTask = await leerDatoPorClaves(ACTIVE_TASK_KEY, currentStorageKeys);
  if (!activeTask?.taskId) return;
  mostrarToast("info", "ℹ️ Hay una vacante procesandose en segundo plano.");
  await iniciarSeguimientoTarea(activeTask.taskId);
}

async function restaurarUltimoAnalisis() {
  const lastAnalysis = await leerDatoPorClaves(LAST_ANALYSIS_KEY, currentStorageKeys);
  if (!lastAnalysis?.analysis) return;
  renderAnalisis(lastAnalysis.analysis);
}

async function cargarAnalisisHistorico(link) {
  if (!link) return false;

  try {
    const result = await consultarVacantePorLink(link);
    if (!result?.found || !result?.analysis || !result?.vacancy?.id) {
      return false;
    }

    await guardarDatoPorClaves(LAST_ANALYSIS_KEY, currentStorageKeys, {
      vacancyId: result.vacancy.id,
      pageUrl: normalizarUrlVacante(link),
      vacancyKey: currentVacancyKey,
      analysis: result.analysis,
    });
    renderAnalisis(result.analysis);
    setStatus("ok", "Vacante ya analizada");
    return true;
  } catch (_) {
    return false;
  }
}

async function verificarAPI() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    const data = await res.json();

    if (data.db_connected) {
      setStatus("ok", "API activa · BD conectada");
      return true;
    }

    setStatus("error", "API activa pero sin conexion a BD");
    return false;
  } catch (_) {
    setStatus("error", "API no disponible — ejecuta: uvicorn api:app --port 8001");
    return false;
  }
}

async function obtenerTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

async function extraerDatosDeTab(tabId) {
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["linkedin-job-helpers.js", "content.js"],
    });
  } catch (_) {
    // Si falla la inyeccion, probablemente la pagina no la permite o ya estaba cargada.
  }

  return new Promise((resolve) => {
    chrome.tabs.sendMessage(tabId, { action: "extraerVacante" }, (response) => {
      if (chrome.runtime.lastError || !response) {
        resolve({ success: false, error: "No se pudo comunicar con la pagina." });
      } else {
        resolve(response);
      }
    });
  });
}

function chipCalidad(campo, ok) {
  return `<span class="calidad-chip ${ok ? "ok" : "warn"}">${ok ? "✓" : "⚠"} ${campo}</span>`;
}

function renderFormulario(datos) {
  const { cargo, empresa, modalidad, descripcion, link, _calidad } = datos;

  const calidadHTML = `
    <div class="calidad-bar">
      ${chipCalidad("Cargo", _calidad.cargo)}
      ${chipCalidad("Empresa", _calidad.empresa)}
      ${chipCalidad("Modalidad", _calidad.modalidad)}
      ${chipCalidad("Descripcion", _calidad.descripcion)}
      ${chipCalidad("job_id", _calidad.jobId)}
    </div>
  `;

  const optsModalidad = MODALIDADES.map((item) =>
    `<option value="${item}" ${item === modalidad ? "selected" : ""}>${item}</option>`
  ).join("");

  const html = `
    ${calidadHTML}

    <div class="field">
      <label>💼 Cargo</label>
      <input type="text" id="f_cargo" value="${escHtml(cargo)}" placeholder="Titulo del puesto" />
    </div>

    <div class="field-grid">
      <div class="field">
        <label>🏢 Empresa</label>
        <input type="text" id="f_empresa" value="${escHtml(empresa)}" placeholder="Nombre empresa" />
      </div>
      <div class="field">
        <label>📍 Modalidad</label>
        <select id="f_modalidad">${optsModalidad}</select>
      </div>
    </div>

    <div class="field">
      <label>🔗 Link canonico</label>
      <input type="text" id="f_link" value="${escHtml(link)}" placeholder="https://www.linkedin.com/jobs/view/..." />
    </div>

    <hr class="divider" />

    <div class="field">
      <label>📝 Descripcion</label>
      <textarea id="f_descripcion" rows="5">${escHtml(descripcion)}</textarea>
    </div>

    <button class="btn-guardar" id="btnGuardar">💾 Guardar en CVs-Optimizador</button>
  `;

  $("mainContent").innerHTML = html;
  $("btnGuardar").addEventListener("click", guardarVacante);
}

function renderPaginaIncorrecta() {
  $("mainContent").innerHTML = `
    <div class="alert">
      <strong>Pagina no compatible</strong><br/>
      Esta extension funciona solo en vacantes de LinkedIn Jobs.<br/><br/>
      Usa una URL del tipo:<br/>
      <code style="color:#93c5fd;font-size:0.7rem">linkedin.com/jobs/view/&lt;id&gt;</code><br/>
      o<br/>
      <code style="color:#93c5fd;font-size:0.7rem">linkedin.com/jobs/search/?currentJobId=&lt;id&gt;</code>
    </div>
  `;
}

function renderError(mensaje) {
  $("mainContent").innerHTML = `
    <div class="alert">
      <strong>Error de extraccion</strong><br/>
      ${escHtml(mensaje)}<br/><br/>
      Si estas en Jobs Search, abre una vacante activa visible en el panel de detalle e intenta de nuevo.
    </div>
  `;
}

function escHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

async function validarVacanteActivaAntesDeGuardar() {
  const resultado = await extraerDatosDeTab(currentTabId);
  if (!resultado.success) {
    throw new Error(resultado.error || "No se pudo verificar la vacante activa.");
  }

  const freshData = resultado.datos;
  const freshPrimaryKey =
    freshData.vacancyKey ||
    LINKEDIN_HELPERS.buildVacancyKey(freshData.link) ||
    freshData.link;
  const currentFormKey =
    currentVacancyKey ||
    LINKEDIN_HELPERS.buildVacancyKey($("f_link")?.value) ||
    currentCanonicalLink;

  if (freshPrimaryKey && currentFormKey && freshPrimaryKey !== currentFormKey) {
    await refrescarTabActiva({ skipApiCheck: true, toastMessage: "La vacante activa cambio. Actualizamos el formulario antes de guardar." });
    return { ready: false, datos: null };
  }

  actualizarIdentidadActual(freshData, currentTabUrl);
  return { ready: true, datos: freshData };
}

async function guardarVacante() {
  setGuardarEstado("💾 Guardando vacante...", true);
  document.querySelectorAll(".toast").forEach((toast) => toast.remove());

  const sync = await validarVacanteActivaAntesDeGuardar().catch((error) => {
    mostrarToast("error", `❌ ${error.message}`);
    setStatus("error", "No se pudo validar la vacante activa");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
    return null;
  });
  if (!sync || !sync.ready) {
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
    return;
  }

  const payload = {
    cargo: $("f_cargo").value.trim(),
    empresa: $("f_empresa").value.trim(),
    modalidad: $("f_modalidad").value,
    link: sync.datos.link,
    descripcion: $("f_descripcion").value.trim(),
    vacancyKey: sync.datos.vacancyKey,
    pageUrl: currentTabUrl,
  };

  if (!payload.link || !payload.vacancyKey) {
    mostrarToast("error", "❌ No se pudo resolver un job_id estable para esta vacante.");
    setStatus("error", "Falta job_id estable");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
    return;
  }

  if (!payload.cargo || !payload.empresa || !payload.descripcion) {
    mostrarToast("error", "⚠️ Cargo, empresa y descripcion son obligatorios.");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
    return;
  }

  try {
    setStatus("checking", "Guardando vacante...");
    const response = await runtimeSendMessage({
      action: "guardarVacanteBackground",
      payload,
    });

    if (response?.success) {
      if (response.legacyMode || !response.taskId) {
        setStatus("ok", "Vacante guardada");
        try {
          const analysis = await consultarAnalisisVacante(response.vacancyId);
          await guardarDatoPorClaves(LAST_ANALYSIS_KEY, currentStorageKeys, {
            vacancyId: response.vacancyId,
            pageUrl: payload.link,
            vacancyKey: payload.vacancyKey,
            analysis,
          });
          renderAnalisis(analysis);
          mostrarToast("success", `✅ Vacante guardada (ID: ${response.vacancyId}) y analisis cargado.`);
        } catch (_) {
          mostrarToast("success", `✅ Vacante guardada (ID: ${response.vacancyId}). Reinicia la API local si quieres usar el analisis en segundo plano.`);
        }
        setGuardarEstado("✅ Guardada", true);
        return;
      }

      mostrarToast("info", `ℹ️ Vacante guardada (ID: ${response.vacancyId}). Analisis en segundo plano iniciado.`);
      await iniciarSeguimientoTarea(response.taskId);
      return;
    }

    const detalle = response?.error || "Error desconocido";
    mostrarToast("error", `❌ ${detalle}`);
    setStatus("error", "No se pudo guardar la vacante");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
  } catch (_) {
    mostrarToast("error", "❌ No se pudo conectar con la API. Ejecuta: uvicorn api:app --reload --port 8001");
    setStatus("error", "API no disponible");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
  }
}

async function refrescarTabActiva(options = {}) {
  const { skipApiCheck = false, toastMessage = null } = options;
  const apiOk = skipApiCheck ? true : await verificarAPI();
  const tab = await obtenerTab();
  currentTabId = tab?.id ?? null;
  currentTabUrl = normalizarUrlVacante(tab?.url);
  resetIdentidadActual(tab?.url);

  limpiarVistaTransitoria();
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }

  if (!esPaginaLinkedInSoportada(tab?.url)) {
    renderPaginaIncorrecta();
    return;
  }

  $("mainContent").innerHTML = `<div class="spinner" style="display:block;margin:30px auto;"></div>`;
  const resultado = await extraerDatosDeTab(tab.id);

  if (!resultado.success) {
    renderError(resultado.error || "Error desconocido al leer la pagina.");
    return;
  }

  actualizarIdentidadActual(resultado.datos, tab?.url);
  renderFormulario(resultado.datos);
  await restaurarTareaActiva();
  await restaurarUltimoAnalisis();
  await cargarAnalisisHistorico(resultado.datos.link);

  if (toastMessage) {
    mostrarToast("info", `ℹ️ ${toastMessage}`);
  }

  if (!apiOk) {
    const btn = $("btnGuardar");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "API no disponible";
    }
  }
}

function inicializarObservadoresTabs() {
  if (watchersInitialized) return;
  watchersInitialized = true;

  chrome.tabs.onActivated.addListener(() => {
    refrescarTabActiva().catch(() => {});
  });

  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    const targetUrl = normalizarUrlVacante(tab?.url);
    const matchesCurrent = tabId === currentTabId || (tab?.active && targetUrl === currentTabUrl);
    if (!matchesCurrent) return;
    if (changeInfo.status === "complete") {
      refrescarTabActiva().catch(() => {});
    }
  });
}

async function init() {
  inicializarObservadoresTabs();
  await refrescarTabActiva();
}

document.addEventListener("DOMContentLoaded", init);
