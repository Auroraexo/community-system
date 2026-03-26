/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80033
 Source Host           : localhost:3306
 Source Schema         : community_system

 Target Server Type    : MySQL
 Target Server Version : 80033
 File Encoding         : 65001

 Date: 15/12/2025 14:13:43
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for access_records
-- ----------------------------
DROP TABLE IF EXISTS `access_records`;
CREATE TABLE `access_records`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `device_id` int NOT NULL COMMENT '设备ID',
  `user_id` int NULL DEFAULT NULL COMMENT '用户ID',
  `card_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '卡号',
  `access_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
  `access_result` tinyint(1) NULL DEFAULT 0 COMMENT '通行结果',
  `reason` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '失败原因',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_device_id`(`device_id` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_access_time`(`access_time` ASC) USING BTREE,
  INDEX `idx_access_result`(`access_result` ASC) USING BTREE,
  CONSTRAINT `access_records_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `devices` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `access_records_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '门禁记录表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of access_records
-- ----------------------------
INSERT INTO `access_records` VALUES (1, 1, 1, '1221323', '2025-10-28 20:43:00', 1, NULL);
INSERT INTO `access_records` VALUES (3, 1, 1, NULL, '2025-10-28 20:43:05', 1, NULL);
INSERT INTO `access_records` VALUES (4, 2, NULL, NULL, '2025-10-28 20:43:05', 0, '未授权用户');
INSERT INTO `access_records` VALUES (6, 2, NULL, NULL, '2025-10-28 20:51:00', 0, '未授权用户');

-- ----------------------------
-- Table structure for devices
-- ----------------------------
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '设备ID',
  `device_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备编号',
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备名称',
  `device_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '设备类型',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '安装位置',
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '正常' COMMENT '设备状态',
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '设备IP地址',
  `mac_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'MAC地址',
  `last_online_time` datetime NULL DEFAULT NULL COMMENT '最后在线时间',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `device_code`(`device_code` ASC) USING BTREE,
  INDEX `idx_device_code`(`device_code` ASC) USING BTREE,
  INDEX `idx_device_type`(`device_type` ASC) USING BTREE,
  INDEX `idx_location`(`location` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '设备表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of devices
-- ----------------------------
INSERT INTO `devices` VALUES (1, 'DEV001', '南门门禁', '门禁', '小区南门2', 'online', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-11-11 15:04:13');
INSERT INTO `devices` VALUES (2, 'DEV002', '北门门禁', '门禁', '小区北门', 'online', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-11-11 15:04:25');
INSERT INTO `devices` VALUES (3, 'DEV003', '东门摄像头', '摄像头', '小区东门', 'online', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-11-11 16:07:45');
INSERT INTO `devices` VALUES (4, 'DEV004', '地下车库入口道闸', '道闸', '地下车库入口', 'online', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-11-11 16:47:07');
INSERT INTO `devices` VALUES (5, 'DEV005', '1号楼电梯', '电梯', '1号楼', 'online', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-11-11 17:52:41');
INSERT INTO `devices` VALUES (6, 'DEV006', '车库门禁', '门禁', '车库', 'disabled', NULL, NULL, NULL, '2025-10-28 20:43:00', '2025-10-28 22:24:15');

-- ----------------------------
-- Table structure for operation_logs
-- ----------------------------
DROP TABLE IF EXISTS `operation_logs`;
CREATE TABLE `operation_logs`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` int NULL DEFAULT NULL COMMENT '操作人ID',
  `action` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '操作类型',
  `resource_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '资源类型',
  `resource_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '资源ID',
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '操作详情',
  `ip_address` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'IP地址',
  `user_agent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '客户端信息',
  `success` int NULL DEFAULT 1 COMMENT '操作结果(1成功，0失败)',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '错误信息',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_action`(`action` ASC) USING BTREE,
  INDEX `idx_resource_type`(`resource_type` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE,
  CONSTRAINT `operation_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 722 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '操作日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of operation_logs
-- ----------------------------
INSERT INTO `operation_logs` VALUES (639, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 17:59:09');
INSERT INTO `operation_logs` VALUES (640, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:01:23');
INSERT INTO `operation_logs` VALUES (641, 1, 'view', 'device', NULL, '{\"page\": 1, \"page_size\": 10, \"device_type\": null, \"status\": \"\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:01:30');
INSERT INTO `operation_logs` VALUES (642, 1, 'view_stats', 'access_record', NULL, '{\"stats_type\": \"summary\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:01:34');
INSERT INTO `operation_logs` VALUES (643, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:02:11');
INSERT INTO `operation_logs` VALUES (644, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:02:27');
INSERT INTO `operation_logs` VALUES (645, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 65, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:02:51');
INSERT INTO `operation_logs` VALUES (646, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 60, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:02:55');
INSERT INTO `operation_logs` VALUES (647, 1, 'view_stats', 'access_record', NULL, '{\"stats_type\": \"summary\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:03:14');
INSERT INTO `operation_logs` VALUES (648, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:05');
INSERT INTO `operation_logs` VALUES (649, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:05');
INSERT INTO `operation_logs` VALUES (650, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:09');
INSERT INTO `operation_logs` VALUES (651, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 2, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:14');
INSERT INTO `operation_logs` VALUES (652, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:15');
INSERT INTO `operation_logs` VALUES (653, 1, 'logout', 'auth', NULL, '{\"username\": \"admin\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:23');
INSERT INTO `operation_logs` VALUES (654, 1, 'login', 'auth', NULL, '{\"username\": \"admin\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:25');
INSERT INTO `operation_logs` VALUES (655, 1, 'view_stats', 'access_record', NULL, '{\"stats_type\": \"summary\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:25');
INSERT INTO `operation_logs` VALUES (656, 1, 'view', 'device', NULL, '{\"page\": 1, \"page_size\": 10, \"device_type\": null, \"status\": \"\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:05:27');
INSERT INTO `operation_logs` VALUES (657, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:07:23');
INSERT INTO `operation_logs` VALUES (658, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:08:01');
INSERT INTO `operation_logs` VALUES (659, 1, 'view', 'device', NULL, '{\"page\": 1, \"page_size\": 10, \"device_type\": null, \"status\": \"\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:08:15');
INSERT INTO `operation_logs` VALUES (660, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:09:32');
INSERT INTO `operation_logs` VALUES (661, 1, 'view', 'device', NULL, '{\"page\": 1, \"page_size\": 10, \"device_type\": null, \"status\": \"\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:10:05');
INSERT INTO `operation_logs` VALUES (662, 1, 'view_stats', 'access_record', NULL, '{\"stats_type\": \"summary\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:11:25');
INSERT INTO `operation_logs` VALUES (663, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:11:32');
INSERT INTO `operation_logs` VALUES (664, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:12:26');
INSERT INTO `operation_logs` VALUES (665, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:54');
INSERT INTO `operation_logs` VALUES (666, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:56');
INSERT INTO `operation_logs` VALUES (667, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:56');
INSERT INTO `operation_logs` VALUES (668, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:57');
INSERT INTO `operation_logs` VALUES (669, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:57');
INSERT INTO `operation_logs` VALUES (670, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:59');
INSERT INTO `operation_logs` VALUES (671, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:13:59');
INSERT INTO `operation_logs` VALUES (672, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:00');
INSERT INTO `operation_logs` VALUES (673, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:00');
INSERT INTO `operation_logs` VALUES (674, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:00');
INSERT INTO `operation_logs` VALUES (675, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:00');
INSERT INTO `operation_logs` VALUES (676, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:01');
INSERT INTO `operation_logs` VALUES (677, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:01');
INSERT INTO `operation_logs` VALUES (678, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:02');
INSERT INTO `operation_logs` VALUES (679, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:02');
INSERT INTO `operation_logs` VALUES (680, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:03');
INSERT INTO `operation_logs` VALUES (681, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:05');
INSERT INTO `operation_logs` VALUES (682, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:06');
INSERT INTO `operation_logs` VALUES (683, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": 1, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:10');
INSERT INTO `operation_logs` VALUES (684, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:13');
INSERT INTO `operation_logs` VALUES (685, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:16');
INSERT INTO `operation_logs` VALUES (686, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:16');
INSERT INTO `operation_logs` VALUES (687, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:14:17');
INSERT INTO `operation_logs` VALUES (688, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:15:47');
INSERT INTO `operation_logs` VALUES (689, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:02');
INSERT INTO `operation_logs` VALUES (690, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:03');
INSERT INTO `operation_logs` VALUES (691, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:03');
INSERT INTO `operation_logs` VALUES (692, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:04');
INSERT INTO `operation_logs` VALUES (693, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:04');
INSERT INTO `operation_logs` VALUES (694, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:04');
INSERT INTO `operation_logs` VALUES (695, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:05');
INSERT INTO `operation_logs` VALUES (696, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:05');
INSERT INTO `operation_logs` VALUES (697, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:09');
INSERT INTO `operation_logs` VALUES (698, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:09');
INSERT INTO `operation_logs` VALUES (699, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:10');
INSERT INTO `operation_logs` VALUES (700, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:21');
INSERT INTO `operation_logs` VALUES (701, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:22');
INSERT INTO `operation_logs` VALUES (702, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:22');
INSERT INTO `operation_logs` VALUES (703, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:22');
INSERT INTO `operation_logs` VALUES (704, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:48');
INSERT INTO `operation_logs` VALUES (705, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:49');
INSERT INTO `operation_logs` VALUES (706, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:49');
INSERT INTO `operation_logs` VALUES (707, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:49');
INSERT INTO `operation_logs` VALUES (708, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:49');
INSERT INTO `operation_logs` VALUES (709, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:50');
INSERT INTO `operation_logs` VALUES (710, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:50');
INSERT INTO `operation_logs` VALUES (711, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 10, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:53');
INSERT INTO `operation_logs` VALUES (712, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:55');
INSERT INTO `operation_logs` VALUES (713, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:58');
INSERT INTO `operation_logs` VALUES (714, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:59');
INSERT INTO `operation_logs` VALUES (715, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:59');
INSERT INTO `operation_logs` VALUES (716, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:16:59');
INSERT INTO `operation_logs` VALUES (717, 1, 'view_stats', 'access_record', NULL, '{\"stats_type\": \"summary\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:05');
INSERT INTO `operation_logs` VALUES (718, 1, 'view', 'device', NULL, '{\"page\": 1, \"page_size\": 10, \"device_type\": null, \"status\": \"\"}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:10');
INSERT INTO `operation_logs` VALUES (719, 1, 'view', 'log', NULL, '{\"user_id\": null, \"username\": \"\", \"action\": \"\", \"resource_type\": \"\", \"start_time\": null, \"end_time\": null, \"success\": null, \"ip_address\": null, \"page\": 1, \"page_size\": 10}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:12');
INSERT INTO `operation_logs` VALUES (720, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:16');
INSERT INTO `operation_logs` VALUES (721, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:17');
INSERT INTO `operation_logs` VALUES (722, 1, 'view', 'access_record', NULL, '{\"page\": 1, \"page_size\": 20, \"device_id\": null, \"user_id\": null, \"access_result\": null, \"start_time\": null, \"end_time\": null}', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0', 1, NULL, '2025-11-11 18:18:22');

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '权限名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '权限描述',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  INDEX `idx_name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of permissions
-- ----------------------------
INSERT INTO `permissions` VALUES (1, 'user:read', '查看用户信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (2, 'user:create', '创建用户', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (3, 'user:update', '更新用户信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (4, 'user:delete', '删除用户', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (5, 'device:read', '查看设备信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (6, 'device:create', '创建设备', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (7, 'device:update', '更新设备信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (8, 'device:delete', '删除设备', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (9, 'role:read', '查看角色信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (10, 'role:create', '创建角色', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (11, 'role:update', '更新角色信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (12, 'role:delete', '删除角色', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (13, 'permission:read', '查看权限信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (14, 'permission:create', '创建权限', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (15, 'permission:update', '更新权限信息', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (16, 'permission:delete', '删除权限', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (17, 'access_record:read', '查看门禁记录', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (18, 'access_record:create', '创建门禁记录', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (19, 'log:read', '查看操作日志', '2025-10-28 20:43:00');
INSERT INTO `permissions` VALUES (20, 'log:create', '创建操作日志', '2025-10-28 20:43:00');

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS `role_permissions`;
CREATE TABLE `role_permissions`  (
  `role_id` int NOT NULL COMMENT '角色ID',
  `permission_id` int NOT NULL COMMENT '权限ID',
  PRIMARY KEY (`role_id`, `permission_id`) USING BTREE,
  INDEX `idx_role_id`(`role_id` ASC) USING BTREE,
  INDEX `idx_permission_id`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '角色权限关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of role_permissions
-- ----------------------------
INSERT INTO `role_permissions` VALUES (1, 1);
INSERT INTO `role_permissions` VALUES (1, 2);
INSERT INTO `role_permissions` VALUES (1, 3);
INSERT INTO `role_permissions` VALUES (1, 4);
INSERT INTO `role_permissions` VALUES (1, 5);
INSERT INTO `role_permissions` VALUES (1, 6);
INSERT INTO `role_permissions` VALUES (1, 7);
INSERT INTO `role_permissions` VALUES (1, 8);
INSERT INTO `role_permissions` VALUES (1, 9);
INSERT INTO `role_permissions` VALUES (1, 10);
INSERT INTO `role_permissions` VALUES (1, 11);
INSERT INTO `role_permissions` VALUES (1, 12);
INSERT INTO `role_permissions` VALUES (1, 13);
INSERT INTO `role_permissions` VALUES (1, 14);
INSERT INTO `role_permissions` VALUES (1, 15);
INSERT INTO `role_permissions` VALUES (1, 16);
INSERT INTO `role_permissions` VALUES (1, 17);
INSERT INTO `role_permissions` VALUES (1, 18);
INSERT INTO `role_permissions` VALUES (1, 19);
INSERT INTO `role_permissions` VALUES (1, 20);
INSERT INTO `role_permissions` VALUES (2, 1);
INSERT INTO `role_permissions` VALUES (2, 2);
INSERT INTO `role_permissions` VALUES (2, 3);
INSERT INTO `role_permissions` VALUES (2, 5);
INSERT INTO `role_permissions` VALUES (2, 6);
INSERT INTO `role_permissions` VALUES (2, 7);
INSERT INTO `role_permissions` VALUES (2, 8);
INSERT INTO `role_permissions` VALUES (2, 17);
INSERT INTO `role_permissions` VALUES (2, 18);
INSERT INTO `role_permissions` VALUES (2, 19);
INSERT INTO `role_permissions` VALUES (2, 20);
INSERT INTO `role_permissions` VALUES (3, 1);
INSERT INTO `role_permissions` VALUES (3, 3);
INSERT INTO `role_permissions` VALUES (3, 17);
INSERT INTO `role_permissions` VALUES (4, 1);
INSERT INTO `role_permissions` VALUES (4, 2);
INSERT INTO `role_permissions` VALUES (4, 3);
INSERT INTO `role_permissions` VALUES (4, 4);
INSERT INTO `role_permissions` VALUES (4, 5);
INSERT INTO `role_permissions` VALUES (4, 6);
INSERT INTO `role_permissions` VALUES (4, 7);
INSERT INTO `role_permissions` VALUES (4, 8);
INSERT INTO `role_permissions` VALUES (4, 9);
INSERT INTO `role_permissions` VALUES (4, 10);
INSERT INTO `role_permissions` VALUES (4, 11);
INSERT INTO `role_permissions` VALUES (4, 12);
INSERT INTO `role_permissions` VALUES (4, 13);
INSERT INTO `role_permissions` VALUES (4, 14);
INSERT INTO `role_permissions` VALUES (4, 15);
INSERT INTO `role_permissions` VALUES (4, 16);
INSERT INTO `role_permissions` VALUES (4, 17);
INSERT INTO `role_permissions` VALUES (4, 18);
INSERT INTO `role_permissions` VALUES (4, 19);
INSERT INTO `role_permissions` VALUES (4, 20);
INSERT INTO `role_permissions` VALUES (5, 1);
INSERT INTO `role_permissions` VALUES (5, 2);
INSERT INTO `role_permissions` VALUES (5, 3);
INSERT INTO `role_permissions` VALUES (5, 5);
INSERT INTO `role_permissions` VALUES (5, 6);
INSERT INTO `role_permissions` VALUES (5, 7);
INSERT INTO `role_permissions` VALUES (5, 8);
INSERT INTO `role_permissions` VALUES (5, 17);
INSERT INTO `role_permissions` VALUES (5, 18);
INSERT INTO `role_permissions` VALUES (5, 19);
INSERT INTO `role_permissions` VALUES (5, 20);
INSERT INTO `role_permissions` VALUES (6, 1);
INSERT INTO `role_permissions` VALUES (6, 3);
INSERT INTO `role_permissions` VALUES (6, 17);

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '角色名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '角色描述',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE,
  INDEX `idx_name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles` VALUES (1, '管理员', '系统管理员，拥有所有权限', '2025-10-28 20:43:00');
INSERT INTO `roles` VALUES (2, '物业', '物业管理人员，负责设备管理和用户管理', '2025-10-28 20:43:00');
INSERT INTO `roles` VALUES (3, '住户', '小区住户，拥有基本访问权限', '2025-10-28 20:43:00');
INSERT INTO `roles` VALUES (4, 'admin', '系统管理员', '2025-10-28 20:43:00');
INSERT INTO `roles` VALUES (5, 'property', '物业人员', '2025-10-28 20:43:00');
INSERT INTO `roles` VALUES (6, 'resident', '住户', '2025-10-28 20:43:00');

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS `user_roles`;
CREATE TABLE `user_roles`  (
  `user_id` int NOT NULL COMMENT '用户ID',
  `role_id` int NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`, `role_id`) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_role_id`(`role_id` ASC) USING BTREE,
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户角色关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_roles
-- ----------------------------
INSERT INTO `user_roles` VALUES (1, 1);
INSERT INTO `user_roles` VALUES (1, 4);
INSERT INTO `user_roles` VALUES (2, 3);
INSERT INTO `user_roles` VALUES (2, 6);
INSERT INTO `user_roles` VALUES (3, 2);
INSERT INTO `user_roles` VALUES (3, 5);
INSERT INTO `user_roles` VALUES (4, 3);
INSERT INTO `user_roles` VALUES (4, 6);
INSERT INTO `user_roles` VALUES (13, 3);
INSERT INTO `user_roles` VALUES (14, 3);
INSERT INTO `user_roles` VALUES (15, 3);
INSERT INTO `user_roles` VALUES (16, 3);
INSERT INTO `user_roles` VALUES (17, 3);
INSERT INTO `user_roles` VALUES (18, 3);
INSERT INTO `user_roles` VALUES (19, 3);
INSERT INTO `user_roles` VALUES (20, 3);
INSERT INTO `user_roles` VALUES (21, 3);
INSERT INTO `user_roles` VALUES (22, 3);
INSERT INTO `user_roles` VALUES (24, 3);
INSERT INTO `user_roles` VALUES (25, 3);
INSERT INTO `user_roles` VALUES (26, 3);
INSERT INTO `user_roles` VALUES (27, 3);
INSERT INTO `user_roles` VALUES (28, 3);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '邮箱',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码哈希值',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '手机号',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `is_active` tinyint(1) NULL DEFAULT 1 COMMENT '是否激活',
  `is_deleted` tinyint(1) NULL DEFAULT 0 COMMENT '是否删除',
  `created_at` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  INDEX `idx_username`(`username` ASC) USING BTREE,
  INDEX `idx_email`(`email` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 28 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'admin@example.com', '$2b$12$6ZamR3t/W4VpeEVkyeFNwO.xRwqYYcHwcCI2XjdUviZxHZIYToR3m', '13800000002', '管理员', 1, 0, '2025-10-28 20:43:00', '2025-11-11 16:12:13');
INSERT INTO `users` VALUES (2, 'user', 'user@example2.com', '$2b$12$Padh.ZFQ3fN..dYBVZd9TuwWJswrtxu7QAL3w/kE0ZfaIc/lDeJaO', '17654356562', 'user', 1, 0, '2025-10-28 20:43:00', '2025-11-11 16:09:05');
INSERT INTO `users` VALUES (3, 'property', 'property@example.com', '$2a$10$yYQHWMOfFH/LtDcTDPYuDedJX9Tji4UONjA8MQTbjlBzExgKjkvtC', NULL, '物业管理员', 1, 0, '2025-10-28 20:43:00', '2025-11-11 15:21:11');
INSERT INTO `users` VALUES (4, 'resident', 'resident@example.com', '$2b$12$n.1yFjcOHF0G3Ky9uTO9iuK5tXb6rPaeqho86catApy.p6T.hbKii', NULL, '小区住户', 1, 0, '2025-10-28 20:43:00', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (13, 'l2r451ee', 'l2r451ee@example.com', '$2b$12$Ao/eCrYHpZOI4I1Ibec6nup4KqII/V7JzJD2NXHIVq4sWenR2J3DO', '13800138000', '测试用户_l2r451ee', 1, 1, '2025-10-29 13:25:57', '2025-11-11 15:04:47');
INSERT INTO `users` VALUES (14, '3bb0nrf6', '3bb0nrf6@example.com', '$2b$12$q.JbsPQZrvXPijNUFs.OiOiOkGnRW0Wl/CH3pfZ5iw6uZBh3nDxji', '13900139000', '更新后的测试用户', 1, 1, '2025-10-29 13:26:57', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (15, 'test_user_1761716008650', 'test_user_1761716008650@example.com', '$2b$12$134TlLGIo0JiBtunFKa3zeXK5t74oBKE2SQvEk2oCQzyopKXIsjGy', '13900139000', '更新后的测试用户', 1, 1, '2025-10-29 13:33:28', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (16, 'test_user_1761716077442', 'test_user_1761716077442@example.com', '$2b$12$/uyhWUu2LQlLzjqezlxFf.dGAQJ8bonzYTM1/JpxYfVoGG8dSFIWi', '13900139000', '更新后的测试用户', 1, 1, '2025-10-29 13:34:37', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (17, 'test_user_1761716083616', 'test_user_1761716083616@example.com', '$2b$12$DFozRyYe1HPf5qQR9aTDxurpulDxaBKJIbCM3Qd.SP4jvf9Xq9vRG', '13900139000', '更新后的测试用户', 1, 1, '2025-10-29 13:34:43', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (18, 'testuser_1761720105794', 'test_1761720105794@example.com', '$2b$12$YnUR.94K3gMYQmQb6oEw.esMpK51M4yrzCvT0WEyDEgaABiMtKTAO', '13800138000', '测试用户', 1, 1, '2025-10-29 14:41:45', '2025-11-11 15:05:00');
INSERT INTO `users` VALUES (19, 'testuser_1761720111146', 'test_1761720111146@example.com', '$2b$12$nWp1vZ91pOKKwx1W0BCGv.PC7QVjdo.0WErgNRHkXwjOZdWiHerTm', '13800138000', '测试用户', 1, 1, '2025-10-29 14:41:51', '2025-11-11 15:04:58');
INSERT INTO `users` VALUES (20, 'testuser_1761720124850', 'test_1761720124850@example.com', '$2b$12$G0gcup6kWw89495FsCcXxutU7UtE5y94wJYpV2tsdyR3GEHgKGKc6', '13800138000', '测试用户', 1, 1, '2025-10-29 14:42:04', '2025-11-11 15:04:55');
INSERT INTO `users` VALUES (21, 'testuser_1761720130724', 'test_1761720130724@example.com', '$2b$12$QjO8PNEO9YxXQe70HonwPOueibTX3HG3H8OiclnW7VFgV6lOHXEJa', '13800138000', '测试用户', 1, 1, '2025-10-29 14:42:10', '2025-11-11 15:04:52');
INSERT INTO `users` VALUES (22, 'testuser_1761722197140', 'test_1761722197140@example.com', '$2b$12$fe6HgVGCaRtQfjkCaASrIu2zfm01Blhlt4.WY8c5xYz6D3guoFNiq', '13800138000', '测试用户', 1, 1, '2025-10-29 15:16:37', '2025-11-11 15:05:05');
INSERT INTO `users` VALUES (23, 'aaa', '3418088259@qq.com', '$2b$12$yGMQa2BmHLLT0K69K7ynIuBVXvcwIJ4Z.7CA5HQkl68A49CgcVB7C', '19193133833', 'aaa', 1, 0, '2025-10-29 15:30:54', '2025-11-11 14:12:54');
INSERT INTO `users` VALUES (24, 'testuser', 'test@example.com', '$2b$12$6FA0AeTXSZ/HcKWqXbbDs.R5IsQ68T5AY4XfdbL11ot.HD/ykG7oa', '13800138000', '????', 1, 0, '2025-11-11 14:21:18', NULL);
INSERT INTO `users` VALUES (25, 'testuser2', 'test2@example.com', '$2b$12$tNC9W1SQOR4vnwMVEcgeDufj0MCfg/oJTWzzifDGF/YcP/mzE1BlS', '13800138001', '????2', 1, 0, '2025-11-11 14:23:42', NULL);
INSERT INTO `users` VALUES (26, 'user222', '3418088219@qq.com', '$2b$12$ij.jjbwGOCDwdyf1EDyX.u9fgBrZWYedQKGnr28ia2g3IX19IE5I6', '19193133456', '我', 1, 0, '2025-11-11 14:26:39', NULL);
INSERT INTO `users` VALUES (27, 'uuy', 'mz@qq.com', '$2b$12$4X1diOCC1bh4dZXjiqqxEemlIiKRervdTIONcvt8hau1UpeWq0RZ2', '', 'uuy', 1, 0, '2025-11-11 15:22:45', '2025-11-11 17:43:23');
INSERT INTO `users` VALUES (28, 'wjc', 'wjc@qq.com', '$2b$12$DMln45jTrxdV3F8UpXXVGODq50FH7RS4WMxP2RxLoVJRdyZ24eYMO', '15467863456', '王', 1, 0, '2025-11-11 15:31:48', '2025-11-11 17:43:09');

SET FOREIGN_KEY_CHECKS = 1;
