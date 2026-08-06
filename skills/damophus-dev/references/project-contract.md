# Damophus Project Contract

Use the repository's current paths and exports as the source of truth; this document records boundaries, not a replacement directory map.

| Boundary | Owns | Does not own |
| --- | --- | --- |
| Question Markdown + IAL | Stable question identity, type, options, answer, topic, solution boundary | Attempts, statistics, device/session state |
| Portable TypeScript core | Parsing, validation, answer checking, scoring, state transitions, aggregation, recovery contracts | SiYuan kernel calls, DOM, Svelte state |
| SiYuan adapters | Kernel requests, blocks, Attribute Views, Riff, plugin data storage | Portable domain rules |
| Exam core | Blueprint validation, frozen queue, timer state, scoring, submission plan | Rendering and kernel persistence details |
| Assembly | Catalog selection, deduplication, quotas, balanced/random selection, frozen sets | Exam UI and question content mutation |
| Svelte UI | Rendering, user input, navigation, transient view state | Durable business logic and persistence rules |

Preserve stable `custom-qb-*` identities and solution boundaries. Attempt history is append-only and statistics must remain rebuildable. A new managed field requires a versioned migration and a focused repair test.
