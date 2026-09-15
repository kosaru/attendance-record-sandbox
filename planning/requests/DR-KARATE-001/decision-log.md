# 判断記録

- ユーザーは提示した初期要望を出発点とした要件定義開始に「はい。お願い。」と回答した。
- ユーザーは今回の対象を「新しいアプリとして別に作る」と選択した。
- ユーザーは約15道場への導入について、仕様と運用を「自分が最終判断する」と回答した。
- 当初はローカルに保存しており、GitHub上の登録Commitは未成立だった。
- 正式Baseline、実装開始、Release、Deploymentを承認・成立した記録ではない。
- 正本仕様確認Commit: cbf58de3d2470686558c03b9961520086162b68a

## 保存先の指定と公開設定

- ユーザー指定の資料フォルダ: https://drive.google.com/drive/folders/1C3hvmntQkT2W6hVfve0RpssK6PwBxJTE
- Release用: https://github.com/kosaru/attendance-record
- Sandbox用: https://github.com/kosaru/attendance-record-sandbox
- Sandboxの公開設定確認にユーザーは「公開でいいよ。」と回答した。
- 初期READMEをGitHub連携で作成しようとしたが、403 Resource not accessible by integrationで拒否された。登録Commitはまだ成立していない。

## GitHub登録の再開

- ユーザーがGitHub Appの連携対象に両リポジトリを追加し、「設定したよ。」と回答した。
- 接続対象の追加を確認後、初期READMEの書き込みが成功した。初期Commit: ed9d32e746134935f74c535cc852d374fa860844。
- ユーザーの「中断した作業進めて」を受け、planning/DR-KARATE-001へ開発要求、議論、判断の記録を登録する。
- 過去の403エラーは解消済み。これは要件定義への着手記録であり、正式Baselineまたは実装開始の成立ではない。

## QRコードの配布・掲示と問い合わせ窓口

- QRコードを依頼者が各道場へ配布し、各道場責任者が掲示する確認に、ユーザーは「1.はい。」と回答した。
- 公開後のアプリの問い合わせ窓口を依頼者が担当する確認に、ユーザーは「2.はい。」と回答した。
- 企画書第0.2版と編集元に反映。企画全体の承認、正式Baseline、実装開始の承認へ読み替えない。

## Webアプリ方式と記録の引き継ぎ

- URLを開きホーム画面に追加する方式に、ユーザーは「1.はい。」と回答した。
- 機種変更・紛失後も記録を引き継ぐ希望に「2.はい。」と回答した。
- 「私のアカウントのGoogleドライブに保存してもいいよ。」と保存先候補の利用を許可した。Google Driveを唯一の保存先にする指定や、保存方式の技術的成立、全員へのフォルダ共有の承認とは読み替えない。
- Google Apps Scriptは所有者として実行するWebアプリを構成できる。Driveを使う案の候補だが、本人・家族の権限、同時記録の重複防止、カメラとWebアプリの実機動作、利用制限と復旧を検証する前に採用確定しない。
- 運用データは資料共有用フォルダとは別の非公開領域を候補とする。実際の作成・共有変更・本番データ保存は未実施。
- 保存だけでは本人の記録を復元できないため、ログイン・復旧方法を次に確認する。
- 調査根拠: https://developers.google.com/apps-script/guides/web および https://developers.google.com/apps-script/guides/services/quotas （確認日2026-09-15）。正式Baseline・実装開始は未成立。
