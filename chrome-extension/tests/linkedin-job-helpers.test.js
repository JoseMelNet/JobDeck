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
