# AGENTS.md（テンプレートの保守）

このリポジトリ（python-project-template）を保守するエージェント向けの規約。生成したプロジェクトのエージェントが読む規約は `project/AGENTS.md`。人向けの入口は `README.md`。

## 置き場所

- 生成先に写るのは `project/` の中だけ（`copier.yml` の `_subdirectory`）。生成先の利用者が使う文書・設定・コードは `project/` に置く。
- テンプレート自身のもの（この AGENTS.md、`README.md`、`docs/adr/` のテンプレート ADR、`.github/` のテンプレートの CI）は根に置き、`project/` に入れない。
- `project/` の中で描画されるのは `.jinja` の付いたファイルと、`{{ }}` を含むパス名だけ。GitHub Actions の `${{ }}` を含むファイルに `.jinja` を付けない。
- 生成先のチームが書き換えるファイルは、`copier.yml` の `_skip_if_exists` に入れる（update で上書きしない）。新しくそういうファイルを足したら、ここにも足す。

## 変えたあとの確かめ方

- PR の版から生成して、品質ゲートを流す。テンプレートの CI と同じ手順:

  ```bash
  uvx copier copy --vcs-ref HEAD --defaults -d project_name=try-sample . /tmp/try-sample
  cd /tmp/try-sample && git init -q && git add -A && uv lock && uv sync --locked --dev
  uv run pre-commit run --all-files && uv run pytest -q
  ```

- 根の `.github/workflows/` と `project/.github/workflows/ci.yml` の action の版はそろえる。dependabot は根しか見ないので、テンプレートの CI が版の食い違いで落ちる。

## 判断の記録とリリース

- テンプレートの設計判断は根の `docs/adr/` に ADR として残す（手順書は `.agents/skills/adr-management`。`project/` の手順書への symlink）。生成先の `project/docs/adr/` には写さない。
- 設計判断を変えた PR では、同じ PR で ADR を足し、この AGENTS.md・`project/AGENTS.md`・両方の README の古くなった記述を直す。
- マージしたら版のタグを付ける（`README.md` の「テンプレートを保守する」）。付けないと利用者に届かない。
- コミットメッセージは日本語（`.agents/skills/git-commit`）。
