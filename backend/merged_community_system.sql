-- 社区门禁管理系统数据库合并脚本
-- 创建时间: 2023-12-10
-- 版本: 1.1 (合并版)

-- 使用数据库
USE community_system;

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    phone VARCHAR(20) COMMENT '手机号',
    name VARCHAR(100) COMMENT '真实姓名',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 创建角色表
CREATE TABLE IF NOT EXISTS roles (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '角色名称',
    description VARCHAR(255) COMMENT '角色描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 3. 创建权限表
CREATE TABLE IF NOT EXISTS permissions (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '权限ID',
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '权限名称',
    description VARCHAR(255) COMMENT '权限描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 4. 创建用户-角色关联表
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INT NOT NULL COMMENT '用户ID',
    role_id INT NOT NULL COMMENT '角色ID',
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- 5. 创建角色-权限关联表
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INT NOT NULL COMMENT '角色ID',
    permission_id INT NOT NULL COMMENT '权限ID',
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE,
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- 6. 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '设备ID',
    device_code VARCHAR(50) NOT NULL UNIQUE COMMENT '设备编号',
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_type VARCHAR(50) NOT NULL COMMENT '设备类型',
    location VARCHAR(255) NOT NULL COMMENT '安装位置',
    status VARCHAR(20) DEFAULT '正常' COMMENT '设备状态',
    ip_address VARCHAR(50) COMMENT '设备IP地址',
    mac_address VARCHAR(50) COMMENT 'MAC地址',
    last_online_time DATETIME COMMENT '最后在线时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_device_code (device_code),
    INDEX idx_device_type (device_type),
    INDEX idx_location (location),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 7. 创建门禁记录表
CREATE TABLE IF NOT EXISTS access_records (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
    device_id INT NOT NULL COMMENT '设备ID',
    user_id INT COMMENT '用户ID',
    card_id VARCHAR(50) COMMENT '卡号',
    access_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
    access_result BOOLEAN DEFAULT FALSE COMMENT '通行结果',
    reason VARCHAR(255) COMMENT '失败原因',
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_device_id (device_id),
    INDEX idx_user_id (user_id),
    INDEX idx_access_time (access_time),
    INDEX idx_access_result (access_result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='门禁记录表';

-- 8. 创建操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID',
    user_id INT COMMENT '操作人ID',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id VARCHAR(100) COMMENT '资源ID',
    details TEXT COMMENT '操作详情',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent VARCHAR(255) COMMENT '客户端信息',
    success INT DEFAULT 1 COMMENT '操作结果(1成功，0失败)',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- 插入角色数据（合并两个文件的数据）
INSERT IGNORE INTO roles (name, description) VALUES
('管理员', '系统管理员，拥有所有权限'),
('物业', '物业管理人员，负责设备管理和用户管理'),
('住户', '小区住户，拥有基本访问权限'),
('admin', '系统管理员'),
('property', '物业人员'),
('resident', '住户');

-- 插入权限数据（合并两个文件的数据，保持一致）
INSERT IGNORE INTO permissions (name, description) VALUES
('user:read', '查看用户信息'),
('user:create', '创建用户'),
('user:update', '更新用户信息'),
('user:delete', '删除用户'),
('device:read', '查看设备信息'),
('device:create', '创建设备'),
('device:update', '更新设备信息'),
('device:delete', '删除设备'),
('role:read', '查看角色信息'),
('role:create', '创建角色'),
('role:update', '更新角色信息'),
('role:delete', '删除角色'),
('permission:read', '查看权限信息'),
('permission:create', '创建权限'),
('permission:update', '更新权限信息'),
('permission:delete', '删除权限'),
('access_record:read', '查看门禁记录'),
('access_record:create', '创建门禁记录'),
('log:read', '查看操作日志'),
('log:create', '创建操作日志');

-- 创建默认管理员用户（密码：admin123，加密后的哈希值）
INSERT IGNORE INTO users (username, email, password_hash, name, is_active) VALUES
('admin', 'admin@example.com', 'admin123', '管理员', TRUE);

-- 插入额外的示例用户
INSERT IGNORE INTO users (username, email, password_hash, name, is_active) VALUES
('user', 'user@example.com', 'user123', '普通用户', TRUE),
('property', 'property@example.com', 'property123', '物业管理员', TRUE),
('resident', 'resident@example.com', 'resident123', '小区住户', TRUE);

-- 合并设备数据
INSERT IGNORE INTO devices (device_code, device_name, device_type, location, status) VALUES
('DEV001', '南门门禁', '门禁', '小区南门', '正常'),
('DEV002', '北门门禁', '门禁', '小区北门', '正常'),
('DEV003', '东门摄像头', '摄像头', '小区东门', '正常'),
('DEV004', '地下车库入口道闸', '道闸', '地下车库入口', '正常'),
('DEV005', '1号楼电梯', '电梯', '1号楼', '维护'),
('DEV006', '车库门禁', '门禁', '车库', '正常');

-- 为管理员角色分配所有权限（处理两个角色名称）
-- 管理员：拥有系统所有功能的完整权限
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name IN ('管理员', 'admin');

-- 为物业角色分配权限
-- 物业：负责用户和设备管理，查看门禁记录和日志
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name IN ('物业', 'property')
AND p.name IN ('user:read', 'user:create', 'user:update', 
               'device:read', 'device:create', 'device:update', 'device:delete', 
               'access_record:read', 'access_record:create',
               'log:read', 'log:create');

-- 为住户角色分配基本权限
-- 住户：只能查看和更新自己的信息，查看门禁记录
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id 
FROM roles r, permissions p 
WHERE r.name IN ('住户', 'resident')
AND p.name IN ('user:read', 'user:update', 'access_record:read');

-- 移除重复或冲突的角色权限关联
DELETE FROM role_permissions 
WHERE (role_id, permission_id) IN (
    SELECT r.id, p.id 
    FROM roles r, permissions p 
    WHERE r.name IN ('住户', 'resident')
    AND p.name IN ('user:create', 'user:delete', 'device:read', 'device:create', 
                   'device:update', 'device:delete', 'role:read', 'role:create', 
                   'role:update', 'role:delete', 'permission:read', 'permission:create', 
                   'permission:update', 'permission:delete', 'access_record:create', 
                   'log:read', 'log:create')
);

-- 为用户分配角色
INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'admin' AND r.name IN ('管理员', 'admin');

INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username = 'property' AND r.name IN ('物业', 'property');

INSERT IGNORE INTO user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM users u, roles r 
WHERE u.username IN ('user', 'resident') AND r.name IN ('住户', 'resident');

-- 插入一些示例门禁记录
INSERT INTO access_records (device_id, user_id, access_result)
SELECT 1, u.id, TRUE 
FROM users u 
WHERE u.username = 'admin'
LIMIT 1;

INSERT INTO access_records (device_id, access_result, reason)
VALUES (2, FALSE, '未授权用户');

-- 插入一些操作日志记录
INSERT INTO operation_logs (user_id, action, resource_type, details, ip_address, success)
SELECT u.id, 'login', 'auth', '{"username": "admin"}', '127.0.0.1', 1 
FROM users u 
WHERE u.username = 'admin'
LIMIT 1;

-- 显示创建结果
SELECT '数据库初始化完成' AS result;
SELECT '===========================================' AS divider;
SELECT '创建的表：' AS info;
SHOW TABLES;
SELECT '===========================================' AS divider;
SELECT '默认管理员账号：admin / admin123' AS admin_info;
SELECT '普通用户账号：user / user123' AS user_info;