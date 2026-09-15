# Image prompts

The avatar is drawn by `make-avatar.py` and needs no model.

The header came from the Gemini image API (`gemini-3.1-flash-image`) at
21:9, then cropped by `make-header.py`. Keep the palette sentence
verbatim in any regeneration; without it the model adds gradients,
drop shadows and blur that do not match the avatar.

## Header — chosen

> Wide letterbox banner. The background is divided into four tall
> vertical bands by thin faint charcoal vertical rules, like columns on a
> kanban board, very low contrast so they read as structure not
> decoration. Sitting on these bands are five small document sheet
> outlines drawn in thick charcoal with folded top-right corners,
> distributed unevenly across the columns; the sheet in the third column
> is filled muted amber. Warm off-white cream background, dark charcoal
> strokes, one muted amber accent colour. Flat minimal vector, no
> gradients, no drop shadows, no blur, no 3D, no photographic texture,
> crisp clean edges. No text or lettering anywhere.

## Notes for future generations

- Always pass `--style none`. The default house style belongs to another
  project and will not match these assets.
- Ask for "no text or lettering anywhere" explicitly. Models add stray
  letterforms to anything that looks like a logo.
- Generated sheets sometimes come back with soft shadows despite the
  instruction. Regenerate rather than accept; the flat look is the
  through-line between the avatar and the header.
