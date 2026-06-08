(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  root.LinkedInJobHelpers = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const LINKEDIN_HOST_RE = /(^|\.)linkedin\.com$/i;
  const JOB_VIEW_RE = /^\/jobs\/view\/(\d+)(?:\/|$)/i;
  const JOB_SEARCH_RE = /^\/jobs\/search(?:\/|$)/i;
  const JOB_SEARCH_RESULTS_RE = /^\/jobs\/search-results(?:\/|$)/i;
  const JOB_LINK_RE = /\/jobs\/view\/(\d+)(?:\/|$)/i;
  const MIN_JOB_ID_LENGTH = 6;

  function parseUrl(url) {
    if (!url) return null;
    try {
      return new URL(url);
    } catch (_) {
      return null;
    }
  }

  function isLinkedInHost(hostname) {
    return LINKEDIN_HOST_RE.test(hostname || "");
  }

  function normalizeJobId(value) {
    const raw = String(value || "").trim();
    if (!raw) return null;

    const digits = raw.match(/\b(\d{6,})\b/);
    if (!digits) return null;

    return digits[1].length >= MIN_JOB_ID_LENGTH ? digits[1] : null;
  }

  function detectLinkedInContext(url) {
    const parsed = parseUrl(url);
    if (!parsed || !isLinkedInHost(parsed.hostname)) {
      return "unsupported";
    }

    if (JOB_VIEW_RE.test(parsed.pathname || "")) {
      return "job_view";
    }

    if (JOB_SEARCH_RE.test(parsed.pathname || "") || JOB_SEARCH_RESULTS_RE.test(parsed.pathname || "")) {
      return "job_search_active";
    }

    return "unsupported";
  }

  function resolveJobIdFromViewUrl(url) {
    const parsed = parseUrl(url);
    if (!parsed) return null;

    const match = (parsed.pathname || "").match(JOB_VIEW_RE);
    return normalizeJobId(match ? match[1] : null);
  }

  function resolveJobIdFromSearchParams(url) {
    const parsed = parseUrl(url);
    if (!parsed) return null;

    return (
      normalizeJobId(parsed.searchParams.get("currentJobId")) ||
      normalizeJobId(parsed.searchParams.get("jobId"))
    );
  }

  function resolveJobIdFromHref(href) {
    if (!href) return null;
    const match = String(href).match(JOB_LINK_RE);
    return normalizeJobId(match ? match[1] : null);
  }

  function queryAll(doc, selector) {
    if (!doc || typeof doc.querySelectorAll !== "function") {
      return [];
    }
    try {
      return Array.from(doc.querySelectorAll(selector));
    } catch (_) {
      return [];
    }
  }

  function readAttr(node, attrName) {
    if (!node) return null;
    if (typeof node.getAttribute === "function") {
      return node.getAttribute(attrName);
    }
    return node[attrName] || null;
  }

  function resolveJobIdFromNode(node) {
    if (!node) return null;

    const attributeCandidates = [
      readAttr(node, "data-job-id"),
      readAttr(node, "data-occludable-job-id"),
      readAttr(node, "data-entity-urn"),
      node.dataset?.jobId,
      node.dataset?.occludableJobId,
      node.href,
    ];

    for (const candidate of attributeCandidates) {
      const resolved = resolveJobIdFromHref(candidate) || normalizeJobId(candidate);
      if (resolved) return resolved;
    }

    return null;
  }

  function resolveJobIdFromDocument(doc) {
    const prioritizedSelectors = [
      "[aria-current='true'][data-job-id]",
      "[aria-current='true'][data-occludable-job-id]",
      "[aria-current='true'][data-entity-urn]",
      "[aria-current='true'] a[href*='/jobs/view/']",
      "[class*='active'][data-job-id]",
      "[class*='active'][data-occludable-job-id]",
      "[class*='active'][data-entity-urn]",
      "[class*='active'] a[href*='/jobs/view/']",
      "[data-job-id]",
      "[data-occludable-job-id]",
      "[data-entity-urn]",
      "a[href*='/jobs/view/']",
    ];

    for (const selector of prioritizedSelectors) {
      for (const node of queryAll(doc, selector)) {
        const jobId = resolveJobIdFromNode(node);
        if (jobId) return jobId;
      }
    }

    return null;
  }

  function resolveJobId(input) {
    const url = typeof input === "string" ? input : input?.url;
    const doc = typeof input === "string" ? null : input?.doc;

    return (
      resolveJobIdFromViewUrl(url) ||
      resolveJobIdFromSearchParams(url) ||
      resolveJobIdFromDocument(doc)
    );
  }

  function buildCanonicalJobLink(jobId) {
    const normalized = normalizeJobId(jobId);
    if (!normalized) return null;
    return `https://www.linkedin.com/jobs/view/${normalized}`;
  }

  function normalizeLink(link) {
    if (!link) return null;
    const parsed = parseUrl(link);
    if (!parsed) {
      const trimmed = String(link).trim();
      return trimmed ? trimmed.replace(/[?#].*$/, "").replace(/\/+$/, "") : null;
    }

    parsed.search = "";
    parsed.hash = "";

    const normalized = parsed.toString().replace(/\/+$/, "");
    return normalized || null;
  }

  function buildVacancyKey(link) {
    const normalizedLink = normalizeLink(link);
    return normalizedLink ? `linkedin:${normalizedLink}` : null;
  }

  function canSaveVacancy(identity) {
    return Boolean(identity?.jobId && identity?.canonicalLink && identity?.vacancyKey);
  }

  function resolveVacancyIdentity(input) {
    const url = typeof input === "string" ? input : input?.url;
    const doc = typeof input === "string" ? null : input?.doc;
    const context = detectLinkedInContext(url);
    const jobId = resolveJobId({ url, doc });
    const canonicalLink = buildCanonicalJobLink(jobId);
    const vacancyKey = buildVacancyKey(canonicalLink);

    return {
      context,
      jobId,
      canonicalLink,
      vacancyKey,
      supported: context !== "unsupported",
      canSave: canSaveVacancy({ jobId, canonicalLink, vacancyKey }),
    };
  }

  return {
    buildCanonicalJobLink,
    buildVacancyKey,
    canSaveVacancy,
    detectLinkedInContext,
    normalizeJobId,
    normalizeLink,
    resolveJobId,
    resolveJobIdFromDocument,
    resolveJobIdFromHref,
    resolveJobIdFromSearchParams,
    resolveJobIdFromViewUrl,
    resolveVacancyIdentity,
  };
});
