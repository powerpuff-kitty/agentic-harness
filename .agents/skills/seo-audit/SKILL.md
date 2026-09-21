---
name: seo-audit
description: "Audit public websites and web applications for technical SEO, AEO/GEO retrieval readiness, crawlability, indexability, rendering, canonical URLs, hreflang, sitemaps, structured data, internal-link discoverability, and programmatic-page quality. Use when search visibility, indexing, crawler access, AI-search discovery, or SSR/prerender-for-SEO is explicitly requested. Do not use for general marketing copy/keyword strategy, broad codebase health, or performance profiling alone."
---
# SEO Audit

## Objective

Assess whether intended public pages can be discovered, crawled, understood, canonically identified, and verified by search and answer-engine retrieval systems, using source, built-artifact, deployed HTTP, and external search evidence without inventing ranking factors.

## Inputs

Required: target repository/site and public surface or routes in scope. Optional: production origin(s), sitemap(s), search-console/webmaster evidence, crawler logs, route inventory, rendering architecture, target locales, structured-data requirements, and approved publication/indexability policy.

## Context

Start with project-owned public URL, publication, privacy, localization, deployment, and rendering truth. Inspect only the route/build/server/middleware/metadata code needed to establish crawl behavior. When available, use the canonical Harness search-visibility rules (for example `pattern/search-visibility/1`) as stable finding semantics; the skill remains usable without a CLI or installed registry.

Keep four evidence classes distinct:

1. **source** — code/configuration expresses intended behavior;
2. **build artifact** — generated HTML/sitemap/assets actually contain it;
3. **deployed HTTP** — production status, headers, redirects and response HTML;
4. **external search** — search-console, webmaster, crawler/referral or citation evidence.

A stronger evidence class does not retroactively prove checks that were not performed.

## Procedure

1. Establish public hosts, route classes, canonical URL intent, locales, publication gates, preview/staging policy, and which search/AI providers matter. Do not infer that every reachable application route should be indexed.
2. Inventory robots.txt, meta/X-Robots-Tag directives, authentication boundaries, status codes, redirects, canonical links and sitemaps. Keep **crawl permission** distinct from **indexing directives**; a robots block is not itself proof of noindex.
3. Inspect representative response HTML for home, entity/category, detail/listing, localized, pagination/filter, withdrawn/not-found and preview routes. Record whether essential title, descriptive content, links and metadata exist before client execution. If only source code is available, report response behavior as `not_checked`.
4. Determine the rendering model per route class (CSR, SSR, SSG/prerender or hybrid) and freshness requirements. A JavaScript framework is not an SEO defect by itself. Recommend migration only when evidence shows a concrete rendering, cache/revalidation, route-scale, status-code or maintenance gap that cannot be addressed proportionately in the current architecture.
5. Compare canonical URLs, redirects, sitemap entries and dominant internal links for consistency. Identify duplicates, redirect chains, orphan pages, soft 404s, query/facet explosions and public routes that are missing from intentional discovery paths.
6. For localized pages, verify only genuine translations are advertised, alternate declarations are reciprocal where required, self references are present, and x-default/canonical behavior matches project policy. Do not fabricate locale variants to complete a matrix.
7. Validate structured data against visible supported facts and lifecycle state. Syntax or schema presence is not evidence of eligibility or ranking; never manufacture ratings, prices, availability, identity, location precision or reviews.
8. Evaluate programmatic/entity pages for unique user value: canonical identity, real inventory/data/content, freshness/provenance, useful internal links, and meaningful actions. Treat thin combinations and arbitrary filter URLs as candidates for suppression/canonicalization/noindex rather than mass publication.
9. For AI-search discovery, inspect only provider-documented crawler/directive behavior and target-provider access. Distinguish search/discovery crawlers from training crawlers where the provider documents separate agents. Check edge/WAF behavior when deployed evidence is available. Do not treat `llms.txt` or any emerging convention as universally required without authoritative evidence.
10. Use Search Console, Bing/Webmaster, server logs, referral attribution, field Core Web Vitals or citation reports only when actually accessible. Report the time window, population/sample and provider. Source correctness does not prove indexing; crawler eligibility does not prove citation; lab performance does not prove field CWV.
11. Prioritize confirmed defects by reach and search-surface impact. Separate deterministic defects, risks/heuristics, opportunities and `not_checked`. Route measured runtime bottlenecks to `performance-audit`, positioning/copy strategy to `marketing`, and broad repository health to `codebase-audit`.
12. When implementation is authorized, prefer the smallest reversible fix, preserve publication/privacy controls, and re-check the same evidence class. Framework migrations, domain/subdomain consolidation and large URL changes require redirect/canonical compatibility plans and explicit rollout evidence.

## Output

Return:

- repository/site/revision and production origins reviewed;
- intended indexable route classes and excluded/private classes;
- evidence coverage by **source / build artifact / deployed HTTP / external search**;
- prioritized findings with stable rule ID when available, severity, evidence class, exact route/file/header evidence, impact, and smallest remediation;
- rendering assessment that may explicitly conclude **no framework migration required**;
- AI-search/provider findings attributed to the relevant provider;
- verification steps for each fix and a short list of remaining `not_checked` areas.

Do not produce a synthetic SEO score unless the project supplied an accepted rubric. Do not report ranking, traffic, indexing, citation or Core Web Vitals claims without matching external/deployed evidence.

## Completion

The audit distinguishes crawlability from indexability, source intent from deployed behavior, and conventional search from provider-specific AI retrieval. Intended public route classes are sampled or marked untested, private/preview boundaries remain protected, structured-data claims are grounded in visible facts, framework recommendations name a concrete capability gap, and all unmeasured search outcomes remain explicit.
