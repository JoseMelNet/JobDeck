const test = require("node:test");
const assert = require("node:assert/strict");

const helpers = require("../linkedin-job-helpers.js");

function createNode(attrs = {}) {
  return {
    dataset: attrs.dataset || {},
    href: attrs.href || null,
    getAttribute(name) {
      return Object.prototype.hasOwnProperty.call(attrs, name) ? attrs[name] : null;
    },
  };
}

function createDocument(selectorMap) {
  return {
    querySelectorAll(selector) {
      return selectorMap[selector] || [];
    },
  };
}

function textNode(text) {
  return {
    nodeType: 3,
    textContent: text,
    nodeValue: text,
  };
}

function element(tagName, ...children) {
  const normalizedChildren = children.flat();
  const node = {
    nodeType: 1,
    tagName: tagName.toUpperCase(),
    nodeName: tagName.toUpperCase(),
    childNodes: normalizedChildren,
    textContent: normalizedChildren.map((child) => child.textContent || child.nodeValue || "").join(""),
    innerText: normalizedChildren.map((child) => child.textContent || child.nodeValue || "").join(""),
  };
  return node;
}

test("detects /jobs/view/<id> as job_view", () => {
  assert.equal(
    helpers.detectLinkedInContext("https://www.linkedin.com/jobs/view/4421695645/?tracking=abc"),
    "job_view",
  );
});

test("detects /jobs/search with currentJobId as job_search_active", () => {
  assert.equal(
    helpers.detectLinkedInContext("https://www.linkedin.com/jobs/search/?currentJobId=4421695645&keywords=data"),
    "job_search_active",
  );
});

test("resolves job_id from /jobs/view URL", () => {
  assert.equal(
    helpers.resolveJobIdFromViewUrl("https://www.linkedin.com/jobs/view/4421695645/?tracking=abc"),
    "4421695645",
  );
});

test("resolves job_id from currentJobId", () => {
  assert.equal(
    helpers.resolveJobIdFromSearchParams("https://www.linkedin.com/jobs/search/?currentJobId=4421695645"),
    "4421695645",
  );
});

test("resolves job_id from jobId", () => {
  assert.equal(
    helpers.resolveJobIdFromSearchParams("https://www.linkedin.com/jobs/search/?jobId=4400000001"),
    "4400000001",
  );
});

test("resolves job_id from internal href fallback", () => {
  const doc = createDocument({
    "a[href*='/jobs/view/']": [
      createNode({ href: "https://www.linkedin.com/jobs/view/4382412003/" }),
    ],
  });

  assert.equal(
    helpers.resolveJobId({ url: "https://www.linkedin.com/jobs/search/?keywords=analyst", doc }),
    "4382412003",
  );
});

test("resolves job_id from DOM attributes fallback", () => {
  const doc = createDocument({
    "[data-job-id]": [createNode({ "data-job-id": "4411111111" })],
  });

  assert.equal(
    helpers.resolveJobId({ url: "https://www.linkedin.com/jobs/search/?keywords=analyst", doc }),
    "4411111111",
  );
});

test("builds canonical link from job_id", () => {
  assert.equal(
    helpers.buildCanonicalJobLink("4421695645"),
    "https://www.linkedin.com/jobs/view/4421695645",
  );
});

test("generates stable vacancy key from canonical link", () => {
  assert.equal(
    helpers.buildVacancyKey("https://www.linkedin.com/jobs/view/4421695645/?tracking=abc"),
    "linkedin:https://www.linkedin.com/jobs/view/4421695645",
  );
});

test("marks vacancy as unsavable when no stable job_id exists", () => {
  const identity = helpers.resolveVacancyIdentity(
    "https://www.linkedin.com/jobs/search/?keywords=analyst"
  );

  assert.equal(identity.context, "job_search_active");
  assert.equal(identity.jobId, null);
  assert.equal(identity.canSave, false);
  assert.equal(helpers.canSaveVacancy(identity), false);
});

test("removes 'Acerca del empleo' at the start", () => {
  assert.equal(
    helpers.normalizeDescription("Acerca del empleo\nBuscamos una persona con experiencia en analitica."),
    "Buscamos una persona con experiencia en analitica.",
  );
});

test("removes trailing '... más' and variants at the end", () => {
  assert.equal(
    helpers.normalizeDescription("Descripcion de la vacante...\n... más"),
    "Descripcion de la vacante...",
  );
  assert.equal(
    helpers.normalizeDescription("Descripcion completa del rol Ver más"),
    "Descripcion completa del rol",
  );
});

test("preserves bullets and real content while reducing excessive newlines", () => {
  assert.equal(
    helpers.normalizeDescription("Acerca del empleo\n\n- SQL\n- Python\n\n\n- ETL\n... más"),
    "- SQL\n- Python\n\n- ETL",
  );
});

test("does not change normal descriptions", () => {
  const text = "Responsabilidades principales\n- Analizar datos\n- Presentar hallazgos";
  assert.equal(helpers.normalizeDescription(text), text);
});

test("returns empty string for empty description input", () => {
  assert.equal(helpers.normalizeDescription("   "), "");
  assert.equal(helpers.normalizeDescription(null), "");
});

test("structured extraction separates headings and paragraphs in Search Panel content", () => {
  const container = element(
    "div",
    element("h2", textNode("Propósito del cargo")),
    element("p", textNode("Participar y gestionar iniciativas de analitica.")),
    element("h3", textNode("Educación")),
    element("p", textNode("Pregrado en ingenieria o carreras afines."))
  );

  assert.equal(
    helpers.extractStructuredDescriptionText(container),
    [
      "Propósito del cargo",
      "Participar y gestionar iniciativas de analitica.",
      "Educación",
      "Pregrado en ingenieria o carreras afines.",
    ].join("\n\n"),
  );
});

test("structured extraction preserves list-style lines", () => {
  const container = element(
    "div",
    element("h3", textNode("Conocimientos Técnicos")),
    element(
      "ul",
      element("li", textNode("Transformación de datos")),
      element("li", textNode("Consultas con SQL")),
      element("li", textNode("Bases de datos"))
    )
  );

  assert.equal(
    helpers.extractStructuredDescriptionText(container),
    [
      "Conocimientos Técnicos",
      "- Transformación de datos",
      "- Consultas con SQL",
      "- Bases de datos",
    ].join("\n\n"),
  );
});

test("structured extraction does not duplicate nested text", () => {
  const container = element(
    "div",
    element(
      "section",
      element("h3", textNode("Competencias")),
      element(
        "div",
        element("p", textNode("Pensamiento analitico.")),
        element("p", textNode("Trabajo colaborativo."))
      )
    )
  );

  assert.equal(
    helpers.extractStructuredDescriptionText(container),
    [
      "Competencias",
      "Pensamiento analitico.",
      "Trabajo colaborativo.",
    ].join("\n\n"),
  );
});

test("structured extraction rejects global LinkedIn noise blocks", () => {
  const noisyContainer = element(
    "div",
    element("div", textNode("Inicio Mi red Empleos Mensajes")),
    element("div", textNode("Premium")),
    element("div", textNode("Seleccionar idioma")),
    element("div", textNode("LinkedIn Corporation")),
  );

  assert.equal(helpers.extractStructuredDescriptionText(noisyContainer), "");
});
