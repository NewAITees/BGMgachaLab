# Large Scale BGM Projects

## 前提
このリポジトリでは、販売や配信用の大量生成を考えるときに、まず生成ルートを分けて考える。

- `MusicGen` ルート: そのまま聴ける `wav` を作る
- `MIDI-LLM` ルート: `mid` を作り、あとで編集や譜面化を行う

今回の 2 プロジェクトは、用途と販売形態が違うので、同じ運用にはしない。

## Project 1: 配信向けイージーリスニング BGM 大量生成

### 目的
- 配信で長時間流せる BGM を大量に用意する
- ジャンルごとに約 1 時間分の素材をそろえる
- 耳に刺さりにくく、ループや長時間再生に耐えるものを中心にする

### 共通制約
- イージーリスニング寄り
- 眠くなりすぎない
- 高音がキーキーしない
- 配信で声を邪魔しない
- 1 曲あたり約 4 分

### 組み合わせ軸
- jazz
- techno-leaning ambient
- DTM / electronic production
- piano-centered
- piano trio
- modern classical

### 運用単位
- 1 バリエーション = 4 分曲 x 15 本 = 約 1 時間
- ここでいうバリエーションは、共通制約に対して組み合わせ軸を 1 つまたは複数重ねたもの

### 例
- jazz + piano trio
- techno-leaning ambient + DTM
- modern classical + piano-centered
- jazz + DTM + piano-centered

### 推奨ルート
- 第一候補: `MusicGen`

理由:
- 直接 `wav` が出る
- 配信用 BGM はまず耳で確認できることが重要
- 今の repo には長尺 `wav` 生成の実績がある

### 「このアーティストっぽい」の扱い
この repo では、音楽ジャンルは主軸として保持し、その上にアーティスト要素を補助レイヤーとして加える。

運用ルール:
- まずジャンルを書く
- 必要ならアーティスト名も直接入れる
- ただし、名前だけに依存せず特徴量も必ず併記する
- アーティスト要素はジャンルを置き換えない

併記する特徴量の例:
- 音色
- 和声傾向
- テンポ感
- リズムの密度
- 空間の広さ
- グルーヴの強さ
- 時代感
- 展開の仕方

例:
- 直接名 + 特徴量: `game music, Nobuo Uematsu, lyrical melody, clear harmonic motion, gentle emotional lift`
- 直接名 + 特徴量: `ambient techno, Brian Eno, soft atmospheric drift, restrained development, spacious but controlled texture`
- 特徴量のみ: `warm jazzy hip-hop harmony, dusty drums, soft piano loop, late-night city mood`

参照:
- [artist_style_layers.md](/home/perso/analysis/BGMgachaLab/docs/artist_style_layers.md)

### 販売向けの運用単位
- `variation_pack/<style>/`
- 1 パック = 15 曲前後
- 各曲にメタデータを付ける

必要メタデータ:
- title
- genre
- bpm
- mood
- usage
- duration
- prompt
- model
- revision

## Project 2: ゲーム BGM 生成・販売

### 目的
- ゲームのシーン別に BGM を用意する
- 販売時に「用途が明確なセット」として整理する

### シーン軸
- title
- town
- field
- battle
- boss
- dungeon
- stealth
- puzzle
- victory
- game over
- shop
- event / cutscene

### 基本単位
ゲーム BGM は配信 BGMより短く、用途ごとに切る。

推奨:
- 2 分から 4 分の曲をベースにする
- 必要ならループ前提で設計する

### 推奨ルート
- 第一候補: `MusicGen`
- 第二候補: `MIDI-LLM` を補助的に使う

使い分け:
- まず販売用の試作品や大量試作は `MusicGen`
- 明確なメロディ、ループ編集、譜面管理が必要な場面では `MIDI-LLM`

### 販売向けの整理単位
- `scene_pack/<theme>/`
- 1 パック = 同一世界観の 8 から 12 曲

テーマ例:
- fantasy RPG
- cyberpunk
- cozy life sim
- dark dungeon
- sci-fi strategy

### 必須メタデータ
- title
- scene
- theme
- bpm
- loop_intent
- tension
- duration
- prompt
- model
- revision

## リスク整理

### 1. アーティスト模倣リスク
- 特定アーティスト名をそのまま販売用生成条件に使わない
- 特徴を抽象化して style guide 化する

### 2. 長時間 BGM の品質ばらつき
- 長尺を 1 回で当てに行かず、複数候補から選ぶ
- 6 本生成して 3 本採用のような歩留まり前提で考える

### 3. 販売物の整理不足
- 生成直後からメタデータを保存する
- ファイル名だけで管理しない

## 最初の実行順

### Phase 1
- 配信向け 3 バリエーションで試作
- 各バリエーション 4 分 x 3 曲
- 合計 9 曲で品質確認

初期 3 バリエーション案:
- `jazz + piano trio`
- `techno-leaning ambient + DTM`
- `modern classical + piano-centered`

### Phase 2
- 良かったバリエーションを 4 分 x 15 曲まで拡張
- 1 バリエーション 1 時間体制を作る

### Phase 3
- ゲーム向けに 2 テーマ試作
- 各テーマ 4 シーンずつ作る

### Phase 4
- 販売用パッケージ構成とメタデータ整備
