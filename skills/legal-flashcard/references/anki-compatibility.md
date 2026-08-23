# Anki-like compatibility boundary

The local Skill Room index was queried read-only. It contains the installed `flashcards` skill from `CSlawyer1985/claude-for-legal-ZH`, whose useful generation heuristics are: one concept per card, source citation, split long answers, cloze only for a short target, and prefer fewer sourced cards over many guesses. No separate Anki skill was present in the local SQL cache.

Reuse those content heuristics only. DAMO owns portable Markdown semantics; the skill does not copy Anki note IDs, card IDs, deck names, due dates, intervals, review logs, suspend/bury state, or device state. `custom-dm-card-kind` is the semantic note/card kind; `custom-dm-card-renderer` remains the host container.

