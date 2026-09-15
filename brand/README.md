# Brand assets

| File | Size | Use |
|---|---|---|
| `oif-avatar-400.png` | 400×400 | X, Reddit, most social profiles |
| `oif-avatar-512.png` | 512×512 | GitHub organisation, npm |
| `oif-avatar-1024.png` | 1024×1024 | anything wanting a large square |
| `oif-avatar-192.png` | 192×192 | web app manifest |
| `oif-avatar-180.png` | 180×180 | Apple touch icon |
| `oif-avatar-32.png` | 32×32 | favicon |
| `oif-avatar-400-circle-preview.png` | 400×400 | preview only, do not upload |
| `oif-header-1500x500.png` | 1500×500 | X header, social banner |

Upload the square avatar, not the circle preview. Platforms apply their
own circular mask; the preview exists so you can check the mark survives
it before uploading.

## The mark

`oif` in charcoal with `.md` at 42% height in amber, set in Adwaita Mono
Bold. The pair occupies 68% of the canvas width, which is what keeps it
inside a circular crop.

| Colour | Hex | Use |
|---|---|---|
| Charcoal | `#2D2D2D` | the wordmark, strokes, body text |
| Amber | `#E0A03C` | one accent per composition, never two |
| Off-white | `#F9F5EA` | background |

At small sizes `oif` stays legible and `.md` reduces to an amber
suggestion. That is intended. Enlarging `.md` to keep it readable at 32
pixels shrinks `oif` until neither works.

## Regenerating

```sh
python3 src/make-avatar.py     # every avatar size from the wordmark
python3 src/make-header.py     # crops the header source to 1500×500
```

The avatar is drawn directly, so it is exactly reproducible. The header
was generated once from a text prompt and is only reframed here; the
prompt is in `src/PROMPTS.md` if it ever needs regenerating.
