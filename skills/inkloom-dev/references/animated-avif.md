# Animated AVIF publication

Publish an animated AVIF companion for every existing semantic Remotion scene after page-still QA passes. This is additive to the original full-length video and replaces only the retired static final-frame publishing flow. Keep the full video, its encoding and publication behavior, and the existing pagination/deep-link contract unchanged.

## Asset contract

1. Every `RemotionScene` must have a stable descriptive kebab-case `id`, and every `RemotionDeck` call must provide its stable `animationId`. File names derive from these IDs, never from page numbers or mutable titles.
2. Run `pnpm animation:publish-avif <animation-id>` for each changed animation. After a completed batch, run `pnpm animation:publish-avif` with no IDs so automatic discovery publishes every animation.
3. Each scene is rendered from `start` through the stable frame determined by `previewEndTrimFrames`. Do not include the authored exit tail.
4. Default to q45, which maps to AV1 CRF 35, at 2560x1440, target 15 fps, and loop count 1. Permit an explicit user-requested quality override through q0 through q100, mapped to AV1 CRF 63 through 0, but never silently change the default. The file itself plays once and stops on its final stable teaching frame. Do not encode infinite looping into the asset.
5. Publish to `public/animation-avif/<animation-id>/<scene-id>.avif` and write `manifest.json` beside the scene files. The manifest must record quality, dimensions, source and target fps, loop count, exact scene IDs/titles/frame ranges/frame counts/durations/file sizes, and total bytes.
6. Treat the public path as the durable Markdown contract: `https://inkloomer.github.io/inkloom/animation-avif/<animation-id>/<scene-id>.avif`. Keep it stable across title edits and page reordering.
7. Keep every file below GitHub's individual-file limit and review the batch total before committing. If an asset becomes too large, reduce authored duration or redesign unnecessary motion before lowering readability.
8. Do not render per-scene MP4/WebM files, replace the original full video, or rewrite `SCENES` to fit AVIF publication. Derive one AVIF from each existing scene boundary and keep the scene number, semantic ID, order, `start`, `duration`, and deep-link behavior intact.

## Website contract

1. The shared player must expose visible Video and AVIF tabs and persist the selected media mode in `localStorage` across routes and sessions.
2. Scene navigation and semantic `?scene=` deep links must select the matching video range and AVIF file.
3. The AVIF surface must replay on demand and offer an explicit infinite-loop control by reloading the once-playing asset. Do not claim native `<img>` pause support.
4. Provide one-click copy actions for the exact Markdown image syntax and the image itself. Prefer `ClipboardItem` with `image/avif`; when the browser cannot write AVIF binary, copy a rich-text `<img>` reference plus the production URL and report the fallback honestly.
5. Publish `public/tools/siyuan-animated-image-player.js`. Keep its top-level format list and booleans configurable for replay-button visibility, loop-button visibility, replay on hover, and replay when a large-image viewer opens. Support WebP, GIF, AVIF, and explicit `.apng` assets by reloading the native `<img>` for replay and using manifest timing for optional infinite looping. Do not add pause/resume, `ImageDecoder`, or Canvas playback. Never wrap, hide, or reparent the original image; place controls in a non-flow overlay that follows the image so SiYuan's native width adjustment and large-image viewer remain intact.

## Rendering and validation

1. Use Remotion's renderer to obtain source frames and FFmpeg `libaom-av1` with the AVIF muxer for q45 output. Re-open every generated file with FFprobe and an independent AVIF-capable reader, verifying its frame count, canvas dimensions, frame timing, and loop count.
2. On Windows, keep `renderFrames` concurrency at 1. Give each scene its own renderer-browser lifetime, close that browser before encoding, and run FFmpeg with one thread so Chrome and animated-AVIF encoding do not overlap their memory peaks. Remotion 4 is more reliable under Node 22 than Node 24 when native compositor failures occur. An `ERR_INSUFFICIENT_RESOURCES` or Windows commitment-limit exit is an environment failure: free virtual memory without terminating user applications, then rerun the affected animation.
3. Inspect at least the first, middle, and final coalesced frames of every scene at native output resolution. Reject blank frames, clipped content, smeared small text, broken thin connectors, color hierarchy changes, or a final frame that enters the authored exit.
4. Build the site and test a narrow and wide viewport. Verify video/AVIF switching, localStorage restoration after reload and across routes, scene changes, replay, infinite loop, copy Markdown, copy image behavior, and the SiYuan script download/copy action.
5. After deployment, open the production page and direct AVIF URLs. Do not report the animation uploaded while any asset, manifest, copy action, or production route remains unverified.
