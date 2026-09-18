# Design intent

The scenario uses a quiet, compact reading list with one primary add action, a labelled all/unread filter and clearly named read-status controls. Decoration must not compete with titles or validation messages.

The future `src/styles/tokens.css` owns semantic foreground, background, muted, border, error and focus roles plus spacing and type scales. Concrete values are unresolved until selected and contrast-checked; this document does not define a competing token implementation.

Future shared controls are a labelled text field, primary button, filter and read-status toggle. Their contracts include accessible names, keyboard use, visible focus and error association. Native controls are acceptable until shared wrappers offer a useful contract. Required states include empty list, empty filter, valid form, invalid title, invalid link and populated list.

Preserve form values after rejection; do not indicate errors or read status through color alone. Wrap long titles and links. Do not introduce animation as the sole status signal. Verify focus recovery from PRODUCT.md and the narrow viewport target once implementation exists.

No components, tokens, screenshots or accessibility results exist yet. A filled design document establishes scenario intent only.
