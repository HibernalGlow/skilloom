---
name: civitai-lora-upload
description: Upload local LoRA safetensors projects to Civitai with a Chrome logged-in account, local file bridge, and ScriptCat/Tampermonkey userscript. Use when batching ComfyUI LoRA projects from a finish/output folder to Civitai, selecting final checkpoints, avoiding training/cache/state files, filling Civitai model/version/post fields, recovering post image uploads, or documenting Civitai upload status.
---

# Civitai LoRA Upload

## Core Workflow

1. Use the Chrome skill for Civitai because the user's logged-in Civitai session is in Chrome.
2. Read and honor the confirmed queue and exclusions before uploading.
3. Use a local read-only bridge plus userscript instead of repeated coordinate/UI automation.
4. Create one Civitai model per project.
5. Upload only the approved final `.safetensors`.
6. Create a post with a preview image, then stop at hidden/saved unless the user explicitly confirms publishing.

Primary tool folder:

```text
D:\1Repo\Github\ComfyUI\Workflow\lora\tools\civitai-upload
```

Start or verify the bridge:

```powershell
node D:\1Repo\Github\ComfyUI\Workflow\lora\tools\civitai-upload\bridge-server.mjs
```

The bridge serves:

- `GET /queue`
- `GET /file?id=<queue-id>-model`
- `GET /file?id=<queue-id>-preview`
- `POST /status`

The userscript is:

```text
D:\1Repo\Github\ComfyUI\Workflow\lora\tools\civitai-upload\civitai-lora-uploader.user.js
```

Install/update it in ScriptCat or Tampermonkey.

## Queue Rules

Exclude any user-skipped projects, currently:

```text
kuromoon
oyari
```

Reject these files:

- `*-state\model.safetensors`
- training state folders
- cache folders
- dataset files
- TE cache files
- `post_image_dataset\_anima_uncond_te.safetensors`

Prefer final hand-picked files in each project `output` directory.

## Civitai Field Mapping

- Type: `LoRA`
- Base model: `Anima`
- Category:
  - `Style` for `@...` or `...style` artist projects
  - `Character` for `nanao` and `nanao2`
  - `Concept` for action/concept projects
- POI / actual person: `No`
- Mature: true for explicit concept/action models such as `cervical penetration`, `footjob through footwear`, `hairj`, `hairop`, `under-stirrup footjob`
- Version name: `v1.0`
- Version notes: `Initial release. Trained for Anima base. Selected checkpoint: <filename>.`
- Description: mention Anima base and trigger.

## Preview Selection

For artist/style models, do not search by the full trigger if it includes training wrapper text. Use artist body:

1. Strip leading `@`.
2. Strip trailing `style`.
3. Do not strip a real final `s` from names like `iris`.
4. For `nanao2`, search as `nanao`.

Image preference:

1. Latest project `output\sample` image.
2. Latest matching image under `E:\1Hub\EH\comfy` by artist body.
3. Recent fallback image only if required.

## Operating the Userscript

On Civitai create/wizard pages, use the floating `Civitai LoRA Upload` panel.

- `Run current`: process the current queue item.
- `Open`: open the saved wizard URL or create page.
- `Reload`: reload bridge queue/status.
- `Clear flow`: clear continuation state before starting a new item if prior navigation was interrupted.
- `Recover page`: on `wizard?step=4`, recover the missing preview post for the queue item matching the current model URL. In userscript v0.3+, this uses Civitai page APIs directly: create or reuse the hidden post, upload the preview through `/api/v1/image-upload/multipart`, then attach it with `post.addImage`.
- `Publish`: separate action; do not click unless the user confirms publishing.

If the panel logs `Missing combo input: Base Model` or `Timed out waiting for option LoRA`, rerun from the current wizard step. These are usually Civitai hydration timing issues.

If the model file is uploaded but the post image is missing, do not create a duplicate model. Open the existing `wizard?step=4` URL and use `Recover page`.

If `Recover page` reports `You've reached your daily limit for new posts` or `TOO_MANY_REQUESTS` from `post.create`, stop retrying that day. Civitai is blocking hidden post creation; the model file is already uploaded. Keep the saved `wizard?step=4` URL and retry recovery after the daily new-post limit resets.

## Verification

Use the bridge queue as local status evidence:

```powershell
node -e "fetch('http://127.0.0.1:8765/queue').then(r=>r.json()).then(j=>console.log(JSON.stringify(j.queue.map(x=>({project:x.project,status:x.status,wizardUrl:x.wizardUrl,note:x.note||''})),null,2)))"
```

Completion states:

- `hidden-post-ready`: model file and post image are uploaded; post is hidden/saved.
- `skipped` with note `model uploaded; post image pending`: model file is uploaded but step 4 needs `Recover page`, usually after the Civitai daily new-post limit resets.
- `published`: only if explicitly published.

Before declaring the whole job complete, verify every non-excluded confirmed item is either `hidden-post-ready` or `published`, and no item remains in post-image recovery.
