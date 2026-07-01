# Streaming BGM Variations

Reference:
- [musicgen_prompting_guide.md](/home/perso/analysis/BGMgachaLab/docs/musicgen_prompting_guide.md)

## 共通制約
- easy listening
- not sleepy
- controlled reverb
- soft top end
- streamer voice friendly
- around 4 minutes per track
- clear musical form
- gentle intro
- gradual development
- stable middle section
- small late variation
- natural ending

## Axis Matrix

- axes count: 7
- single-axis variation count: 7
- two-axis variation count: 21
- total variation count: 28
- only single-axis and two-axis combinations are generated

Axes:
- `jazz`
- `techno`
- `ambient`
- `dtm`
- `piano_centered`
- `piano_trio`
- `modern_classical`

## Initial Variation Set

### 1. jazz_piano_trio
- axes: `jazz + piano trio`
- target: modern, light groove, warm upright bass, muted brushed drums, clear but soft piano, lightly dusty texture
- form: simple piano-and-bass intro, gradual groove entry, stable talking-friendly middle, small harmonic lift near the end, soft resolved ending

Prompt guide:
`streaming background music, easy-listening, modern jazz, piano trio, warm upright bass, muted brushed drums, rounded piano tone, start with a simple piano motif and light bass, gradually bring in a gentle groove, keep a stable middle section for talking-friendly background use, add a small harmonic variation in the later section without changing the core mood, finish with a soft resolved ending, tasteful harmony, gentle forward motion, lightly dusty texture, controlled room sound, soft top end, not sleepy, around four minutes`

### 2. techno_ambient
- axes: `techno + ambient`
- target: soft pulse, low-mid synth bed, smooth low-mid energy, spacious but controlled atmosphere
- form: soft pad opening, gradual pulse layering, steady central flow, modest texture change later, smooth fade-like resolution

Prompt guide:
`streaming background music, easy-listening, techno, ambient, soft pulse, low-mid synth bed, start with warm pads and a soft pulse, gradually layer the rhythm and atmosphere, keep a stable middle section with steady motion for talking-friendly background use, introduce a small texture change in the later section while keeping the same mood, finish with a smooth natural ending, warm low mids, light rhythmic motion, controlled space, dry-to-moderate ambience, focused but calm, around four minutes`

### 3. modern_classical_piano
- axes: `modern classical + piano-centered`
- target: grounded chamber feel, soft repetition, restrained harmony changes, elegant motion
- form: sparse piano opening, gentle layering of repeated figures, balanced middle plateau, slight melodic turn later, quiet cadential close

Prompt guide:
`streaming background music, easy-listening, modern classical, piano-centered, grounded chamber atmosphere, start with sparse piano figures, gradually build soft repeating patterns, keep a stable middle section with restrained harmony for talking-friendly background use, add a slight melodic turn in the later section without becoming dramatic, finish with a quiet natural cadence, soft repeating figures, restrained harmony, elegant motion, controlled room sound, soft top end, refined and calm, around four minutes`

## Trial Plan
- 3 variations
- 3 tracks per variation
- total 9 tracks
- duration per track: 240 seconds
- 4 minutes is expected to be generated in one pass, not stitched from 120-second segments

## Output Layout
- `outputs/streaming_bgm_trial/`
- one subfolder per variation

## Full Matrix Plan
- 28 variations
- 3 tracks per variation
- total 84 tracks
- duration per track: 240 seconds
- 4 minutes is expected to be generated in one pass when memory allows

Full matrix generator:
- [generate_streaming_bgm_full_matrix.py](/home/perso/analysis/BGMgachaLab/scripts/generate_streaming_bgm_full_matrix.py)
