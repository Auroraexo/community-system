#!/usr/bin/env python3
"""
用户密码迁移脚本
将明文密码迁移到bcrypt加密
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# 添加后端目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.database import engine, SessionLocal, get_db
from src.models.user import User
from src.utils.auth import get_password_hash
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_password_strength(password: str) -> bool:
    """检查密码是否需要迁移（简单判断是否是bcrypt哈希）"""
    # bcrypt哈希通常以 $2b$ 开头
    return not password.startswith("$2b$")

def migrate_user_passwords():
    """迁移用户密码到bcrypt加密"""
    print("🔐 用户密码迁移工具")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # 获取所有用户
        users = db.query(User).all()
        total_users = len(users)
        migrated_users = 0
        skipped_users = 0
        
        print(f"发现 {total_users} 个用户")
        
        for user in users:
            if check_password_strength(user.password_hash):
                print(f"正在迁移用户: {user.username} (ID: {user.id})")
                
                # 生成新的bcrypt哈希
                new_hash = get_password_hash(user.password_hash)
                user.password_hash = new_hash
                
                migrated_users += 1
                print(f"✅ 已迁移: {user.username}")
            else:
                skipped_users += 1
                print(f"⏭️  跳过: {user.username} (已经是bcrypt哈希)")
        
        # 提交更改
        db.commit()
        
        print("\n" + "=" * 50)
        print("📊 迁移完成统计:")
        print(f"- 总用户数: {total_users}")
        print(f"- 已迁移: {migrated_users}")
        print(f"- 已跳过: {skipped_users}")
        print(f"- 成功率: {(migrated_users/total_users*100):.1f}%")
        
        if migrated_users > 0:
            print("\n✅ 密码迁移成功完成！")
            print("⚠️  注意：请通知用户他们的密码仍然有效，但现在已经安全加密")
        else:
            print("\nℹ️  所有密码已经是加密状态，无需迁移")
            
    except Exception as e:
        db.rollback()
        print(f"❌ 迁移失败: {e}")
        logger.error(f"密码迁移失败: {e}", exc_info=True)
    finally:
        db.close()

def verify_migration():
    """验证迁移结果"""
    print("\n🔍 验证迁移结果...")
    
    db = SessionLocal()
    try:
        users = db.query(User).limit(5).all()  # 检查前5个用户
        
        for user in users:
            is_encrypted = user.password_hash.startswith("$2b$")
            status = "✅ 已加密" if is_encrypted else "❌ 未加密"
            print(f"- {user.username}: {status}")
            
    except Exception as e:
        print(f"验证失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # 确认提示
    print("⚠️  警告：此操作将更新所有用户的密码加密方式")
    print("- 现有密码将继续有效")
    print("- 密码将被迁移到更安全的bcrypt加密")
    print("- 建议在操作前备份数据库")
    
    confirm = input("\n是否继续？(yes/no): ")
    if confirm.lower() == "yes":
        migrate_user_passwords()
        verify_migration()
    else:
        print("操作已取消")