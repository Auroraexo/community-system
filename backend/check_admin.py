import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 加载环境变量
load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 创建引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建会话
db = SessionLocal()

try:
    # 查询admin用户
    admin_user = db.execute(text("SELECT * FROM users WHERE username = 'admin'")).fetchone()
    print("Admin User:")
    print(f"ID: {admin_user[0]}, Username: {admin_user[1]}, Email: {admin_user[2]}, Name: {admin_user[4]}, Is Active: {admin_user[6]}")
    
    # 查询admin用户的角色
    roles_query = text("""
        SELECT r.* 
        FROM roles r
        JOIN user_roles ur ON r.id = ur.role_id
        JOIN users u ON ur.user_id = u.id
        WHERE u.username = 'admin'
    """)
    admin_roles = db.execute(roles_query).fetchall()
    print("\nAdmin Roles:")
    for role in admin_roles:
        print(f"Role ID: {role[0]}, Role Name: {role[1]}")
    
    # 查询角色的权限
    permissions_query = text("""
        SELECT p.*
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN roles r ON rp.role_id = r.id
        JOIN user_roles ur ON r.id = ur.role_id
        JOIN users u ON ur.user_id = u.id
        WHERE u.username = 'admin'
    """)
    admin_permissions = db.execute(permissions_query).fetchall()
    print("\nAdmin Permissions:")
    for perm in admin_permissions:
        print(f"Permission ID: {perm[0]}, Permission Name: {perm[1]}")
        
finally:
    db.close()