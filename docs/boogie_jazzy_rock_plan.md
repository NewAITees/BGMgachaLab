# Boogie Jazzy Rock Fusion Plan

## ゴール
- 同じ方向性のプロンプトで何十曲か生成する
- その中から、人間が演奏しやすく、狙った雰囲気に合う曲を選ぶ
- 最終的に練習候補として約10曲を残す

## 本命プロンプト
`A solo piano boogie-woogie jazzy rock fusion piece. Keep a strong repetitive groove and a clear core rhythm throughout the piece. Start with a sparse texture and gradually add more notes, thicker chords, syncopated accents, bluesy fills, and energetic embellishments while preserving the same rhythmic foundation. The music should blend boogie-woogie drive, jazzy harmony, rock energy, and fusion-like richness. It should feel increasingly luxurious, exciting, and full over time, but remain playable by a human pianist.`

## 生成で狙う要素
- ブギウギ由来の強い推進力
- ジャジーな和声とブルージーな装飾
- ロック寄りの勢い
- 同じ土台リズムを繰り返しながら厚みが増していく構成
- 最後に向かって少しずつ豪華になる展開

## 評価観点
### 音楽的評価
- ブギウギ感があるか
- jazzy rock / fusion の混ざり方が自然か
- リズムの反復が核として残っているか
- 音数の増加と豪華さの上昇が感じられるか

### 演奏可能性評価
- 急激な大跳躍が多すぎないか
- 同時押鍵数が過密すぎないか
- ピアノ音域から大きく外れていないか
- 片手に無理な密度が集中していないか

## 運用の流れ
1. 同一プロンプトで複数回生成する
2. 自動で MIDI と MusicXML を出力する
3. 軽量な演奏可能性スコアで一次選別する
4. 残った候補を `pianoplayer` で二次評価する
5. その後に耳と譜面で確認する
6. 約10曲まで絞る

## 次の実務タスク
- 大量生成用のループ実行に対応させる
- 生成結果一覧を JSON または CSV で保存する
- 上位候補にタグやメモを付けられるようにする
- `pianoplayer` の評価結果も一覧に含める
- 総合スコア順に並べて上位10曲を自動抽出する
