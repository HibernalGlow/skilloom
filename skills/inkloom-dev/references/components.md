# InkLoom component map

Use these existing components before creating page-specific HTML. Confirm the actual import path and prop types in the repository before editing a call site.

## Metadata

- `<TagGroup>`: horizontal wrapper for metadata.
- `<Badge variant="...">`: Starlight-aligned pill tag.
- `<MoneyBadge amount="...">`: green currency tag for transaction tracking.

## Case structure

- `<CaseCard title="..." subject="..." year="...">`: factual-background highlight box.
- `<ModelCard title="..." subtitle="..." type="...">`: one legal scenario/model; normally contains `<VisualFlow>` and `<ModelAnalysis>`.
- `<ConclusionBlock type="..." label="...">`: final legal conclusion for an actor.

## Interactive legal flows

- `<VisualFlow amountA="..." action="..." relationInfo="...">`: connects briber, intermediary, and recipient.
- `<ModelAnalysis>`: responsive actor-analysis container.
- `<ActorColumn actor="..." title="...">`: vertical column for 甲, 乙, or 丙.
- `<ActionBlock class="..." icon="..." label="..." money="..." badge="...">`: action-step capsule.

`ActionBlock` may use `trigger-link-1` or `trigger-link-2`. These classes are semantic interaction hooks: matching paths in `VisualFlow` change emphasis on hover. Keep the class names stable unless the component contract and styles are updated together.

## Comparison and recall

- `<ComparisonBoard>` and `<ComparisonRail>`: responsive comparison matrices.
- `<details class="interactive-card">`: collapsible flashcard or self-test block.
- Memory challenge pages use a hidden `#memory-challenge-toggle`, a `.note-content-wrapper`, and `.answer-node` elements. The sibling selector is intentional for Notion and Obsidian compatibility.

## Layout overrides

`src/components/overrides/PageTitle.astro` owns the floating tick TOC, quick actions, copy HTML, copy iframe, and memory-toggle controls. `src/styles/custom.css` owns the widescreen override. Reuse those surfaces instead of adding a second toolbar or page-level TOC.
