/**
 * popup.js
 * Orquesta toda la lógica del popup:
 *   1. Verifica que la API local esté corriendo
 *   2. Inyecta content.js y solicita extracción del DOM
 *   3. Renderiza el formulario con los datos extraídos (editables)
 *   4. Envía el POST a la API y muestra el resultado
 */

const API_BASE = "http://localhost:8001";

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
  const btn = $("btnGuardar");
  btn.disabled = true;
  btn.textContent = "Guardando...";

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
    btn.disabled = false;
    btn.textContent = "💾 Guardar en CVs-Optimizador";
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/vacantes`, {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok && data.success) {
      mostrarToast("success", `✅ Vacante guardada correctamente (ID: ${data.id})`);
      btn.textContent = "✅ Guardada";
    } else {
      const detalle = data.detail || data.message || "Error desconocido";
      mostrarToast("error", `❌ ${detalle}`);
      btn.disabled = false;
      btn.textContent = "💾 Guardar en CVs-Optimizador";
    }
  } catch (err) {
    mostrarToast("error", "❌ No se pudo conectar con la API. ¿Está corriendo uvicorn?");
    btn.disabled = false;
    btn.textContent = "💾 Guardar en CVs-Optimizador";
  }
}

// ─────────────────────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────────────────────

async function init() {
  // 1. Verificar API
  const apiOk = await verificarAPI();

  // 2. Obtener tab actual
  const tab = await obtenerTab();

  // 3. Verificar que sea una página de vacante de LinkedIn
  if (!esLinkedInJobView(tab.url)) {
    renderPaginaIncorrecta(tab.url);
    return;
  }

  // 4. Extraer datos del DOM
  $("mainContent").innerHTML = `<div class="spinner" style="display:block;margin:30px auto;"></div>`;

  const resultado = await extraerDatosDeTab(tab.id);

  if (!resultado.success) {
    renderError(resultado.error || "Error desconocido al leer la página.");
    return;
  }

  // 5. Renderizar formulario (con datos extraídos editables)
  renderFormulario(resultado.datos);

  // 6. Si la API no está disponible, deshabilitar el botón de guardar
  if (!apiOk) {
    const btn = $("btnGuardar");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "API no disponible";
    }
  }
}

document.addEventListener("DOMContentLoaded", init);
