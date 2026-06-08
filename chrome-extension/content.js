/**
 * content.js
 * Extrae la vacante activa desde LinkedIn Jobs, tanto en /jobs/view/<id>
 * como en /jobs/search con panel de detalle abierto.
 */

const MODALIDADES_VALIDAS = new Set([
  "Remoto", "Hibrido", "Híbrido", "Presencial",
  "Remote", "Hybrid", "On-site", "On site",
]);

const LINKEDIN_HELPERS = globalThis.LinkedInJobHelpers;

function textoLimpio(value) {
  return (value || "").replace(/\s+/g, " ").trim();
}

function extraerDesdeTitle() {
  const title = document.title || "";
  const partes = title.split(" | ").map((value) => value.trim()).filter(Boolean);
  const cargo = partes[0] || "";
  const empresa = partes.length >= 3 ? partes[1] : (partes[1] || "");
  return { cargo, empresa };
}

function normalizarModalidad(texto) {
  const t = textoLimpio(texto).toLowerCase();
  if (t === "remote" || t === "remoto") return "Remoto";
  if (t === "hybrid" || t === "hibrido" || t === "híbrido") return "Híbrido";
  if (t === "on-site" || t === "on site" || t === "presencial") return "Presencial";
  return null;
}

function extraerModalidad(root = document) {
  for (const span of root.querySelectorAll("span")) {
    if (span.children.length > 0) continue;
    const texto = textoLimpio(span.innerText);
    if (MODALIDADES_VALIDAS.has(texto)) {
      return normalizarModalidad(texto) || "Remoto";
    }
  }
  return "Remoto";
}

function obtenerContenedorDescripcionBusqueda(root = document) {
  const selectores = [
    ".jobs-description__container",
    ".jobs-box__html-content",
    ".jobs-description-content__text",
    ".jobs-description",
  ];

  for (const selector of selectores) {
    const node = root.querySelector(selector);
    if (node) return node;
  }

  return null;
}

function obtenerTextoPorSelectores(selectores, root = document) {
  for (const selector of selectores) {
    const node = root.querySelector(selector);
    const texto = textoLimpio(node?.innerText || node?.textContent || "");
    if (texto) return texto;
  }
  return "";
}

function obtenerRootDetalleBusqueda() {
  const selectors = [
    ".jobs-search__job-details--container",
    ".jobs-search__job-details",
    ".jobs-details",
    ".scaffold-layout__detail",
    ".jobs-unified-top-card",
    "main",
  ];

  for (const selector of selectors) {
    const node = document.querySelector(selector);
    if (node) return node;
  }

  return document;
}

function extraerHeaderBusqueda(root) {
  const cargo = obtenerTextoPorSelectores([
    ".job-details-jobs-unified-top-card__job-title",
    ".jobs-unified-top-card__job-title",
    ".jobs-details-top-card__job-title",
    ".t-24.job-details-jobs-unified-top-card__job-title",
    "h1",
  ], root);

  const empresa = obtenerTextoPorSelectores([
    ".job-details-jobs-unified-top-card__company-name",
    ".jobs-unified-top-card__company-name",
    ".jobs-details-top-card__company-url",
    ".jobs-details-top-card__company-info a",
    "a[href*='/company/']",
  ], root);

  return { cargo, empresa };
}

function extraerVacanteJobView(identity) {
  const { cargo, empresa } = extraerDesdeTitle();
  const modalidad = extraerModalidad(document);
  const descripcion = LINKEDIN_HELPERS.extractLegacyDescriptionFrom(document);

  return {
    cargo,
    empresa,
    modalidad,
    descripcion,
    link: identity.canonicalLink,
    vacancyKey: identity.vacancyKey,
    _identity: identity,
    _calidad: {
      cargo: cargo.length > 0,
      empresa: empresa.length > 0,
      modalidad: MODALIDADES_VALIDAS.has(modalidad),
      descripcion: descripcion.length > 200,
      jobId: Boolean(identity.jobId),
    },
  };
}

function extraerVacanteSearchPanel(identity) {
  const root = obtenerRootDetalleBusqueda();
  const fallback = extraerDesdeTitle();
  const header = extraerHeaderBusqueda(root);
  const cargo = header.cargo || fallback.cargo;
  const empresa = header.empresa || fallback.empresa;
  const modalidad = extraerModalidad(root);
  const descriptionContainer = obtenerContenedorDescripcionBusqueda(root);
  const descripcionNormalizada = LINKEDIN_HELPERS.extractLegacyDescriptionFrom(descriptionContainer || root);

  return {
    cargo,
    empresa,
    modalidad,
    descripcion: descripcionNormalizada,
    link: identity.canonicalLink,
    vacancyKey: identity.vacancyKey,
    _identity: identity,
    _calidad: {
      cargo: cargo.length > 0,
      empresa: empresa.length > 0,
      modalidad: MODALIDADES_VALIDAS.has(modalidad),
      descripcion: descripcionNormalizada.length > 200,
      jobId: Boolean(identity.jobId),
    },
  };
}

function extraerDatosVacante() {
  const identity = LINKEDIN_HELPERS.resolveVacancyIdentity({
    url: window.location.href,
    doc: document,
  });

  if (identity.context === "unsupported") {
    throw new Error("Esta pagina de LinkedIn Jobs no esta soportada por la extension.");
  }

  if (!identity.canSave) {
    throw new Error("No se pudo resolver un job_id estable para la vacante activa.");
  }

  if (identity.context === "job_view") {
    return extraerVacanteJobView(identity);
  }

  return extraerVacanteSearchPanel(identity);
}

if (!globalThis.__CVS_OPTIMIZADOR_LINKEDIN_CONTENT_LISTENER__) {
  chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
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

  globalThis.__CVS_OPTIMIZADOR_LINKEDIN_CONTENT_LISTENER__ = true;
}
