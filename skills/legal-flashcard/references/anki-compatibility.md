# External flashcard-design boundary

The external skill search was refreshed against dedicated creators rather than Anki runtime tools:

- `anthropics/claude-for-legal@flashcards` treats one concept as one card, splits paragraph answers, cites the source, and prefers fewer verified cards over padded output.
- `terkelg/anki-markdown@anki` requires atomic, simple, unambiguous prompts, one unique specific answer, short backs, preview before acceptance, and distinct retrieval directions for useful variants.
- `blazewicz/claude-flashcards@flashcard-creator` usefully selects among direct recall, fill-in-the-blank, application, mistake-correction, and mnemonic forms according to the material.

[card-design.md](card-design.md) is the local source of truth for the adapted rules. DAMO keeps the atomicity, prompt specificity, material-driven card-type choice, contextual hints, and preview step. It prunes AnkiConnect operations, `Front`/`Back` labels, fixed bulk targets, mandatory variant multiplication, deck names, note IDs, scheduling fields, review state, and conversion scripts.

Completion criterion: an external heuristic changes recall quality without changing DAMO fields, IAL boundaries, renderer semantics, or the prohibition on runtime state.

