# PDF Note Margin Maker

PDFの各ページの右側に、手書き用のノート欄を追加するWindows向けGUIツールです。
Goodnotesなどのノートアプリに読み込むと、PDF本文の横にメモ欄を作れます。

## できること

- PDFの右側にノート欄を追加
- ノート欄の幅を指定
- 横罫線のあり/なしを選択
- ページサイズが混在したPDFにも各ページごとのサイズで対応

## 出力イメージ

元PDF:

```text
┌──────────────┐
│ PDF本文      │
│              │
│              │
└──────────────┘
```

変換後:

```text
┌──────────────┬──────────────┐
│ PDF本文      │ ノート欄     │
│              │              │
│              │              │
└──────────────┴──────────────┘
```

## すぐ使う場合

Pythonを入れずに使う場合は、以下のファイルをダブルクリックしてください。

```text
release/PDF Note Margin Maker.exe
```

## 開発者向け

```bash
pip install -r requirements.txt
```

ソースから動作確認する場合は `app.py` を実行します。
通常利用では `release/PDF Note Margin Maker.exe` を使ってください。

## 使い方

画面で以下を選んでから「変換開始」を押してください。

- 入力PDF
- 出力PDF
- ノート欄の比率
- 横罫線の有無

## ノート欄の比率

ノート欄の比率は、元PDFの横幅に対する割合です。

| 比率 | 意味 |
| ---: | --- |
| `0.5` | 元PDFの半分の幅のノート欄 |
| `0.65` | 少し控えめなノート欄 |
| `1.0` | 元PDFと同じ幅のノート欄 |
| `1.2` | 元PDFより広いノート欄 |

## exeを作る場合

Windowsで `build_exe.bat` をダブルクリックすると、以下の配布用exeが更新されます。

```text
release/PDF Note Margin Maker.exe
```

初回は `pyinstaller` のインストールが走るため、インターネット接続が必要です。
ビルド中に作られる `dist` と `build` はGit管理対象外です。

## 注意事項

- パスワード付きPDFは処理できない場合があります。
- DRM付きPDFは処理できない場合があります。
- PDFのサイズが大きい場合、処理に時間がかかることがあります。
- 画像主体のPDFでは、出力ファイルサイズが大きくなることがあります。
- 変換前後のPDFは `.gitignore` でGit管理対象外にしています。

## ファイル構成

```text
pdf_subnote/
├── app.py           # GUI本体
├── converter.py     # PDF変換ロジック
├── release/
│   └── PDF Note Margin Maker.exe
├── build_exe.bat    # exe作成用
├── pdf_note_margin_maker.spec
├── requirements.txt
├── LICENSE
└── README.md
```

## ライセンス

MIT Licenseです。詳しくは `LICENSE` を確認してください。
