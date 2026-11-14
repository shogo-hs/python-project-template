# ADR 0008: 配り方を GitHub のテンプレートリポジトリから copier に移し、生成物を project/ に分ける

最終更新: 2026-11-14
- ステータス: 承認済み(accepted)
- 決定者: shogo-hs
- 関連: [ADR 0001](./0001-record-architecture-decisions.md), [ADR 0003](./0003-expand-ci-quality-gates.md), [ADR 0004](./0004-agents-md-and-shared-skills.md)

## 1. 文脈

テンプレートから実際にプロジェクトを立ち上げて、使う人の目線で監査したところ（2026-11-14）、次の問題があった。

- 「Use this template」は既定ブランチを丸ごと写し、写さないファイルを決める仕組みが無い。テンプレート自身の経緯を書いた ADR 0001〜0007（Cursor 対応や dotenvx をやめた経緯、保守者の宿題）・README がそのまま生成先に入り、生成先の新しい ADR は 0008 から始まっていた。
- 履歴がつながらないので、テンプレートの更新（`tools/code_graph.py` の修正、規約・手順書の改訂）を作ったプロジェクトに取り込む手段が無かった。
- pyproject・pre-commit・CI は、エージェントが手順書の Markdown（`templates.md`）から写して作っていた。作り方が 2 通りあり（`uv init` を勧める手順とひな形）、`uv init` の経路では入口のコマンドが `ImportError` で壊れた。同じ規則が 4〜5 か所に重なっていた。
- テンプレート自体に CI が無く、テンプレートを壊しても気づけなかった。

## 2. 決定

- copier（9.19 以上）で配る。`copier.yml` の `_subdirectory: project` で、生成先に写るものを `project/` に分け、テンプレート自身のもの（README・この docs/adr・テンプレートの CI・保守の AGENTS.md）を根に置く。
- pyproject・pre-commit・CI・dependabot・パッケージの骨組みを、`project/` の実際のファイル（名前を埋めるものだけ `.jinja`）にする。手順書 `python-project-bootstrap` と `python-uv-ci-setup` は消す。
- 生成先の ADR は、`0001`（ADR を使う）と `0002`（テンプレートの決まりを引き継ぐ。中身は AGENTS.md と設定ファイル、理由はテンプレート ADR、版は `.copier-answers.yml`）の 2 本から始める。テンプレート ADR は写さない。
- チームが書き換えるファイル（README・vision.md・`docs/adr/`（README・0001・0002）・`.env.example`・smoke テスト・Issue のテンプレート）は、`_skip_if_exists`（既存のプロジェクトへの copy で上書きしない）と、update のときだけの `_exclude`（update では扱わず、チームが消しても作り直さない）に入れる。ほか（AGENTS.md・手順書・`tools/`・CI・pre-commit・pyproject.toml・PR のテンプレート）は `copier update` でテンプレートに追従する。生成先に template-update の手順書を置く。
- `.claude/skills` の symlink を保つため `_preserve_symlinks: true` にする（無いとコピーになることを確かめた）。
- テンプレートの CI（`template-ci.yml`）で、PR の版から生成し（`--vcs-ref HEAD`。無いと最新のタグの版が写る）、品質ゲートと actionlint を流す。根と `project/` の CI の action の版の食い違いでも落とす（dependabot は根の `.github/workflows` しか見ないため）。
- マージしたら版のタグを付ける。copier は最新のタグを使うので、付けないと利用者に届かない。
- 判断基準: 生成先に関係ないものが入らないこと、更新を取り込めること、作り方が 1 通りであること、テンプレートの破損に CI で気づけること。

## 3. 代替案と不採用理由

- 代替案A: GitHub のテンプレートリポジトリのまま、立ち上げの手順で ADR と README を消す・書き換える。
  - 不採用理由: 手順に頼るので消し忘れが起き、更新を取り込む手段が無いままになる。
- 代替案B: GitHub のテンプレートリポジトリのまま、actions-template-sync で更新を取り込む。
  - 不採用理由: `-X theirs` で生成先の変更を上書きしがちで、生成物とテンプレート自身の文書を分ける問題も解けない。
- 代替案C: cookiecutter と cruft。
  - 不採用理由: 更新の取り込みは cruft という別の道具になる。copier は生成と更新が 1 つで、`uvx` で入れずに動く。
- 代替案D: テンプレート ADR を生成先に写し、番号を振り直す。
  - 不採用理由: テンプレートの経緯が生成先の判断として読まれる問題が残る。

## 4. 影響

- 使う人の手順が「Use this template」の 1 回の操作から、`uvx copier copy` と `gh repo create` の 2 本のコマンドになる。
- `copier update` で衝突したら、チームが解く（生成先の template-update の手順書）。
- 保守者は、生成してからでないとテンプレートを試せない（README と AGENTS.md の手順）。
- copier に移る前に作ったプロジェクトは、旧テンプレートの ADR と廃止した手順書を消してから `copier copy --overwrite` で入れ、差分を選び戻す（README）。
- GitHub のリポジトリ設定の「Template repository」を外す。押すと `project/` の外まで写ってしまうため。
- ADR 0003 のうち bootstrap の挙動についての決定と、ADR 0004 の手順書の一覧は、この ADR で置き換える。

## 5. フォローアップ

- [x] 生成先の CI（`code-graph` のコメントを含む）が GitHub Actions 上で動くことを確かめる（2026-11-14、agm-copilot の PR #6 で quality と code-graph が通り、コメントが付いた）。
- [~] 既にこのテンプレートから作ったプロジェクトを、README の「既にあるプロジェクトに入れる」の手順で移す（agm-copilot・humansim。旧テンプレートの ADR の本数が作った時期で違うので、README は範囲を決め打ちしない形に直した）。

## 6. 変更履歴

- 2026-11-14: 初版作成。
