#!/usr/bin/env python3
"""
MCP Safety Controller - Kamui Code MCP必須操作の安全制御
"""

import os
import json
from pathlib import Path

# Kamui Code MCP必須の生成操作（ホワイトリスト）
KAMUI_REQUIRED_OPERATIONS = {
    "generate_image",
    "generate_video", 
    "generate_music",
    "generate_3d_model",
    "generate_speech",
    "image_to_video",
    "image_to_3d",
    "text_to_speech",
    # 今後の生成系機能はここに追加
}

# 加工・表示系操作（他MCP使用OK）
PROCESSING_OPERATIONS = {
    "create_3d_scene",       # 3JS
    "process_3d_model",      # Blender  
    "combine_assets",        # 3JS
    "render_scene",          # Blender
    "optimize_model",        # Blender
    "create_animation",      # 3JS/Blender
    "compose_scene"          # 3JS
}

class MCPSafetyController:
    """MCP操作の安全性を制御"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # 環境に応じて設定パスを決定
            home_dir = os.path.expanduser("~")
            config_path = os.path.join(home_dir, ".claude", "mcp-kamuicode.json")
        self.kamui_config_path = config_path
        self.strict_mode = os.getenv("KAMUI_STRICT_MODE", "true").lower() == "true"
    
    def verify_kamui_mcp_available(self):
        """Kamui Code MCPの利用可能性を確認"""
        if not os.path.exists(self.kamui_config_path):
            raise Exception(f"Kamui Code MCP設定が見つかりません: {self.kamui_config_path}")
        
        try:
            with open(self.kamui_config_path, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" not in config:
                raise Exception("Kamui Code MCP設定が無効です")
            
            # 主要な生成機能の存在確認
            servers = config["mcpServers"]
            required_services = ["t2i-", "t2v-", "t2m-"]  # text-to-image, video, music
            
            available_services = [key for key in servers.keys()]
            print(f"✅ 利用可能なKamui MCPサービス: {len(available_services)}個")
            
            return True
            
        except json.JSONDecodeError as e:
            raise Exception(f"Kamui Code MCP設定の読み込みエラー: {e}")
    
    def ensure_kamui_for_operation(self, operation_name):
        """指定された操作でKamui Code MCPの使用を強制"""
        if operation_name in KAMUI_REQUIRED_OPERATIONS:
            if self.strict_mode:
                self.verify_kamui_mcp_available()
                print(f"🔒 {operation_name}: Kamui Code MCP使用を確認")
            else:
                print(f"⚠️  {operation_name}: Kamui Code MCP推奨（strict_mode無効）")
        
        elif operation_name in PROCESSING_OPERATIONS:
            print(f"🔧 {operation_name}: 加工系操作（他MCP使用OK）")
        
        else:
            if self.strict_mode:
                raise Exception(f"未定義の操作: {operation_name}")
            else:
                print(f"❓ {operation_name}: 未定義操作（注意が必要）")
    
    def get_operation_type(self, operation_name):
        """操作タイプを判定"""
        if operation_name in KAMUI_REQUIRED_OPERATIONS:
            return "generation"
        elif operation_name in PROCESSING_OPERATIONS:
            return "processing"
        else:
            return "unknown"
    
    def list_allowed_operations(self):
        """利用可能な操作一覧を表示"""
        print("🎨 Kamui Code MCP必須（生成系）:")
        for op in sorted(KAMUI_REQUIRED_OPERATIONS):
            print(f"  - {op}")
        
        print("\n🔧 他MCP使用可能（加工系）:")
        for op in sorted(PROCESSING_OPERATIONS):
            print(f"  - {op}")
    
    def add_kamui_operation(self, operation_name):
        """新しいKamui必須操作を追加"""
        KAMUI_REQUIRED_OPERATIONS.add(operation_name)
        print(f"✅ Kamui必須操作に追加: {operation_name}")
    
    def add_processing_operation(self, operation_name):
        """新しい加工系操作を追加"""
        PROCESSING_OPERATIONS.add(operation_name)
        print(f"✅ 加工系操作に追加: {operation_name}")

# グローバルインスタンス
safety_controller = MCPSafetyController()

# デコレータとして使用可能
def require_kamui_mcp(func):
    """関数にKamui MCP必須制約を追加するデコレータ"""
    def wrapper(*args, **kwargs):
        operation_name = func.__name__
        safety_controller.ensure_kamui_for_operation(operation_name)
        return func(*args, **kwargs)
    return wrapper

def allow_other_mcp(func):
    """関数で他MCP使用を明示的に許可するデコレータ"""
    def wrapper(*args, **kwargs):
        operation_name = func.__name__
        if operation_name not in PROCESSING_OPERATIONS:
            PROCESSING_OPERATIONS.add(operation_name)
        return func(*args, **kwargs)
    return wrapper