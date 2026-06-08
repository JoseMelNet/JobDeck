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
  const BLOCK_TAGS = new Set([
    "article", "div", "header", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "ol", "p", "section", "ul",
  ]);
  const LIST_TAGS = new Set(["ul", "ol"]);
  const INLINE_TEXT_TAGS = new Set([
    "a", "b", "em", "i", "small", "span", "strong", "u",
  ]);
  const IGNORED_TAGS = new Set([
    "button", "footer", "nav", "script", "style", "svg",
  ]);
  const LINKEDIN_NOISE_PATTERNS = [
    "inicio mi red empleos mensajes",
    "linkedin corporation",
    "seleccionar idioma",
    "premium",
  ];

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

  function collapseWhitespace(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function getNodeTagName(node) {
    return String(node?.tagName || node?.nodeName || "").toLowerCase();
  }

  function getNodeType(node) {
    if (!node) return 0;
    if (typeof node.nodeType === "number") return node.nodeType;
    if (node.childNodes || node.tagName || node.nodeName) return 1;
    return 3;
  }

  function getChildNodes(node) {
    if (!node) return [];
    if (Array.isArray(node.childNodes)) return node.childNodes;
    if (typeof node.childNodes?.length === "number") return Array.from(node.childNodes);
    return [];
  }

  function getNodeText(node) {
    if (!node) return "";
    if (getNodeType(node) === 3) {
      return String(node.textContent || node.nodeValue || "");
    }
    return String(node.innerText || node.textContent || "");
  }

  function isLikelyLinkedInNoise(text) {
    const normalized = collapseWhitespace(text).toLowerCase();
    if (!normalized) return false;

    const matches = LINKEDIN_NOISE_PATTERNS.filter((pattern) => normalized.includes(pattern));
    if (matches.length >= 2) return true;
    if (matches.length === 1 && normalized.length <= 120) return true;
    return false;
  }

  function uniquePush(target, value) {
    if (!value) return;
    if (!target.includes(value)) {
      target.push(value);
    }
  }

  function inlineTextFromNode(node) {
    if (!node) return "";

    const nodeType = getNodeType(node);
    if (nodeType === 3) {
      return String(node.textContent || node.nodeValue || "");
    }

    const tag = getNodeTagName(node);
    if (IGNORED_TAGS.has(tag)) return "";
    if (tag === "br") return "\n";

    const children = getChildNodes(node);
    if (!children.length) {
      return getNodeText(node);
    }

    let text = "";
    for (const child of children) {
      const childTag = getNodeTagName(child);
      if (LIST_TAGS.has(childTag) || BLOCK_TAGS.has(childTag)) {
        continue;
      }
      const childText = inlineTextFromNode(child);
      if (childText === "\n") {
        text += "\n";
      } else if (childText) {
        text += childText;
      }
    }

    return text || getNodeText(node);
  }

  function structuredBlocksFromNode(node) {
    if (!node) return [];

    const nodeType = getNodeType(node);
    if (nodeType === 3) {
      const text = collapseWhitespace(node.textContent || node.nodeValue || "");
      return text ? [text] : [];
    }

    const tag = getNodeTagName(node);
    if (IGNORED_TAGS.has(tag)) return [];
    if (tag === "br") return [];

    const children = getChildNodes(node);

    if (LIST_TAGS.has(tag)) {
      const blocks = [];
      for (const child of children) {
        const childTag = getNodeTagName(child);
        if (childTag === "li") {
          const itemText = collapseWhitespace(inlineTextFromNode(child));
          if (!itemText || isLikelyLinkedInNoise(itemText)) continue;
          uniquePush(blocks, itemText.startsWith("-") ? itemText : `- ${itemText}`);
          continue;
        }
        for (const block of structuredBlocksFromNode(child)) {
          if (!isLikelyLinkedInNoise(block)) uniquePush(blocks, block);
        }
      }
      return blocks;
    }

    if (tag === "li") {
      const itemText = collapseWhitespace(inlineTextFromNode(node));
      if (!itemText || isLikelyLinkedInNoise(itemText)) return [];
      return [itemText.startsWith("-") ? itemText : `- ${itemText}`];
    }

    const childBlockTags = children
      .map((child) => getNodeTagName(child))
      .filter((childTag) => BLOCK_TAGS.has(childTag) || childTag === "br");

    if (!childBlockTags.length) {
      const text = collapseWhitespace(inlineTextFromNode(node));
      if (!text || isLikelyLinkedInNoise(text)) return [];
      return [text];
    }

    const blocks = [];
    let inlineBuffer = "";

    const flushInlineBuffer = () => {
      const text = collapseWhitespace(inlineBuffer);
      inlineBuffer = "";
      if (!text || isLikelyLinkedInNoise(text)) return;
      uniquePush(blocks, text);
    };

    for (const child of children) {
      const childType = getNodeType(child);
      const childTag = getNodeTagName(child);

      if (childType === 3) {
        inlineBuffer += ` ${child.textContent || child.nodeValue || ""}`;
        continue;
      }

      if (IGNORED_TAGS.has(childTag)) continue;

      if (childTag === "br") {
        inlineBuffer += "\n";
        continue;
      }

      if (BLOCK_TAGS.has(childTag) || LIST_TAGS.has(childTag)) {
        flushInlineBuffer();
        for (const block of structuredBlocksFromNode(child)) {
          if (!isLikelyLinkedInNoise(block)) uniquePush(blocks, block);
        }
        continue;
      }

      if (INLINE_TEXT_TAGS.has(childTag) || !childTag) {
        inlineBuffer += ` ${inlineTextFromNode(child)}`;
      }
    }

    flushInlineBuffer();

    if (!blocks.length) {
      const text = collapseWhitespace(getNodeText(node));
      if (!text || isLikelyLinkedInNoise(text)) return [];
      return [text];
    }

    return blocks;
  }

  function extractStructuredDescriptionText(root) {
    if (!root) return "";

    const blocks = structuredBlocksFromNode(root)
      .map((block) => collapseWhitespace(block))
      .filter(Boolean)
      .filter((block) => !isLikelyLinkedInNoise(block));

    if (!blocks.length) return "";

    return blocks.join("\n\n");
  }

  function normalizeDescription(text) {
    if (text == null) return "";

    let normalized = String(text).replace(/\r\n?/g, "\n").trim();
    if (!normalized) return "";

    normalized = normalized.replace(/^Acerca del empleo\b(?:\s*:\s*|\s*\n+|\s+)/i, "");
    normalized = normalized.replace(/\n[ \t]+\n/g, "\n\n");
    normalized = normalized
      .split("\n")
      .map((line) => line.trimEnd())
      .join("\n");
    normalized = normalized.replace(/\n{3,}/g, "\n\n");
    normalized = normalized.replace(/(?:\u2026|\.\.\.)\s*m[aá]s$/i, "");
    normalized = normalized.replace(/Ver m[aá]s$/i, "");

    return normalized.trim();
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
    extractStructuredDescriptionText,
    isLikelyLinkedInNoise,
    normalizeDescription,
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
