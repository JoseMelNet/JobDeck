/**
 * content.js — v2
 * Selectores confirmados por inspección real del DOM de LinkedIn.
 *
 * Estrategia por campo:
 *   Cargo      → document.title  ("Cargo | Empresa | LinkedIn")
 *   Empresa    → document.title  (mismo parse)
 *   Modalidad  → primer SPAN nodo-hoja con texto exacto de modalidad
 *   Descripción→ el P/SPAN más largo de la página (500–8000 chars)
 *   Link       → window.location.href limpio
 */

// ─────────────────────────────────────────────────────────────
// CARGO Y EMPRESA — desde document.title
// Formato estable: "Cargo | Empresa | LinkedIn"
// ─────────────────────────────────────────────────────────────

function extraerDesdeTitle() {
  const title  = document.title || "";
  const partes = title.split(" | ").map(p => p.trim()).filter(Boolean);
  const cargo   = partes[0] || "";
  const empresa = partes.length >= 3 ? partes[1] : (partes[1] || "");
  return { cargo, empresa };
}

// ─────────────────────────────────────────────────────────────
// MODALIDAD — primer SPAN nodo-hoja con texto exacto
// ─────────────────────────────────────────────────────────────

const MODALIDADES_VALIDAS = new Set([
  "Remoto", "Híbrido", "Presencial",
  "Remote", "Hybrid", "On-site", "On site",
]);

function normalizarModalidad(texto) {
  const t = texto.toLowerCase().trim();
  if (t === "remote"  || t === "remoto")                        return "Remoto";
  if (t === "hybrid"  || t === "híbrido" || t === "hibrido")    return "Híbrido";
  if (t === "on-site" || t === "on site" || t === "presencial") return "Presencial";
  return null;
}

function extraerModalidad() {
  for (const span of document.querySelectorAll("span")) {
    if (span.children.length > 0) continue;
    const texto = span.innerText?.trim() || "";
    if (MODALIDADES_VALIDAS.has(texto)) {
      return normalizarModalidad(texto) || "Remoto";
    }
  }
  return "Remoto";
}

// ─────────────────────────────────────────────────────────────
// DESCRIPCIÓN — el P o SPAN más largo entre 500 y 8000 chars
// ─────────────────────────────────────────────────────────────

function extraerDescripcion() {
  let mejor    = "";
  let mejorLen = 0;

  for (const el of document.querySelectorAll("p, span")) {
    const texto = el.innerText?.trim() || "";
    if (texto.length > 500 && texto.length < 8000 && texto.length > mejorLen) {
      mejor    = texto;
      mejorLen = texto.length;
    }
  }
  return mejor;
}

// ─────────────────────────────────────────────────────────────
// FUNCIÓN PRINCIPAL
// ─────────────────────────────────────────────────────────────

function extraerDatosVacante() {
  const { cargo, empresa } = extraerDesdeTitle();
  const modalidad          = extraerModalidad();
  const descripcion        = extraerDescripcion();
  const link               = window.location.href.split("?")[0];

  return {
    cargo,
    empresa,
    modalidad,
    descripcion,
    link,
    _calidad: {
      cargo:       cargo.length > 0,
      empresa:     empresa.length > 0,
      modalidad:   MODALIDADES_VALIDAS.has(modalidad),
      descripcion: descripcion.length > 200,
    },
  };
}

// ─────────────────────────────────────────────────────────────
// LISTENER
// ─────────────────────────────────────────────────────────────

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extraerVacante") {
    try {
      const datos = extraerDatosVacante();
      sendResponse({ success: true, datos });
    } catch (error) {
      sendResponse({ success: false, error: error.message });
    }
  }
  return true;
});