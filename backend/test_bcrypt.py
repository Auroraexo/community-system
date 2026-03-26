#!/usr/bin/env python3
"""测试bcrypt密码加密功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.auth import get_password_hash, verify_password

def test_bcrypt_functionality():
    """测试bcrypt功能"""
    print("🧪 测试bcrypt密码加密功能...")
    
    # 测试密码
    test_passwords = [
        "test123456",
        "password123",
        "mysecurepassword",
        "短密码",
        "这是一个很长的密码用于测试bcrypt的72字节截断功能"
    ]
    
    for password in test_passwords:
        print(f"\n测试密码: {password}")
        
        # 生成哈希
        try:
            hashed = get_password_hash(password)
            print(f"生成的哈希: {hashed[:50]}...")
            print(f"哈希长度: {len(hashed)}")
            
            # 验证密码
            is_valid = verify_password(password, hashed)
            print(f"密码验证: {'✅ 成功' if is_valid else '❌ 失败'}")
            
            # 测试错误密码
            wrong_valid = verify_password("wrongpassword", hashed)
            print(f"错误密码验证: {'❌ 正确拒绝' if not wrong_valid else '❌ 错误接受'}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n🎉 bcrypt功能测试完成！")

if __name__ == "__main__":
    test_bcrypt_functionality()