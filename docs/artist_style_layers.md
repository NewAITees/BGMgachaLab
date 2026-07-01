# Artist Style Layers

## 目的
このメモは、音楽ジャンルを主軸に保ったまま、アーティスト要素を補助レイヤーとして加えるための整理表である。

基本方針:
- ジャンルはそのまま残す
- アーティスト名は補助タグとして加える
- 同時に特徴量も併記する
- 実際のプロンプトは `genre + artist tag + decomposed traits + form + mix constraints` の順で組む

例:
- `streaming background music, ambient techno, Brian Eno, soft atmospheric drift, restrained development, spacious but controlled texture, gentle intro, stable middle section, natural ending`
- `game music, Nobuo Uematsu, lyrical melody, clear harmonic motion, gentle emotional lift, natural instrumental layering`

## レイヤー構造

### 1. Genre layer
曲の骨格を決める主軸。

例:
- `game music`
- `ambient`
- `techno`
- `jazz`
- `modern classical`
- `piano trio`

### 2. Artist tag layer
方向を強めるための補助ラベル。

例:
- `Nobuo Uematsu`
- `Aphex Twin`
- `Max Cooper`
- `Brian Eno`
- `Shoji Meguro`
- `GoGo Penguin`
- `Tigran Hamasyan`
- `Yussef Dayes`

### 3. Decomposed traits layer
アーティスト名だけに依存しないよう、特徴を並べる層。

分類:
- melody
- harmony
- rhythm
- instrumentation
- texture
- arrangement
- mix character
- emotional motion

## Artist Reference Table

### Game music

#### Nobuo Uematsu
- use case: `game music`, `field`, `town`, `battle`, `emotional theme`
- traits:
  - lyrical melody
  - clear harmonic motion
  - memorable motif writing
  - gentle emotional lift
  - orchestral-to-band hybrid feel
- prompt fragment:
  - `game music, Nobuo Uematsu, lyrical melody, clear harmonic motion, memorable motif, gentle emotional lift`

#### Shoji Meguro
- use case: `game music`, `urban RPG`, `stylish battle`, `late-night city`
- traits:
  - jazz-inflected harmony
  - tight rhythm section
  - modern urban atmosphere
  - cool restrained tension
  - groove-first arrangement
- prompt fragment:
  - `game music, Shoji Meguro, jazz-inflected harmony, tight rhythm section, modern urban atmosphere, cool restrained tension`

### Ambient / electronic

#### Brian Eno
- use case: `ambient`, `calm background`, `low-fatigue streaming BGM`
- traits:
  - soft atmospheric drift
  - restrained development
  - spacious but controlled texture
  - subtle repetition
  - non-intrusive motion
- prompt fragment:
  - `ambient, Brian Eno, soft atmospheric drift, restrained development, spacious but controlled texture, subtle repetition`

#### Aphex Twin
- use case: `electronic`, `experimental ambient`, `broken rhythm`, `textural variation`
- traits:
  - unusual rhythmic detail
  - fragile melodic fragments
  - warped electronic texture
  - intimate synthetic timbre
  - detailed micro-variation
- prompt fragment:
  - `electronic, Aphex Twin, unusual rhythmic detail, fragile melodic fragments, warped texture, intimate synthetic timbre`

#### Max Cooper
- use case: `ambient techno`, `cinematic electronic`, `gradual build`
- traits:
  - precise pulse design
  - evolving texture
  - spacious modern production
  - geometric rhythmic layering
  - controlled emotional rise
- prompt fragment:
  - `ambient techno, Max Cooper, precise pulse design, evolving texture, spacious modern production, controlled emotional rise`

### Piano trio / jazz-adjacent

#### GoGo Penguin
- use case: `piano trio`, `modern acoustic groove`, `minimal repetition`
- traits:
  - driving piano ostinato
  - acoustic trio precision
  - modern minimal groove
  - clean dynamic contour
  - contemporary chamber-jazz feel
- prompt fragment:
  - `piano trio, GoGo Penguin, driving piano ostinato, acoustic trio precision, modern minimal groove, clean dynamic contour`

#### Tigran Hamasyan
- use case: `piano-centered`, `modern jazz`, `rhythmic complexity`
- traits:
  - strong piano attack
  - asymmetrical rhythmic motion
  - modal harmonic color
  - dramatic but controlled development
  - folk-inflected melodic contour
- prompt fragment:
  - `modern jazz piano, Tigran Hamasyan, asymmetrical rhythmic motion, modal harmonic color, dramatic but controlled development`

### Drums / groove

#### Yussef Dayes
- use case: `groove-led background music`, `modern jazz rhythm`, `drum character`
- traits:
  - fluid live drumming
  - broken groove nuance
  - warm cymbal texture
  - elastic pocket
  - organic momentum
- prompt fragment:
  - `modern jazz rhythm section, Yussef Dayes, fluid live drumming, broken groove nuance, warm cymbal texture, organic momentum`

## 実運用ルール

1. ジャンルを先に書く
2. アーティスト名はジャンルの後ろに置く
3. その後ろに特徴量を並べる
4. 曲構成の指示は別レイヤーとして必ず入れる
5. 配信用BGMでは、アーティスト要素を入れても耳障りな高音や急変を避ける制約を残す

## 配信用BGMテンプレート

`streaming background music, easy-listening, [genre], [artist name], [artist traits], start with [intro], gradually [development], keep a stable middle section for talking-friendly background use, add a small late variation, finish with a natural ending, [mix constraints], around three to four minutes`

## ゲームBGMテンプレート

`game music, [scene], [genre], [artist name], [artist traits], start with [intro], gradually [development], keep a clear middle section, finish with a natural ending, [instrumentation], [mix constraints]`
