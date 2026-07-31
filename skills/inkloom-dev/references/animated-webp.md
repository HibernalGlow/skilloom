# Animated WebP publication

Publish an animated WebP companion for every semantic Remotion scene after page-still QA passes. This replaces the retired static final-frame publishing flow; do not maintain both systems.

## Asset contract

1. Every `RemotionScene` must have a stable descriptive kebab-case `id`, and every `RemotionDeck` call must provide its stable `animationId`. File names derive from these IDs, never from page numbers or mutable titles.
2. Run `pnpm animation:publish-webp <animation-id>` for each changed animation. After a completed batch, run `pnpm animation:publish-webp` with no IDs so automatic discovery publishes every animation.
3. Each scene is rendered from `start` through the stable frame determined by `previewEndTrimFrames`. Do not include the authored exit tail.
4. Encode at WebP quality 45, 1280x720, target 15 fps, and loop count 1. The file itself plays once and stops on its final stable teaching frame. Do not encode infinite looping into the asset.
5. Publish to `public/animation-webp/<animation-id>/<scene-id>.webp` and write `manifest.json` beside the scene files. The manifest must record quality, dimensions, source and target fps, loop count, exact scene IDs/titles/frame ranges/frame counts/durations/file sizes, and total bytes.
6. Treat the public path as the durable Markdown contract: `https://inkloomer.github.io/inkloom/animation-webp/<animation-id>/<scene-id>.webp`. Keep it stable across title edits and page reordering.
7. Keep every file below GitHub's individual-file limit and review the batch total before committing. If an asset becomes too large, reduce authored duration or redesign unnecessary motion before lowering readability.

## Website contract

1. The shared player must expose visible Video and WebP tabs and persist the selected media mode in `localStorage` across routes and sessions.
2. Scene navigation and semantic `?scene=` deep links must select the matching video range and WebP file.
3. The WebP surface must replay on demand and offer an explicit infinite-loop control by reloading the once-playing asset. Do not claim native `<img>` pause support.
4. Provide one-click copy actions for the exact Markdown image syntax and the image itself. Prefer `ClipboardItem` with `image/webp`; when the browser cannot write WebP binary, copy a rich-text `<img>` reference plus the production URL and report the fallback honestly.
5. Publish `public/tools/siyuan-webp-player.js`. The SiYuan controller must use `ImageDecoder` and Canvas when available to provide real pause/resume, replay, and infinite loop; its fallback may provide replay and manifest-timed looping without pretending to pause.

## Rendering and validation

1. Use Remotion's renderer to obtain source frames and FFmpeg `libwebp_anim` for q45 output. Re-open every generated file with an independent WebP reader and verify its frame count, canvas dimensions, delay list, and loop count.
2. On Windows, keep `renderFrames` concurrency at 1. Give each scene its own renderer-browser lifetime, close that browser before encoding, and run FFmpeg with one thread so Chrome and animated-WebP encoding do not overlap their memory peaks. Remotion 4 is more reliable under Node 22 than Node 24 when native compositor failures occur. An `ERR_INSUFFICIENT_RESOURCES` or Windows commitment-limit exit is an environment failure: free virtual memory without terminating user applications, then rerun the affected animation.
3. Inspect at least the first, middle, and final coalesced frames of every scene at native output resolution. Reject blank frames, clipped content, smeared small text, broken thin connectors, color hierarchy changes, or a final frame that enters the authored exit.
4. Build the site and test a narrow and wide viewport. Verify video/WebP switching, localStorage restoration after reload and across routes, scene changes, replay, infinite loop, copy Markdown, copy image behavior, and the SiYuan script download/copy action.
5. After deployment, open the production page and direct WebP URLs. Do not report the animation uploaded while any asset, manifest, copy action, or production route remains unverified.
