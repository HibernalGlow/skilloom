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

## Global CSS Contract

SiYuan injects the plugin stylesheet into the host document, so every emitted selector shares an invalidation domain with the editor, toolbars, status bar, themes, and other plugins. Relational selectors such as `:has()` are forbidden in both the emitted stylesheet and runtime-injected CSS. A relation from a component to one of its descendants must instead be represented by explicit local state or a stable `data-*` attribute on the component boundary; small spacing differences may use one stable layout when no state is semantically necessary.

Keep the package validator's zero-`:has()` assertion for both `dist/index.css` and `dist/index.js`, and run it in the release workflow after the production build. Tailwind source discovery must exclude generated output and deployment/worktree copies so stale class names cannot be compiled back into a clean artifact.
