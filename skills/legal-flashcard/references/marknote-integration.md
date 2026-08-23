# MarkNote adapter for dedicated cards

Read this file only in dedicated-card mode. Before using it, invoke the separately registered `legal-marknote` skill by name; skill deployments are not required to be sibling directories. Do not load it on the ordinary route; ordinary mode delegates its complete presentation contract to MarkNote without loading card rules.

## Card-sized adapter

- Reuse MarkNote's source fidelity, semantic hierarchy, bold-first style syntax, and meaningful highlight rules. Read the `Plan semantic colors`, `Accuracy`, and `Rich visual contract` sections of `legal-marknote/SKILL.md`; consult its detailed guide only when a card uses a table, Callout, image, or other advanced structure.
- When a source note exists, [style-inheritance.md](style-inheritance.md) is the authority for the actual palette and fragments: copy provider-scoped source styles instead of constructing a new deck-wide color vocabulary.
- A genuinely plain source range may produce a plain card. Never append a detached or recolored word merely to satisfy visual density.
- A card deck is not a full MarkNote chapter. Do not require a Mermaid diagram, a summary table, four structural families, four style families, an emoji, or three background anchors merely to make a deck pass.
- Keep `basic` question roots free of `==...==` reading highlights. Leave generated question wording plain; preserve a styled legal object only when its complete styled fragment is inherited from the corresponding source range.
- Use `==...==` only for a `cloze` deletion target or for the explicit retrieval target of a `mnemonic` card. A mnemonic root is a cue card, not a disguised question: name the recall subject in the root, such as `- 立法审查主体口诀：==...==` or `- 备案顺序口诀：==...==`, then show each source sentence's contributing character or segment and the assembled result as separately highlighted child items. A bare `- 口诀：...` label is insufficient.
- A mnemonic card may highlight its complete口诀 even when it exceeds MarkNote's ordinary six-character highlight limit. This exception applies only to the complete mnemonic phrase and its auditable mapping; do not add a question label merely to justify the highlight.

Completion criterion: source-derived styles remain exact and provider-scoped, generated question scaffolding stays plain, no whole answer sentence is colored, mnemonic mappings remain auditable, and no full-document richness requirement was added solely for decoration.
