#!/usr/bin/env python3
"""
Kamui MCP テストスクリプト
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_safety import safety_controller
from kamui_client import KamuiMCPClient

def test_kamui_connection():
    """Kamui MCP接続テスト"""
    print("🔒 Testing Kamui Code MCP connection...")
    
    try:
        # 安全性チェック
        safety_controller.verify_kamui_mcp_available()
        print("✅ Kamui Code MCP configuration found")
        
        # クライアント作成
        client = KamuiMCPClient()
        print("✅ Kamui client initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Kamui MCP test failed: {e}")
        return False

def test_simple_generation():
    """簡単な生成テスト"""
    print("\n🎨 Testing simple image generation...")
    
    try:
        client = KamuiMCPClient()
        
        # 小さなテスト画像を生成
        result = client.generate_image(
            prompt="A simple red circle",
            style="minimal",
            output_name="test_circle.jpg"
        )
        
        print(f"✅ Test generation completed: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def test_safety_controls():
    """安全制御のテスト"""
    print("\n🔒 Testing safety controls...")
    
    try:
        # 利用可能な操作一覧
        safety_controller.list_allowed_operations()
        
        # 操作タイプの確認
        gen_type = safety_controller.get_operation_type("generate_image")
        proc_type = safety_controller.get_operation_type("create_3d_scene")
        
        print(f"✅ generate_image type: {gen_type}")
        print(f"✅ create_3d_scene type: {proc_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Safety test failed: {e}")
        return False

def main():
    print("🧪 Creative Factory - Kamui MCP Test Suite")
    print("=" * 50)
    
    tests = [
        ("Connection Test", test_kamui_connection),
        ("Safety Controls Test", test_safety_controls),
        ("Simple Generation Test", test_simple_generation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Kamui MCP is ready.")
    else:
        print("⚠️ Some tests failed. Check configuration.")

if __name__ == "__main__":
    main()