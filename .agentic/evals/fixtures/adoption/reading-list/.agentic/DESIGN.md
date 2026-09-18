# Design

One compact column contains the session-loss notice, labelled title/link inputs, add action, All/Unread filter and entries. Read status is text plus a stable-name pressed button. Empty-list and empty-filter messages give distinct next steps. External links disclose the new-tab behavior.

`src/presentation/styles/tokens.css` owns foreground, background, muted, border, error, focus and surface colors, spacing, base/heading type and radius. Focus outlines remain visible; controls have a 44px minimum height; long titles wrap. There is no animation, icon font or external asset fetch.

Shared `TextField`, `Button` and `Filter` components own native controls. TextField connects labels and validation errors and exposes focus recovery. Button forwards event/ARIA attributes and defaults to `type=button`; add explicitly uses submit. Filter owns its label and focus method. The read toggle composes Button instead of duplicating a control implementation.

`.agentic/design-system.json` requires these controls and tokens. It declares the components and styles directories as shared roots. Raw controls and literal colors outside those roots must produce findings. This checker cannot prove token usage for every CSS value or semantic equivalence of a wrapper. No baseline exceptions are configured.

Playwright verifies keyboard add/toggle, validation preservation, focus recovery, 320px reflow and axe checks in empty, invalid and populated states. See `../VERIFICATION.md` for the actual run. These automated checks are not a complete WCAG audit; screen-reader, zoom, other browsers and visual-review evidence remain outstanding.
