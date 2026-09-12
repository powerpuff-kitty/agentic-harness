# Layout standard

## Read reference boards correctly

A two-column image containing a very long website often shows the *continuation*
of one vertical page, not two simultaneous website columns. A 2-by-3 grid of brand
boards is a contact sheet of scenes, not a required six-card homepage. Transfer
hierarchy, visual rhythm and composition; do not copy the surrounding grey canvas,
logos, tiny filler text or unrelated sales features.

Useful reference patterns include an immersive image cover, an image/text split,
a short positioning statement, image-led capability tiles, a full-width identity
band, a palette/type specimen, a sequence of applications/screens and a closing
brand scene. Repetition should create continuity without making every section a
card. Alternate visual scenes with readable explanations.

## Deterministic visual vocabulary v1

`layouts.json` is authoritative for the supported names and geometry. A renderer
must reject unsupported names rather than interpret them as arbitrary CSS.

| Layout | Items | 12-column desktop spans | Typical use |
| --- | --- | --- | --- |
| full | 1 | 12 | Cover, logo stage, full screen or closing image |
| split | 2 | 6 / 6 | Before/after, related views, even pairing |
| dominant-left | 2 | 8 / 4 | Desktop screen plus mobile/detail |
| dominant-right | 2 | 4 / 8 | Explanation/detail plus dominant image |
| triptych | 3 | 4 / 4 / 4 | Workflow steps or application series |
| mosaic | 4 | 8 / 4, then 4 / 8 | A deliberate asymmetric sequence |

`purpose` describes meaning: cover, context, identity, foundations, application,
interface or workflow. It is separate from layout. A four-image mosaic does not
claim four features; the captions explain the actual content.

Settings: surface (paper/muted/ink), frame (none/line), corners (square/soft),
spacing (compact/comfortable/generous), and per-image ratio
(natural/wide/landscape/square/portrait) plus fit (contain/cover). Defaults are in
layouts.json. These are controlled options, not style strings, remote stylesheets,
user-defined class names, or executable templates. Product-specific brand colors
remain in product tokens and approved artwork; host chrome stays unchanged.

## Responsive rules

The reference implementation uses 12 columns, collapsing to one below 48rem.
Keep DOM/source order at every size. Do not reorder information with CSS, clamp
text to fixed-height boards, shrink captions to fit or require horizontal scrolling
for the case-study body. The breakpoint is a starting contract, not a guarantee of
accessible behavior; verify actual layouts at 320/360px and zoom.

Recommended host editorial settings (proposals, not measured from screenshots):
maximum content width around 80–90rem; horizontal gutters 1–4rem; internal gaps
1–1.5rem; section rhythm 3–6rem; reading measure roughly 60–70 characters. Bind
these to host spacing/layout tokens. Avoid custom spacing per project.

Use natural aspect ratio for tall UI screenshots and informative boards. Contain
screenshots and logos; never crop away functionality or the mark. Cover cropping
is only allowed for photographs/artwork and requires a chosen fixed ratio. Use
intrinsic width/height to reserve space, lazy-load below-fold images, and keep
captions/credits visible. A wide brand scene can be composed within an image, but
essential copy must remain separately accessible.

## Art direction is an independent choice

Possible editorial directions include:
- soft product: rounded specimen frames, airy cards, restrained shadows;
- studio editorial: sharp frames, asymmetric grids, strong image/text contrast;
- expressive brand: large logo/type scenes, repeated motif, controlled color fields;
- technical product: clear diagrams, code/API examples, precise annotations.

They are guidance, not inferred personality attributes or automatic themes. Do not
force every project into one of the reference palettes. More than one direction
can use the same full/split/triptych/mosaic layouts. A project-level brand does not
require a global layout fork.

## Access and motion

No automatic carousel or mandatory animation in a visual narrative. Optional
motion has a static fallback and obeys reduced motion. Informative images require
meaningful alternative text; color values have visible names/roles. Make image
failures understandable without discarding captions. Keep focus/contrast and
keyboard verification as release evidence, not an untested claim.
