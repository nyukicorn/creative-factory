# Creative Factory

マルチMCP環境でクリエイティブ作品を生成するプロジェクト

## 使用するMCP
- **Kamui Code MCP**: 画像・動画・音楽生成（メイン素材作成）
- **3JS MCP**: 3D環境・Web表示
- **Blender MCP**: 3Dモデリング・レンダリング調整

## プロジェクト構成
- `src/`: ソースコード
- `assets/`: 入力素材
- `workflows/`: GitHub Actions workflows
- `config/`: MCP設定ファイル
- `outputs/`: 生成物
  - `images/`: 生成画像
  - `videos/`: 生成動画
  - `audio/`: 生成音楽
  - `3d/`: 3Dモデル・シーン

## 制約
- 素材生成はKamui Code MCPのみを使用（月額プラン範囲内）
- ローカル開発 + GitHub Actions での自動化