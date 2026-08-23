# MarkNote adapter for dedicated cards

Read this file only in dedicated-card mode. Before using it, invoke the separately registered `legal-marknote` skill by name; skill deployments are not required to be sibling directories. Do not load it on the ordinary route; ordinary mode delegates its complete presentation contract to MarkNote without loading card rules.

## Card-sized subset

- Reuse MarkNote's source fidelity, semantic hierarchy, short bold color-anchor syntax, stable subject/color mapping, and meaningful highlight rules. Read the `Plan semantic colors`, `Accuracy`, and `Rich visual contract` sections of `legal-marknote/SKILL.md`; consult its detailed guide only when a card uses a table, callout, image, or other advanced structure.
- Every accepted card needs at least one purposeful `**短锚点**{: style="..."}`. Color a legal subject, object, threshold, exception, procedure, or result that participates in the recall statement. Do not append a detached colored word merely to satisfy validation.
- A card deck is not a full MarkNote chapter. Do not require a Mermaid diagram, a summary table, four structural families, four style families, an emoji, or three background anchors merely to make a deck pass.
- Keep `basic` question roots free of `==...==` reading highlights. Use only a purposeful bold semantic anchor with MarkNote color style, such as `**民主性原则**{: style="color: var(--b3-font-color10);"}`, to identify the legal object without turning the question into a cloze.
- Use `==...==` only for a `cloze` deletion target or for the explicit retrieval target of a `mnemonic` card. A mnemonic root is a cue card, not a disguised question: write `- 口诀：==...==`, then show each source sentence's contributing character or segment and the assembled result as separately highlighted child items.
- A mnemonic card may highlight its complete口诀 even when it exceeds MarkNote's ordinary six-character highlight limit. This exception applies only to the complete mnemonic phrase and its auditable mapping; do not add a question label merely to justify the highlight.

Completion criterion: every card has a valid semantic anchor, no whole answer sentence is colored, mnemonic mappings remain auditable, and no full-document richness requirement was added solely for decoration.
