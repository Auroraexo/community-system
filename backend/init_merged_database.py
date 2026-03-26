#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社区门禁管理系统 - 数据库初始化脚本
功能：使用合并后的SQL文件初始化MySQL数据库
"""

import os
import sys
import logging
import pymysql
import pymysql.cursors
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',  # 默认密码
    'port': 3306,
    'charset': 'utf8mb4'
}

DATABASE_NAME = 'community_system'
SQL_FILE_PATH = 'merged_community_system.sql'

def create_database():
    """创建数据库"""
    try:
        # 先连接到MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            **DB_CONFIG,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        logger.info(f"数据库 '{DATABASE_NAME}' 创建成功（如果不存在）")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"创建数据库失败: {str(e)}")
        return False

def execute_sql_script(script_path):
    """执行SQL脚本文件"""
    try:
        # 连接到指定数据库
        conn = pymysql.connect(
            **DB_CONFIG,
            database=DATABASE_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        
        # 读取SQL文件内容
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 分割SQL语句（处理分号分隔的语句）
        sql_statements = []
        current_statement = ""
        
        for line in sql_script.split('\n'):
            # 跳过注释行和空行
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement += line + '\n'
            
            # 如果遇到分号并且不在字符串内，执行当前语句
            if ';' in current_statement and current_statement.count('"') % 2 == 0 and current_statement.count("'") % 2 == 0:
                sql_statements.append(current_statement.strip())
                current_statement = ""
        
        # 执行所有SQL语句
        for i, statement in enumerate(sql_statements):
            try:
                cursor.execute(statement)
                # 对于SELECT语句，打印结果
                if statement.strip().upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    if results:
                        logger.info(f"SQL语句 {i+1} 结果:")
                        for row in results:
                            for key, value in row.items():
                                logger.info(f"  {key}: {value}")
                conn.commit()
            except Exception as e:
                logger.warning(f"执行SQL语句 {i+1} 时出错: {str(e)}")
                logger.debug(f"出错的SQL语句: {statement}")
                # 继续执行其他语句
        
        cursor.close()
        conn.close()
        logger.info("SQL脚本执行完成")
        return True
    except Exception as e:
        logger.error(f"执行SQL脚本失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 社区门禁管理系统 - 数据库初始化工具")
    print("=" * 50)
    print(f"将使用以下配置创建数据库:")
    print(f"- 主机: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"- 用户名: {DB_CONFIG['user']}")
    print(f"- 数据库名: {DATABASE_NAME}")
    print(f"- SQL文件: {SQL_FILE_PATH}")
    print("\n正在初始化数据库...")
    
    # 检查SQL文件是否存在
    sql_file = Path(SQL_FILE_PATH)
    if not sql_file.exists():
        logger.error(f"SQL文件 '{SQL_FILE_PATH}' 不存在")
        print("❌ 错误: SQL文件不存在")
        return False
    
    # 创建数据库
    if not create_database():
        print("❌ 数据库创建失败，请检查MySQL连接配置")
        print("\n提示:")
        print("1. 请确保MySQL服务器已启动")
        print("2. 检查用户名和密码是否正确")
        print(f"3. 当前配置用户名: {DB_CONFIG['user']}, 密码: {DB_CONFIG['password']}")
        print("4. 确保用户有创建数据库的权限")
        return False
    
    # 执行SQL脚本
    if not execute_sql_script(SQL_FILE_PATH):
        print("❌ SQL脚本执行失败，请检查SQL文件内容")
        return False
    
    print("\n✅ 数据库初始化成功！")
    print("\n📋 系统信息:")
    print(f"- 数据库: {DATABASE_NAME}")
    print(f"- 默认管理员账号: admin / admin123")
    print(f"- 普通用户账号: user / user123")
    print(f"- 物业管理员账号: property / property123")
    print(f"- 小区住户账号: resident / resident123")
    print("\n💡 注意事项:")
    print("1. 请在生产环境中修改默认密码")
    print("2. 数据库连接信息已在.env文件中配置")
    print("3. 现在可以启动后端服务了")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)