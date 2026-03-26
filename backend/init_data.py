"""初始化默认数据脚本"""
import sys
import os
from sqlalchemy.orm import Session

# 添加当前目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import engine, SessionLocal, Base
from src.models.user import User, Role, Permission

def init_db():
    """初始化数据库，创建默认角色和权限"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        if db.query(Role).count() > 0:
            print("数据库已有初始化数据，跳过初始化")
            return
        
        print("开始初始化默认数据...")
        
        # 创建权限
        permissions = [
            # 用户管理权限
            Permission(name="user:read", description="读取用户信息"),
            Permission(name="user:create", description="创建用户"),
            Permission(name="user:update", description="更新用户信息"),
            Permission(name="user:delete", description="删除用户"),
            
            # 设备管理权限
            Permission(name="device:read", description="读取设备信息"),
            Permission(name="device:create", description="创建设备"),
            Permission(name="device:update", description="更新设备信息"),
            Permission(name="device:delete", description="删除设备"),
            
            # 门禁记录权限
            Permission(name="access:read", description="读取门禁记录"),
            Permission(name="access:delete", description="删除门禁记录"),
            Permission(name="access:export", description="导出门禁记录"),
            Permission(name="access:cleanup", description="清理门禁记录"),
            
            # 日志管理权限
            Permission(name="log:read", description="读取操作日志"),
            Permission(name="log:delete", description="删除操作日志"),
            
            # 角色管理权限
            Permission(name="role:read", description="读取角色信息"),
            Permission(name="role:create", description="创建角色"),
            Permission(name="role:update", description="更新角色信息"),
            Permission(name="role:delete", description="删除角色"),
        ]
        
        for perm in permissions:
            db.add(perm)
        db.commit()
        
        # 创建角色
        roles = {
            "管理员": ["user:read", "user:create", "user:update", "user:delete",
                      "device:read", "device:create", "device:update", "device:delete",
                      "access:read", "access:delete", "access:export", "access:cleanup",
                      "log:read", "log:delete",
                      "role:read", "role:create", "role:update", "role:delete"],
            "物业": ["user:read", "user:update",
                    "device:read", "device:update",
                    "access:read", "access:export",
                    "log:read"],
            "住户": []  # 住户默认无特殊权限
        }
        
        role_objects = {}
        for role_name, perm_names in roles.items():
            role = Role(name=role_name)
            
            # 为角色分配权限
            for perm_name in perm_names:
                perm = db.query(Permission).filter(Permission.name == perm_name).first()
                if perm:
                    role.permissions.append(perm)
            
            db.add(role)
            role_objects[role_name] = role
        
        db.commit()
        
        # 创建默认管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            name="系统管理员",
            password_hash="admin123",  # 明文密码
            is_active=True
        )
        
        # 为管理员分配角色
        admin_role = role_objects.get("管理员")
        if admin_role:
            admin_user.roles.append(admin_role)
        
        db.add(admin_user)
        db.commit()
        
        print("默认数据初始化完成！")
        print("- 默认管理员账号: admin")
        print("- 默认密码: admin123")
        print("- 已创建角色: 管理员、物业、住户")
        
    except Exception as e:
        import traceback
        print(f"初始化数据时出错: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()