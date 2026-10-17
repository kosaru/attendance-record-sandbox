# 図とPDFの再描画

Mermaid 11.12.0、Node.js、Playwright、Chromiumを使用する。Mermaidのローカルバンドルを第1引数へ渡す。

```sh
node tools/render.cjs /absolute/path/to/mermaid.min.js
```

既存Chromeを使う場合はCHROME_PATHへ実行ファイルを指定する。図の意味はdiagrams/*.mmd、表示用の機能の楕円変換はこのレンダラーで管理する。図・YAML・対応表を編集した場合は意味の再照合が必要であり、再描画だけで同期済みにはならない。
