---
name: template-update
description: このプロジェクトの元になった python-project-template の新しい版を、copier で取り込む手順。「テンプレートの更新を取り込んで」「テンプレートを最新にして」と頼まれたとき、または `uvx copier check-update` が新しい版を見つけたときに使う。
---

# テンプレートの更新の取り込み

## 実行手順

1. 作業ツリーを空にする。
   - `git status --short` が空であることを確かめる。空でなければ、コミットするか退避するかを利用者に聞く。copier は作業ツリーが汚れていると取り込まない。
   - 取り込み用のブランチを切る: `git switch -c chore/template-update`

2. 新しい版を確かめる。
   - `uvx copier check-update` で、今の版（`.copier-answers.yml` の `_commit`）と新しい版を見る。

3. 取り込む。
   - `uvx copier update --defaults`（前回の回答をそのまま使う）。
   - 質問を変えたいと言われたときだけ `--defaults` を外す。

4. 衝突を解く。
   - `git status --short` で変わったファイルを見る。衝突は、ファイルの中の `<<<<<<<`〜`>>>>>>>` の印か、`.rej` のファイルとして出る。
   - チームが足した変更（依存・設定の値）は残し、テンプレートの変更（規則・スキル・`tools/`）を取り込む。どちらを残すか決められないときは、利用者に聞く。
   - `.rej` は中身を反映してから消す。`.copier-answers.yml` は手で書き換えない。

5. 確かめる。
   - `uv lock` → `uv sync --locked --dev` → `uv run pre-commit run --all-files` → `uv run pytest -q`。
   - テンプレートの決まりが変わっていたら、`docs/adr/0002-adopt-template-baseline.md` の参照先（テンプレート ADR）を読み、このプロジェクトの ADR で外している決まりとぶつからないかを見る。

6. コミットして PR を出す。
   - コミットメッセージの例: `chore: テンプレートの更新（v1.1.0）を取り込む`
   - PR の本文に、取り込んだ版と、衝突をどう解いたかを書く。
