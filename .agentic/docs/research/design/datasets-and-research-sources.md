# Datasets and research sources

Reviewed 2026-09-08. Licensing and redistribution must be re-verified before bundling, mirroring, or automated ingestion.

## RICO

Source: https://www.interactionmining.org/archive/rico

Structured Android UI research corpus containing screenshots, view hierarchies, interaction traces, and related metadata. It is valuable for structural search and deterministic UI research, but its age makes it unsuitable as the sole source of current visual trends.

Potential Harness use:
- local/offline structural search;
- component/layout frequency research;
- flow and interaction evidence where available;
- deterministic similarity using available layout representations.

## Enrico

Source: https://github.com/luileito/enrico

Curated RICO-derived interface dataset with semantic categories and structured annotations. It is a good lightweight first dataset for an open Harness research index.

Potential Harness use:
- category browsing;
- semantic/structural search fixtures;
- development and regression fixtures for the research-provider abstraction.

## Screen Annotation

Source: https://github.com/google-research-datasets/screen_annotation

Semantic screen-element annotations associated with RICO-derived interfaces.

Potential Harness use:
- semantic search over UI structure and content;
- mapping screen elements to normalized component/role concepts;
- evaluating deterministic extraction and classification.

## UICrit

Source: https://github.com/google-research-datasets/uicrit

Human-written critiques attached to UI examples.

Potential Harness use:
- evaluate analyzer findings against human-observed usability/aesthetic concerns;
- research which deterministic signals correlate with human critique;
- never use the dataset to create an opaque universal design-quality score.

## ScreenQA

Source: https://github.com/google-research-datasets/screen_qa

Question/answer data over UI screens.

Potential Harness use:
- optional UI-understanding evaluation for model-fit work;
- keep separate from design inspiration and deterministic design-compliance scoring.

## Free/current browsing sources

Examples reviewed:
- https://www.pttrns.com/
- https://uiguana.com/

These may be useful as current visual/flow references for users, but "free to browse" does not imply permission to scrape, mirror, index, or redistribute. Provider adapters must fail closed when programmatic rights are unknown.

## Source strategy

Harness should combine:
1. an open/local core that works without subscriptions;
2. user-provided references;
3. optional current/commercial providers through explicit adapters and user authorization.

Every provider record should carry source, review date, freshness, attribution, redistribution, indexing, retention, benchmark/training, and export permissions.
