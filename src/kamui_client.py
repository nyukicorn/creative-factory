#!/usr/bin/env python3
"""
Kamui Code MCP Client - 実際のKamui Code MCPとの通信
"""

import subprocess
import tempfile
import os
import re
import requests
from pathlib import Path
from urllib.parse import urlparse
from mcp_safety import safety_controller

class KamuiMCPClient:
    """Kamui Code MCP通信クライアント"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # 環境に応じて設定パスを決定
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, ".claude", "mcp-kamuicode.json")
        self.config_path = config_path
        self.project_root = Path(__file__).parent.parent
        self.outputs_dir = self.project_root / "outputs"
        
        # 出力ディレクトリを確保
        for subdir in ["images", "videos", "audio", "3d"]:
            (self.outputs_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    def call_claude_with_kamui(self, prompt, working_dir=None):
        """Claude CodeをKamui MCP設定で呼び出し"""
        # 安全性チェック
        safety_controller.verify_kamui_mcp_available()
        
        # 作業ディレクトリ設定
        if working_dir is None:
            working_dir = self.project_root
        
        try:
            # PATH環境変数を設定
            env = os.environ.copy()
            home_dir = os.path.expanduser("~")
            env['PATH'] = f"{home_dir}/.local/bin:" + env['PATH']
            # 非対話モードを強制
            env['CLAUDE_AUTO_YES'] = "1"
            
            # Claude Code実行コマンド
            cmd = [
                "claude",
                f"--mcp-config={self.config_path}",
                "--print",
                "--dangerously-skip-permissions"
            ]
            
            print(f"🔧 Executing: {' '.join(cmd)}")
            print(f"📂 Working directory: {working_dir}")
            print(f"📄 Config path: {self.config_path}")
            
            # プロンプトを標準入力で送信
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                env=env
            )
            
            stdout, stderr = process.communicate(input=prompt)
            
            print(f"📤 Return code: {process.returncode}")
            print(f"📥 Stdout length: {len(stdout)}")
            if stderr:
                print(f"⚠️ Stderr: {stderr}")
            else:
                print("ℹ️ No stderr output")
            
            if process.returncode != 0:
                error_msg = f"Claude Code error (exit {process.returncode})"
                if stderr:
                    error_msg += f": {stderr}"
                if stdout:
                    error_msg += f"\nStdout: {stdout[:500]}..."
                raise Exception(error_msg)
            
            return stdout
            
        except FileNotFoundError as e:
            raise Exception(f"Claude Code not found. Make sure it's installed and in PATH: {e}")
        except subprocess.TimeoutExpired:
            raise Exception("Claude Code execution timeout")
        except Exception as e:
            print(f"❌ Error calling Claude Code: {e}")
            print(f"🔍 Command: {' '.join(cmd)}")
            print(f"🔍 Working dir: {working_dir}")
            print(f"🔍 Config exists: {os.path.exists(self.config_path)}")
            raise
    
    def extract_urls_from_response(self, response_text):
        """レスポンスからダウンロードURLを抽出"""
        # URLパターンを検索
        url_patterns = [
            r'https://[^\s<>"\']+\.(?:jpg|jpeg|png|gif|mp4|mov|mp3|wav|obj|fbx|gltf)',
            r'https://storage\.googleapis\.com/[^\s<>"\']+',
            r'https://[a-zA-Z0-9.-]+\.googleusercontent\.com/[^\s<>"\']+',
            r'https://fal\.media/[^\s<>"\']+',
        ]
        
        urls = []
        for pattern in url_patterns:
            found_urls = re.findall(pattern, response_text)
            urls.extend(found_urls)
        
        return list(set(urls))  # 重複削除
    
    def download_file(self, url, output_path):
        """URLからファイルをダウンロード"""
        try:
            print(f"📥 Downloading: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    def generate_image(self, prompt, style="photorealistic", aspect_ratio="1:1", output_name=None):
        """画像生成"""
        if output_name is None:
            output_name = f"image_{hash(prompt) % 10000}.jpg"
        
        output_path = self.outputs_dir / "images" / output_name
        
        kamui_prompt = f"""
{prompt}をテーマにした画像を生成してください。

設定:
- スタイル: {style}
- アスペクト比: {aspect_ratio}
- 高品質で生成してください

生成完了したら、必ず以下を実行してください:
1. ダウンロードURLのフルパス表示（省略なし）
2. 今いるディレクトリ（{output_path.parent}）にダウンロード
3. ダウンロード完了後にopenコマンドで開く

保存したファイルの場所は~からのフルパスで表示してください。
"""
        
        print(f"🎨 Generating image: {prompt}")
        response = self.call_claude_with_kamui(kamui_prompt)
        
        # URLを抽出してダウンロード
        urls = self.extract_urls_from_response(response)
        if urls:
            downloaded_file = self.download_file(urls[0], output_path)
            if downloaded_file:
                return downloaded_file
        
        print("⚠️ No download URL found in response")
        return str(output_path)
    
    def generate_video(self, prompt, duration=5, fps=24, output_name=None):
        """動画生成"""
        if output_name is None:
            output_name = f"video_{hash(prompt) % 10000}.mp4"
        
        output_path = self.outputs_dir / "videos" / output_name
        
        kamui_prompt = f"""
{prompt}をテーマにした動画を生成してください。

設定:
- 継続時間: {duration}秒
- FPS: {fps}
- 高品質で生成してください

生成完了したら、必ず以下を実行してください:
1. ダウンロードURLのフルパス表示（省略なし）
2. 今いるディレクトリ（{output_path.parent}）にダウンロード
3. ダウンロード完了後にopenコマンドで開く

保存したファイルの場所は~からのフルパスで表示してください。
"""
        
        print(f"🎬 Generating video: {prompt}")
        response = self.call_claude_with_kamui(kamui_prompt)
        
        # URLを抽出してダウンロード
        urls = self.extract_urls_from_response(response)
        if urls:
            downloaded_file = self.download_file(urls[0], output_path)
            if downloaded_file:
                return downloaded_file
        
        print("⚠️ No download URL found in response")
        return str(output_path)
    
    def generate_music(self, prompt, duration=30, genre="ambient", output_name=None):
        """音楽生成"""
        if output_name is None:
            output_name = f"music_{hash(prompt) % 10000}.mp3"
        
        output_path = self.outputs_dir / "audio" / output_name
        
        kamui_prompt = f"""
{prompt}をテーマにした音楽を生成してください。

設定:
- 継続時間: {duration}秒
- ジャンル: {genre}
- 高品質で生成してください

生成完了したら、必ず以下を実行してください:
1. ダウンロードURLのフルパス表示（省略なし）
2. 今いるディレクトリ（{output_path.parent}）にダウンロード
3. ダウンロード完了後にopenコマンドで開く

保存したファイルの場所は~からのフルパスで表示してください。
"""
        
        print(f"🎵 Generating music: {prompt}")
        response = self.call_claude_with_kamui(kamui_prompt)
        
        # URLを抽出してダウンロード
        urls = self.extract_urls_from_response(response)
        if urls:
            downloaded_file = self.download_file(urls[0], output_path)
            if downloaded_file:
                return downloaded_file
        
        print("⚠️ No download URL found in response")
        return str(output_path)
    
    def generate_3d_model(self, prompt, complexity="medium", output_name=None):
        """3Dモデル生成"""
        if output_name is None:
            output_name = f"model_{hash(prompt) % 10000}.obj"
        
        output_path = self.outputs_dir / "3d" / output_name
        
        kamui_prompt = f"""
{prompt}をテーマにした3Dモデルを生成してください。

設定:
- 複雑さ: {complexity}
- 高品質で生成してください

生成完了したら、必ず以下を実行してください:
1. ダウンロードURLのフルパス表示（省略なし）
2. 今いるディレクトリ（{output_path.parent}）にダウンロード
3. ダウンロード完了後にopenコマンドで開く

保存したファイルの場所は~からのフルパスで表示してください。
"""
        
        print(f"🗿 Generating 3D model: {prompt}")
        response = self.call_claude_with_kamui(kamui_prompt)
        
        # URLを抽出してダウンロード
        urls = self.extract_urls_from_response(response)
        if urls:
            downloaded_file = self.download_file(urls[0], output_path)
            if downloaded_file:
                return downloaded_file
        
        print("⚠️ No download URL found in response")
        return str(output_path)
    
    def image_to_video(self, image_path, motion_prompt="gentle movement", duration=5, output_name=None):
        """画像から動画生成"""
        if output_name is None:
            output_name = f"i2v_{hash(motion_prompt) % 10000}.mp4"
        
        output_path = self.outputs_dir / "videos" / output_name
        
        # 画像のフルパスを取得
        image_full_path = Path(image_path).resolve()
        
        kamui_prompt = f"""
画像から動画を生成してください。

入力画像: {image_full_path}
モーション: {motion_prompt}
継続時間: {duration}秒

※入力URLはgoogleからのものを使ってください（省略なし）。

生成完了したら、必ず以下を実行してください:
1. ダウンロードURLのフルパス表示（省略なし）
2. 今いるディレクトリ（{output_path.parent}）にダウンロード
3. ダウンロード完了後にopenコマンドで開く

保存したファイルの場所は~からのフルパスで表示してください。
"""
        
        print(f"🎬 Converting image to video: {image_path}")
        response = self.call_claude_with_kamui(kamui_prompt)
        
        # URLを抽出してダウンロード
        urls = self.extract_urls_from_response(response)
        if urls:
            downloaded_file = self.download_file(urls[0], output_path)
            if downloaded_file:
                return downloaded_file
        
        print("⚠️ No download URL found in response")
        return str(output_path)