/**
 * sidepanel.js
 * Orquesta toda la lógica del panel lateral:
 *   1. Verifica que la API local esté corriendo
 *   2. Inyecta content.js y solicita extracción del DOM
 *   3. Renderiza el formulario con los datos extraídos (editables)
 *   4. Envía el POST a la API y muestra el resultado
 */

const API_BASE = "http://localhost:8001";
const ACTIVE_TASK_KEY = "activeAnalysisTasks";
const LAST_ANALYSIS_KEY = "lastAnalysisResults";
let pollingTimer = null;
let currentTabId = null;
let currentTabUrl = null;
let watchersInitialized = false;

const MODALIDADES = ["Remoto", "Presencial", "Híbrido"];

// ─────────────────────────────────────────────────────────────
// HELPERS DOM
// ─────────────────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

function setStatus(estado, texto) {
  const dot  = $("statusDot");
  const span = $("statusText");
  dot.className  = `status-dot ${estado}`;
  span.textContent = texto;
}

function mostrarToast(tipo, mensaje) {
  // Eliminar toast previo si existe
  const prev = document.querySelector(".toast");
  if (prev) prev.remove();

  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  toast.style.display = "block";
  toast.textContent = mensaje;
  $("mainContent").appendChild(toast);
}

function limpiarVistaTransitoria() {
  document.querySelectorAll(".toast").forEach((t) => t.remove());
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

async function storageRemove(key) {
  await chrome.storage.local.remove(key);
}

async function storageSet(values) {
  await chrome.storage.local.set(values);
}

async function guardarDatoPorUrl(storageKey, pageUrl, value) {
  const normalizedUrl = normalizarUrlVacante(pageUrl);
  if (!normalizedUrl) return;
  const current = (await storageGet(storageKey)) || {};
  current[normalizedUrl] = value;
  await storageSet({ [storageKey]: current });
}

async function leerDatoPorUrl(storageKey, pageUrl) {
  const normalizedUrl = normalizarUrlVacante(pageUrl);
  if (!normalizedUrl) return null;
  const current = (await storageGet(storageKey)) || {};
  return current[normalizedUrl] || null;
}

async function borrarDatoPorUrl(storageKey, pageUrl) {
  const normalizedUrl = normalizarUrlVacante(pageUrl);
  if (!normalizedUrl) return;
  const current = (await storageGet(storageKey)) || {};
  if (!(normalizedUrl in current)) return;
  delete current[normalizedUrl];
  await storageSet({ [storageKey]: current });
}

function normalizarUrlVacante(url) {
  return (url || "").split("?")[0];
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
          await guardarDatoPorUrl(LAST_ANALYSIS_KEY, currentTabUrl, {
            vacancyId: task.vacancy_id,
            pageUrl: currentTabUrl,
            analysis,
          });
          renderAnalisis(analysis);
        } catch (_) {
          // Si el analisis todavia no esta visible por API, mantenemos solo el estado.
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
      await borrarDatoPorUrl(ACTIVE_TASK_KEY, currentTabUrl);
      await runtimeSendMessage({ action: "clearActiveTask", pageUrl: currentTabUrl });
    } catch (_) {
      setStatus("checking", "Analisis en segundo plano. Reabre el panel para refrescar.");
    }
  };

  await actualizar();
  pollingTimer = setInterval(actualizar, 2000);
}

async function restaurarTareaActiva() {
  const activeTask = await leerDatoPorUrl(ACTIVE_TASK_KEY, currentTabUrl);
  if (!activeTask?.taskId) return;
  mostrarToast("info", "ℹ️ Hay una vacante procesandose en segundo plano.");
  await iniciarSeguimientoTarea(activeTask.taskId);
}

async function restaurarUltimoAnalisis() {
  const lastAnalysis = await leerDatoPorUrl(LAST_ANALYSIS_KEY, currentTabUrl);
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

    await guardarDatoPorUrl(LAST_ANALYSIS_KEY, link, {
      vacancyId: result.vacancy.id,
      pageUrl: normalizarUrlVacante(link),
      analysis: result.analysis,
    });
    renderAnalisis(result.analysis);
    setStatus("ok", "Vacante ya analizada");
    return true;
  } catch (_) {
    return false;
  }
}

// ─────────────────────────────────────────────────────────────
// 1. VERIFICAR API
// ─────────────────────────────────────────────────────────────

async function verificarAPI() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    const data = await res.json();

    if (data.db_connected) {
      setStatus("ok", "API activa · BD conectada");
      return true;
    } else {
      setStatus("error", "API activa pero sin conexión a BD");
      return false;
    }
  } catch (_) {
    setStatus("error", "API no disponible — ejecuta: uvicorn api:app --port 8001");
    return false;
  }
}

// ─────────────────────────────────────────────────────────────
// 2. DETECTAR PÁGINA Y EXTRAER DATOS
// ─────────────────────────────────────────────────────────────

async function obtenerTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function esLinkedInJobView(url) {
  return url && url.includes("linkedin.com/jobs/view/");
}

async function extraerDatosDeTab(tabId) {
  // Inyectar content.js si no está ya inyectado
  try {
    await chrome.scripting.executeScript({
      target: { tabId },
      files: ["content.js"],
    });
  } catch (_) {
    // Si falla la inyección, probablemente ya estaba cargado
  }

  return new Promise((resolve) => {
    chrome.tabs.sendMessage(tabId, { action: "extraerVacante" }, (response) => {
      if (chrome.runtime.lastError || !response) {
        resolve({ success: false, error: "No se pudo comunicar con la página." });
      } else {
        resolve(response);
      }
    });
  });
}

// ─────────────────────────────────────────────────────────────
// 3. RENDERIZAR FORMULARIO
// ─────────────────────────────────────────────────────────────

function chipCalidad(campo, ok) {
  return `<span class="calidad-chip ${ok ? "ok" : "warn"}">${ok ? "✓" : "⚠"} ${campo}</span>`;
}

function renderFormulario(datos) {
  const { cargo, empresa, modalidad, descripcion, link, _calidad } = datos;

  // Indicadores de calidad de extracción
  const calidadHTML = `
    <div class="calidad-bar">
      ${chipCalidad("Cargo",       _calidad.cargo)}
      ${chipCalidad("Empresa",     _calidad.empresa)}
      ${chipCalidad("Modalidad",   _calidad.modalidad)}
      ${chipCalidad("Descripción", _calidad.descripcion)}
    </div>
  `;

  // Opciones de modalidad
  const optsModalidad = MODALIDADES.map((m) =>
    `<option value="${m}" ${m === modalidad ? "selected" : ""}>${m}</option>`
  ).join("");

  const html = `
    ${calidadHTML}

    <div class="field">
      <label>💼 Cargo</label>
      <input type="text" id="f_cargo" value="${escHtml(cargo)}" placeholder="Título del puesto" />
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
      <label>🔗 Link</label>
      <input type="text" id="f_link" value="${escHtml(link)}" placeholder="URL de la vacante" />
    </div>

    <hr class="divider" />

    <div class="field">
      <label>📝 Descripción</label>
      <textarea id="f_descripcion" rows="5">${escHtml(descripcion)}</textarea>
    </div>

    <button class="btn-guardar" id="btnGuardar">💾 Guardar en CVs-Optimizador</button>
  `;

  $("mainContent").innerHTML = html;

  // Evento del botón
  $("btnGuardar").addEventListener("click", guardarVacante);
}

function renderPaginaIncorrecta(url) {
  $("mainContent").innerHTML = `
    <div class="alert">
      <strong>Página no compatible</strong><br/>
      Esta extensión solo funciona en páginas de detalle de vacantes de LinkedIn.<br/><br/>
      Navega a una URL del tipo:<br/>
      <code style="color:#93c5fd;font-size:0.7rem">linkedin.com/jobs/view/...</code>
    </div>
  `;
}

function renderError(mensaje) {
  $("mainContent").innerHTML = `
    <div class="alert">
      <strong>Error de extracción</strong><br/>
      ${escHtml(mensaje)}<br/><br/>
      Recarga la página de LinkedIn e intenta de nuevo.
    </div>
  `;
}

// Escapar HTML para evitar XSS al insertar texto de LinkedIn en innerHTML
function escHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ─────────────────────────────────────────────────────────────
// 4. GUARDAR VACANTE
// ─────────────────────────────────────────────────────────────

async function guardarVacante() {
  setGuardarEstado("💾 Guardando vacante...", true);

  // Eliminar toast previo
  document.querySelectorAll(".toast").forEach((t) => t.remove());

  const payload = {
    cargo:       $("f_cargo").value.trim(),
    empresa:     $("f_empresa").value.trim(),
    modalidad:   $("f_modalidad").value,
    link:        $("f_link").value.trim() || null,
    descripcion: $("f_descripcion").value.trim(),
  };

  // Validación básica
  if (!payload.cargo || !payload.empresa || !payload.descripcion) {
    mostrarToast("error", "⚠️ Cargo, empresa y descripción son obligatorios.");
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
          await guardarDatoPorUrl(LAST_ANALYSIS_KEY, payload.link, {
            vacancyId: response.vacancyId,
            pageUrl: normalizarUrlVacante(payload.link),
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
    } else {
      const detalle = response?.error || "Error desconocido";
      mostrarToast("error", `❌ ${detalle}`);
      setStatus("error", "No se pudo guardar la vacante");
      setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
    }
  } catch (err) {
    mostrarToast("error", "❌ No se pudo conectar con la API. ¿Está corriendo uvicorn?");
    setStatus("error", "API no disponible");
    setGuardarEstado("💾 Guardar en CVs-Optimizador", false);
  }
}

async function refrescarTabActiva() {
  const apiOk = await verificarAPI();
  const tab = await obtenerTab();
  currentTabId = tab?.id ?? null;
  currentTabUrl = normalizarUrlVacante(tab?.url);

  limpiarVistaTransitoria();
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }

  if (!esLinkedInJobView(tab?.url)) {
    renderPaginaIncorrecta(tab?.url);
    return;
  }

  $("mainContent").innerHTML = `<div class="spinner" style="display:block;margin:30px auto;"></div>`;
  const resultado = await extraerDatosDeTab(tab.id);

  if (!resultado.success) {
    renderError(resultado.error || "Error desconocido al leer la página.");
    return;
  }

  renderFormulario(resultado.datos);
  await restaurarTareaActiva();
  await restaurarUltimoAnalisis();
  await cargarAnalisisHistorico(resultado.datos.link);

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

// ─────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────

async function init() {
  inicializarObservadoresTabs();
  await refrescarTabActiva();
}

document.addEventListener("DOMContentLoaded", init);
