# MusicGen Prompting Guide

## Scope
This note summarizes prompt-writing guidance for `MusicGen` based on official sources and adapts it to this repository's use cases.

Related local references:
- [artist_style_layers.md](/home/perso/analysis/BGMgachaLab/docs/artist_style_layers.md)

Primary sources:
- AudioCraft repository: https://github.com/facebookresearch/audiocraft
- MusicGen docs: https://raw.githubusercontent.com/facebookresearch/audiocraft/main/docs/MUSICGEN.md
- MusicGen model card: https://raw.githubusercontent.com/facebookresearch/audiocraft/main/model_cards/MUSICGEN_MODEL_CARD.md
- MusicGen paper: https://arxiv.org/abs/2306.05284
- Hugging Face model page: https://huggingface.co/facebook/musicgen-stereo-medium

## What the official sources say

### 1. MusicGen is text-conditioned, but prompt engineering matters
The official model card states that it can be difficult to know which text descriptions work best, and that prompt engineering may be required to get satisfying generations.

Implication for this repo:
- treat prompt writing as a first-class part of generation quality
- generate multiple prompt variants instead of relying on one sentence

### 2. English descriptions are the strongest default
The official model card says the model was trained with English descriptions and will not perform as well in other languages.

Implication:
- write the actual generation prompt in English
- supporting notes can stay in Japanese, but the prompt body should stay English

### 3. Official examples are short, attribute-rich descriptions
The official docs and model pages use prompts like:
- `happy rock`
- `energetic EDM`
- `sad jazz`
- `80s pop track with bassy drums and synth`
- `90s rock song with loud guitars and heavy drums`

Inference from the official examples:
- concise prompts work
- prompts are usually built from stacked attributes rather than long prose
- useful prompt parts are genre, mood, era, instrumentation, and mix character

### 4. The model is controllable, but not exact
The paper and docs position MusicGen as controllable, but the model card also warns that results vary by style and culture, and that prompt engineering is needed.

Implication:
- use prompts to steer direction, not to demand exact arrangements
- expect iteration

## Recommended prompt structure

For this repo, the most reliable pattern is:

`[use case], [genre/style], [artist name if used], [decomposed artist traits], [instrumentation], [musical form], [groove/tempo feel], [mix/timbre], [length intent]`

Example template:

`streaming background music, easy-listening, modern jazz piano trio, GoGo Penguin, driving piano ostinato, acoustic trio precision, warm upright bass, soft brushed drums, start with a simple piano motif, gradually build a gentle groove, keep a stable middle section, add a small late variation, finish with a soft resolved ending, rounded piano tone, soft top end, controlled room sound, around four minutes`

This follows the same attribute-stacking style as the official examples, but makes the constraints explicit for our use case.

## Useful prompt ingredients

### Genre / style
- `modern jazz`
- `ambient electronic`
- `techno-leaning ambient`
- `modern classical`
- `piano trio`
- `piano-centered`

### Mood / function
- `easy-listening`
- `streaming background music`
- `focused but calm`
- `not sleepy`
- `voice friendly`
- `low-fatigue`

### Instrumentation
- `warm upright bass`
- `muted brushed drums`
- `rounded piano tone`
- `low-mid synth bed`
- `grounded chamber atmosphere`

### Artist layer
- `Brian Eno`
- `Aphex Twin`
- `Max Cooper`
- `Nobuo Uematsu`
- `Shoji Meguro`
- `GoGo Penguin`
- `Yussef Dayes`

### Movement / energy
- `gentle forward motion`
- `soft pulse`
- `restrained repetition`
- `light rhythmic motion`

### Musical form
- `start with a simple motif`
- `gradually layer the groove`
- `keep a stable middle section`
- `add a small late variation`
- `finish with a soft resolved ending`
- `finish with a quiet natural cadence`

### Mix / timbre
- `soft top end`
- `controlled room sound`
- `controlled reverb`
- `dry-to-moderate ambience`
- `warm low mids`
- `lightly dusty texture`
- `slightly worn texture`

## Things to avoid in prompts

These are not forbidden by MusicGen itself, but they are poor fits for the streaming BGM goal:

- `bright`
- `shimmer`
- `glossy`
- `sparkling highs`
- `crisp hats`
- `aggressive transients`
- `sharp leads`
- `huge reverb tails`
- `dramatic peaks`

Why:
- they can push the model toward ear-fatiguing highs
- they can increase the chance of brittle attacks or echo-heavy top end
- they work against the user's stated goal

Also avoid relying on negative-only structure instructions such as:
- `no abrupt start`
- `no abrupt ending`
- `no sudden section change`

Why:
- positive structure wording is more actionable for MusicGen than abstract prohibition
- telling the model how to begin, develop, and resolve is more reliable than only telling it what not to do

## Guidance for this repository

### For streaming BGM
Prefer:
- short English prompts with explicit constraints
- warm timbre terms
- low-fatigue mix terms
- function words like `streaming background music` or `voice friendly`
- explicit form words that describe intro, development, middle stability, late variation, and ending

Avoid:
- highly cinematic build instructions
- very bright descriptors
- dramatic arrangement language

Example:

`streaming background music, easy-listening techno-leaning ambient with soft electronic arrangement, soft pulse, low-mid synth bed, start with warm pads and a soft pulse, gradually layer the rhythm, keep a stable middle section for talking-friendly background use, add a small texture shift in the later section, finish with a smooth natural ending, warm low mids, dry-to-moderate ambience, soft top end, focused but calm, around four minutes`

### For game BGM
Prefer:
- scene + style + instrumentation + tension level

Example:

`town theme, cozy modern fantasy, light piano and woodwinds, gentle rhythmic motion, warm room tone, soft top end, calm and inviting`

### For artist-adjacent prompts
In this repo, artist usage has two layers:
- keep the main genre/style as the primary anchor
- optionally add the artist name directly as a secondary steering tag
- always add decomposed traits after the name

Recommended order:
- genre first
- artist name second
- traits third

Example:
- `ambient techno, Brian Eno, soft atmospheric drift, restrained development, spacious but controlled texture`

Important:
- the artist name should be an added flavor layer, not a replacement for the genre
- do not rely on the name alone; always pair it with explicit traits

Traits to decompose into:
- harmony
- groove
- instrumentation
- timbre
- era feel
- mix character

Example conversion:
- direct-plus-traits: `game music, Shoji Meguro, jazz-inflected harmony, tight rhythm section, modern urban atmosphere`
- traits-only: `warm jazzy harmony, dusty drums, soft piano loop, late-night city mood`

## Working rules

1. Keep prompts in English.
2. Stack attributes instead of writing long narrative paragraphs.
3. Put the functional goal near the front:
   - `streaming background music`
   - `game battle theme`
   - `easy-listening`
4. Describe musical form directly:
   - intro
   - gradual development
   - stable middle
   - small late variation
   - natural ending
5. Add negative steering through positive wording:
   - use `soft top end` instead of only saying `not harsh`
6. When quality matters, generate multiple variants with small wording changes.

## Practical conclusion

For this repo, the best prompt style is:
- English
- short to medium length
- attribute-stacked
- explicit about role and sound constraints

That is the closest match to the official examples and the safest path for repeatable MusicGen outputs.
