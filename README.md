# 仓库管理系统 (WMS)

前后端分离的仓库管理系统：Vue 3 + Element Plus + Flask + MySQL。

库存变更**仅**通过后端 `inventory_service`，每次变动写入流水；入/出库/盘点走「草稿 → 提交 → 审核过账 → 完成」。

## 目录结构

| 目录 / 文档 | 说明 |
|-------------|------|
| `WmsClient/` | Vue 3 前端（Vite + Element Plus + Pinia） |
| `WmsServer/` | Flask REST API（Waitress，`/api/v1`） |
| `WmsSQL/` | MySQL 建库脚本与表结构说明 |
| `仓库管理系统架构提示词.md` | 架构约束与协作约定（与当前实现对齐） |
| `WmsSQL/表结构说明.md` | 13 张表字段与关系说明 |

## 已实现功能

- 登录鉴权（JWT）、改密、用户管理（admin）
- 商品 / 仓库 / 库位主数据
- 库存查询、流水、安全库存预警
- 入库单 / 出库单 / 盘点单（建单、提交、审核、驳回、取消）
- 首页看板（出入库趋势）
- 可选：审核通过后 GPIO 脉冲（Orange Pi，默认关闭）

## 本地开发

### 1. 数据库

启动本地 MySQL，创建库并执行初始化脚本：

```bash
mysql -u root -p < WmsSQL/init.sql
```

连接参数见 `WmsServer/.env.example`（默认库名 `wmsdatabase`，密码 `wmspassword`）。

仅需用户种子时可另执行 `WmsSQL/seed_users.sql`；完整示例数据推荐用下方 `init_db.py`。

### 2. 后端

```bash
cd WmsServer
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python serve.py
```

- 健康检查：http://localhost:5000/api/v1/health
- `init_db.py`：建表 + 种子（用户、仓库 WH01、库位、商品 SKU-P001/P002）

### 3. 前端

```bash
cd WmsClient
npm install
npm run dev
```

访问 http://localhost:5173（Vite 代理 `/api` → `localhost:5000`）

### 默认账号

| 用户名 | 角色 | 密码 |
|--------|------|------|
| `admin` | 管理员 | `admin123` |
| `keeper` | 仓管 (`warehouse_keeper`) | `admin123` |
| `viewer` | 查看者 | `admin123` |

## 角色权限（摘要）

| 能力 | admin | warehouse_keeper | viewer |
|------|-------|------------------|--------|
| 商品 / 仓库 / 库位 / 用户管理 | ✓ | | |
| 入/出库建单、编辑、提交、删除 | ✓ | ✓ | ✓ |
| 盘点建单与流转 | ✓ | ✓ | 只读列表 |
| 单据审核 / 驳回 / 取消 | ✓ | ✓ | |
| 库存查询、流水、看板 | ✓ | ✓ | ✓ |

## 核心业务规则

- 库存变更**仅**通过 `inventory_service`，每次变动写入 `inventory_transaction`
- 单据：`draft` → `submitted` → 审核过账后直接 `completed`（或 `cancelled`）；驳回回到 `draft`
- 出库审核前校验可用库存，不足返回 `409` + `INSUFFICIENT_STOCK`
- 单据号：`IN` / `OUT` / `ST` + `YYYYMMDD` + 4 位序号
