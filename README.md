# python-project-template

Codex と Claude Code で開発する Python プロジェクトを、[copier](https://copier.readthedocs.io/) で作るテンプレート。

生成したプロジェクトには、次のものが最初から入る。

- 4 層（`adapters -> application -> ports -> domain`）のパッケージの骨組みと、依存の向きの検査（import-linter）
- 品質ゲート 6 本（ruff format・ruff check（関数の複雑さ 10 まで）・mypy・import-linter・deptry・pytest）を、pre-commit と GitHub Actions の両方で流す設定
- PR ごとに、コードの関係の差分（増えた・消えた・引数が変わった関数、モジュールの依存の増減）を CI が PR にコメントする仕組み
- エージェント向けの規約 `AGENTS.md` と手順書（ADR・コミット・テンプレートの更新の取り込み）

生成先に写るのは `project/` の中だけ。この README・`docs/adr/`（テンプレート ADR）・テンプレートの CI は写らない。

## 前提

- [uv](https://docs.astral.sh/uv/) 0.10.7 以上（copier は `uvx` で動かすので入れなくてよい）
- GitHub にリポジトリを作るなら [gh](https://cli.github.com/)

## 新しいプロジェクトを作る

```bash
uvx copier copy gh:shogo-hs/python-project-template csv-digest   # 質問に答える（プロジェクト名・パッケージ名・説明）
cd csv-digest
git init -b main
uv lock                                                          # uv.lock を作る（CI は uv.lock どおりに入れる）
git add -A && git commit -m "chore: テンプレートから立ち上げる"
gh repo create <owner>/csv-digest --private --source . --push
```

`uv.lock` と `.copier-answers.yml` は必ずコミットする。続きは生成したプロジェクトの README.md の「セットアップ」。`docs/product/vision.md` は、エージェントが最初の作業の前に聞いて埋める。

## テンプレートの更新を取り込む

生成したプロジェクトで、エージェントに「テンプレートの更新を取り込んで」と頼む（生成先の template-update の手順書）。手で行うなら次のとおり。

```bash
uvx copier check-update      # 新しい版があるかを見る
uvx copier update --defaults # 作業ツリーが空の状態で流す。衝突したファイルは git status で UU と出る
```

README・vision.md・`docs/adr/`（README・0001・0002）・`.env.example`・smoke テスト・Issue のテンプレートはチームのもので、更新では扱わない（消してあっても作り直さない）。`copier recopy` は使わない（生成のやり直しとして扱われ、チームが消したファイルが戻る）。それ以外（AGENTS.md・手順書・`tools/`・CI・pre-commit・pyproject.toml・PR のテンプレート）はテンプレートに追従する。

## 既にあるプロジェクトに入れる

テンプレートから作っていないプロジェクトや、copier に移る前（v1.0.0 より前）にこのテンプレートから作ったプロジェクトに入れるときは、上書きしてから差分を選び戻す。

copier に移る前のテンプレートから作ったプロジェクトでは、先に旧テンプレートから来たものを消す。消さないと、旧テンプレートの ADR 0001〜0007 と廃止した手順書が残り、ADR 0002 が 2 本並ぶ（どれも `git diff` には出ない）。チームが自分で書いた ADR（0008 以降など）は残す。

```bash
git switch -c chore/adopt-template          # 作業ツリーが空の状態から始める
# copier に移る前のテンプレートから作ったときだけ: 旧テンプレートの ADR・ADR の一覧・廃止した手順書を消す
git rm -r docs/adr/README.md docs/adr/000[1-7]-*.md \
  .agents/skills/python-project-bootstrap .agents/skills/python-uv-ci-setup \
  .claude/skills/python-project-bootstrap .claude/skills/python-uv-ci-setup
uvx copier copy --overwrite gh:shogo-hs/python-project-template .
git diff                                     # 消えた・変わった自分の内容を確かめる
git checkout -p -- <残したいファイル>         # 自分の内容に戻したい部分を選ぶ
```

旧テンプレートから移したときは、新しく入った `docs/adr/README.md` の一覧に、残したチームの ADR を書き足す。

`--overwrite` を付けないと、既にあるファイルとぶつかったところで止まり、途中まで書いた状態で残る。`.copier-answers.yml` を手で置いて `copier update` するだけでは、プロジェクトに無いファイルは「消したもの」と扱われ、何も足されない。

## テンプレートを保守する

保守の規約は [AGENTS.md](AGENTS.md)、テンプレートの設計判断は [docs/adr/](docs/adr/README.md)（テンプレート ADR）。

1. ブランチで `project/` か `copier.yml` を直し、PR を出す。テンプレートの CI（`.github/workflows/template-ci.yml`）が、PR の版から生成して品質ゲートを流す。
2. 手元で試すときは、PR の版（未コミットの変更を含む）から生成する。

   ```bash
   uvx --from copier==9.19.1 copier copy --vcs-ref HEAD --defaults -d project_name=try-sample . /tmp/try-sample
   ```

   `--vcs-ref HEAD` を付けないと、最新のタグの版から生成される。
3. マージしたら版のタグを付ける。**タグを付けないと、利用者の `copier copy`・`copier update` に届かない**（copier は最新のタグを使う）。

   ```bash
   gh release create v1.1.0 --generate-notes   # 互換を壊す変更は v2.0.0 のように上げる
   ```
