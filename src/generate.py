#!/usr/bin/env python3
"""
Creative Factory - Multi-MCP Content Generation Script
Kamui Code, 3JS, Blender MCPを連携してクリエイティブ作品を生成
"""

import os
import sys
import argparse
import json
from pathlib import Path
from mcp_safety import safety_controller, require_kamui_mcp, allow_other_mcp
from kamui_client import KamuiMCPClient

def setup_environment():
    """環境設定とパスの準備"""
    project_root = Path(__file__).parent.parent
    outputs_dir = project_root / "outputs"
    
    # 出力ディレクトリを作成
    for subdir in ["images", "videos", "audio", "3d"]:
        (outputs_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    return project_root, outputs_dir

# グローバルKamuiクライアント
kamui_client = KamuiMCPClient()

@require_kamui_mcp
def generate_image(prompt, style="photorealistic"):
    """Kamui Code MCPで画像生成（Kamui必須）"""
    return kamui_client.generate_image(prompt, style=style)

@require_kamui_mcp
def generate_video(prompt, duration=5):
    """Kamui Code MCPで動画生成（Kamui必須）"""
    return kamui_client.generate_video(prompt, duration=duration)

@require_kamui_mcp
def generate_music(prompt, duration=30):
    """Kamui Code MCPで音楽生成（Kamui必須）"""
    return kamui_client.generate_music(prompt, duration=duration)

@require_kamui_mcp
def generate_3d_model(prompt, complexity="medium"):
    """Kamui Code MCPで3Dモデル生成（Kamui必須）"""
    return kamui_client.generate_3d_model(prompt, complexity=complexity)

@allow_other_mcp
def create_3d_scene(assets, scene_config):
    """3JS MCPで3Dシーン作成（他MCP使用OK）"""
    print(f"Creating 3D scene with {len(assets)} assets")
    
    # 3JS MCP呼び出し（実装予定）
    
    return "outputs/3d/scene.html"

@allow_other_mcp
def process_with_blender(model_path, operations):
    """Blender MCPで3D処理（他MCP使用OK）"""
    print(f"Processing 3D model: {model_path}")
    print(f"Operations: {operations}")
    
    # Blender MCP呼び出し（実装予定）
    
    return "outputs/3d/processed_model.blend"

def main():
    parser = argparse.ArgumentParser(description="Creative Factory Content Generator")
    parser.add_argument("--type", choices=["image", "video", "music", "3d", "all"], 
                       default="image", help="Content type to generate")
    parser.add_argument("--prompt", default="Beautiful landscape", help="Generation prompt")
    parser.add_argument("--output", help="Output filename")
    parser.add_argument("--list-operations", action="store_true", help="List all available operations")
    
    args = parser.parse_args()
    
    if args.list_operations:
        safety_controller.list_allowed_operations()
        return
    
    # 安全性チェックを最初に実行
    print("🔒 Checking Kamui Code MCP availability...")
    try:
        safety_controller.verify_kamui_mcp_available()
        print("✅ Kamui Code MCP ready")
    except Exception as e:
        print(f"❌ Kamui Code MCP error: {e}")
        sys.exit(1)
    
    project_root, outputs_dir = setup_environment()
    
    print(f"🎨 Creative Factory - Generating {args.type} content...")
    print(f"📝 Prompt: {args.prompt}")
    
    generated_files = []
    
    if args.type in ["image", "all"]:
        image_file = generate_image(args.prompt)
        generated_files.append(image_file)
    
    if args.type in ["video", "all"]:
        video_file = generate_video(args.prompt)
        generated_files.append(video_file)
    
    if args.type in ["music", "all"]:
        music_file = generate_music(args.prompt)
        generated_files.append(music_file)
    
    if args.type in ["3d", "all"]:
        # 3Dモデル生成（Kamui必須）+ 3Dシーン作成（他MCP OK）
        model_file = generate_3d_model(args.prompt)
        generated_files.append(model_file)
        
        # 生成した素材を組み合わせて3Dシーン作成
        scene_file = create_3d_scene(generated_files, {"lighting": "ambient"})
        generated_files.append(scene_file)
    
    print(f"✅ Generated {len(generated_files)} files:")
    for file in generated_files:
        print(f"  📄 {file}")

if __name__ == "__main__":
    main()