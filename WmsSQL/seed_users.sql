-- WMS 测试用户种子数据
-- 在 Navicat 中选中 wmsdatabase 后执行本脚本
-- 所有账号密码均为：admin123（已 werkzeug 哈希，可直接登录后端）

USE wmsdatabase;

-- 密码哈希对应明文 admin123
SET @pwd = 'pbkdf2:sha256:1000000$2l9nBpljWtiYEfYp$f584106e0fd1a61f02118f4dfe11fd3d1832c34bc094bb1ba9f3e01430228e23';

INSERT INTO users (username, name, password, role, is_active) VALUES
('admin',  '系统管理员', @pwd, 'admin',            1),
('keeper', '仓管员',     @pwd, 'warehouse_keeper', 1),
('viewer', '查看员',     @pwd, 'viewer',           1)
ON DUPLICATE KEY UPDATE
  name      = VALUES(name),
  password  = IF(VALUES(password) LIKE 'pbkdf2:%' OR VALUES(password) LIKE 'scrypt:%', VALUES(password), password),
  role      = VALUES(role),
  is_active = VALUES(is_active);

-- 执行后可用以下账号登录系统：
-- | 用户名  | 密码     | 角色           | 权限说明           |
-- | admin   | admin123 | admin          | 全部权限           |
-- | keeper  | admin123 | warehouse_keeper | 建单、审核、维护主数据 |
-- | viewer  | admin123 | viewer         | 只读查询           |
