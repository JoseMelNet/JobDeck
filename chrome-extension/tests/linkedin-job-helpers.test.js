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

function createTextElement(text) {
  return {
    innerText: text,
    textContent: text,
  };
}

function createRootWithTexts(textsBySelector) {
  return {
    querySelectorAll(selector) {
      return (textsBySelector[selector] || []).map((text) => createTextElement(text));
    },
  };
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

test("extractLegacyDescriptionFrom returns the longest p/span text inside the root", () => {
  const shortText = "x".repeat(520);
  const longText = "y".repeat(900);
  const root = createRootWithTexts({
    "p, span": [shortText, longText],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), longText);
});

test("extractLegacyDescriptionFrom ignores texts shorter than 500 chars", () => {
  const root = createRootWithTexts({
    "p, span": ["corto", "a".repeat(499)],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), "");
});

test("extractLegacyDescriptionFrom ignores texts longer than 8000 chars", () => {
  const validText = "a".repeat(700);
  const tooLongText = "b".repeat(8001);
  const root = createRootWithTexts({
    "p, span": [tooLongText, validText],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), validText);
});

test("extractLegacyDescriptionFrom applies normalizeDescription", () => {
  const root = createRootWithTexts({
    "p, span": ["Acerca del empleo\n" + "a".repeat(650) + "\n... más"],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), "a".repeat(650));
});

test("extractLegacyDescriptionFrom only uses text inside the provided root", () => {
  const root = createRootWithTexts({
    "p, span": ["Contenido local " + "a".repeat(650)],
  });
  const globalNoise = createRootWithTexts({
    "p, span": ["Contenido global " + "b".repeat(1200)],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), "Contenido local " + "a".repeat(650));
  assert.notEqual(
    helpers.extractLegacyDescriptionFrom(root),
    helpers.extractLegacyDescriptionFrom(globalNoise),
  );
});

test("extractLegacyDescriptionFrom does not accept global LinkedIn noise when root has no valid description", () => {
  const root = createRootWithTexts({
    "p, span": [
      "Inicio Mi red Empleos Mensajes",
      "Premium",
      "Seleccionar idioma",
      "LinkedIn Corporation",
    ],
  });

  assert.equal(helpers.extractLegacyDescriptionFrom(root), "");
});
