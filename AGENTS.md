# AGENTS.md (Automation Cheatsheet)

## Quick Start

### System Management (Unified CLI)
```bash
# 初始化系统（首次运行）
python manage.py init

# 启动服务
python manage.py start backend       # 启动后端
python manage.py start frontend      # 启动前端  
python manage.py start all           # 同时启动前后端

# 检查状态
python manage.py check               # 检查数据库（Agent、用户、Prompt）
python manage.py check --verbose     # 详细信息
python manage.py status              # 查看系统运行状态
```

### Professional Vocabulary Management (专业词汇管理)
```bash
# 添加钢铁行业默认词汇（首次运行后执行）
python scripts/vocabulary_manager.py add-default

# 从 CSV 文件批量导入词汇
python scripts/vocabulary_manager.py import vocabulary.csv

# 查看词汇统计
python scripts/vocabulary_manager.py stats

# 搜索词汇
python scripts/vocabulary_manager.py search "Q235"

# 导出词汇到 CSV
python scripts/vocabulary_manager.py export output.csv

# 测试查询增强
python scripts/vocabulary_manager.py test-enhance "Q235钢板的抗拉强度是多少？"
```

### RAG System Management (scripts/rag_cli.py)
```bash
# 构建 RAG 索引
python scripts/rag_cli.py build --rebuild

# 搜索文档
python scripts/rag_cli.py search "钢铁生产流程" --top-k 5
python scripts/rag_cli.py search --interactive

# 查看系统信息
python scripts/rag_cli.py info
python scripts/rag_cli.py check      # 检查数据库状态

# 索引迁移（如需手动升级旧索引）
python scripts/migrate_to_fast_index.py --auto
```

### Database Management (scripts/db_migrate.py)
```bash
# 数据库迁移
python scripts/db_migrate.py reset          # 重置数据库
python scripts/db_migrate.py add-presets   # 添加预设问题表
python scripts/db_migrate.py add-prompts   # 添加 Prompt 管理表
python scripts/db_migrate.py add-market    # 添加市场数据表
python scripts/db_migrate.py status        # 查看数据库状态
python scripts/db_migrate.py list          # 列出所有可用迁移
```

### Test Users Management (测试用户管理)
```bash
# 初始化测试用户账号（三种角色）
python scripts/init_test_users.py

# 测试账号列表：
# 1. 管理员 (admin)
#    用户名: admin
#    密码: admin123
#    权限: 全部功能 + 系统管理
#
# 2. 技术经理 (manager)
#    用户名: manager
#    密码: manager123
#    权限: 智能问答、知识库、设备管理、市场分析、工艺流程
#
# 3. 技术员 (technician)
#    用户名: technician
#    密码: tech123
#    权限: 智能问答、知识库查询、设备诊断

# 登录测试：
# 前端: http://localhost:3000/login
# 后端: http://localhost:8000/docs
```

**角色权限对比**：

| 功能模块 | ADMIN | MANAGER | TECHNICIAN |
|---------|-------|---------|------------|
| AI 对话 | ✅ | ✅ | ✅ |
| 知识库查询 | ✅ | ✅ | ✅ |
| 文档上传 | ✅ | ✅ | ❌ |
| 文档删除 | ✅ | ✅ | ❌ |
| 设备管理 | ✅ | ✅ | ✅ (仅查看) |
| 市场分析 | ✅ | ✅ | ❌ |
| 工艺流程 | ✅ | ✅ | ✅ (仅查看) |
| 环保监控 | ✅ | ✅ | ❌ |
| 系统管理 | ✅ | ❌ | ❌ |

**可用 Agent 列表**：

| Agent 类型 | ADMIN | MANAGER | TECHNICIAN |
|-----------|-------|---------|------------|
| 通用助手 (general) | ✅ | ✅ | ✅ |
| 工艺专家 (process) | ✅ | ✅ | ✅ |
| 设备诊断 (equipment) | ✅ | ✅ | ✅ |
| 市场分析师 (market) | ✅ | ✅ | ❌ |
| 质量顾问 (quality) | ✅ | ✅ | ❌ |
| 节能专家 (environment) | ✅ | ✅ | ❌ |

**UI 差异说明**：
- **ADMIN**: 侧边栏显示"系统管理"菜单项，可访问所有功能模块
- **MANAGER**: 侧边栏显示设备管理、市场分析、工艺流程、环保监控，默认 Agent 为"通用助手"
- **TECHNICIAN**: 侧边栏仅显示 AI 对话、知识库、设备管理、工艺流程，默认 Agent 为"设备诊断"

### Role-based UI Testing Guide (角色差异化 UI 测试指南)

**快速测试步骤**：

1. **启动系统**：
   ```bash
   python manage.py start all
   ```

2. **初始化测试用户**（如未创建）：
   ```bash
   python scripts/init_test_users.py
   ```

3. **测试三种角色**：

   **① 管理员角色 (ADMIN)**
   ```
   URL: http://localhost:3000/login
   用户名: admin
   密码: admin123
   
   预期 UI：
   ✅ 侧边栏显示全部 6 个 Agent（通用、工艺、设备、市场、质量、环保）
   ✅ 导航菜单：AI 对话、知识库、设备管理、市场分析、工艺流程、环保监控
   ✅ 系统管理菜单项（独有）
   ✅ 知识库页面：上传、删除、批量删除按钮全部可用
   ✅ 用户信息显示："管理员"角色标签
   ```

   **② 技术经理角色 (MANAGER)**
   ```
   URL: http://localhost:3000/login
   用户名: manager
   密码: manager123
   
   预期 UI：
   ✅ 侧边栏显示全部 6 个 Agent
   ✅ 导航菜单：AI 对话、知识库、设备管理、市场分析、工艺流程、环保监控
   ❌ 无"系统管理"菜单项
   ✅ 知识库页面：上传、删除、批量删除按钮全部可用
   ✅ 设备管理页面：显示"经理功能"提示卡片（紫色边框）
   ✅ 市场分析页面：显示"经理功能"提示卡片（紫色边框）
   ✅ 用户信息显示："技术经理"角色标签
   ✅ 默认 Agent：通用助手
   ```

   **③ 技术员角色 (TECHNICIAN)**
   ```
   URL: http://localhost:3000/login
   用户名: technician
   密码: tech123
   
   预期 UI：
   ✅ 侧边栏仅显示 3 个 Agent（设备诊断、工艺专家、通用助手）
   ✅ 导航菜单：AI 对话、知识库、设备管理、工艺流程
   ❌ 无"市场分析"、"环保监控"、"系统管理"菜单项
   ❌ 知识库页面：无上传、删除按钮（仅查询）
   ✅ 设备管理页面：显示"技术员功能"提示卡片（蓝色边框）
   ❌ 访问 /dashboard/market 应被拦截或提示无权限
   ✅ 用户信息显示："技术员"角色标签
   ✅ 默认 Agent：设备诊断（自动选中）
   ```

**权限验证测试**：

```bash
# 测试技术员访问市场分析页面（应失败）
# 1. 以 technician 身份登录
# 2. 手动访问 http://localhost:3000/dashboard/market
# 预期：侧边栏无此菜单项，直接访问应重定向或显示无权限

# 测试文档上传权限
# 1. 以 technician 身份登录
# 2. 访问知识库页面
# 预期：无"上传文档"按钮，无批量删除按钮

# 测试 Agent 切换权限
# 1. 以 technician 身份登录
# 2. 查看 Agent 列表
# 预期：仅显示 equipment, process, general 三个 Agent
```

**对比测试场景**：

| 操作 | ADMIN | MANAGER | TECHNICIAN |
|-----|-------|---------|------------|
| 切换到"市场分析师"Agent | ✅ | ✅ | ❌ 不可见 |
| 上传文档到知识库 | ✅ | ✅ | ❌ 无按钮 |
| 访问 /dashboard/admin | ✅ | ❌ 无菜单项 | ❌ 无菜单项 |
| 访问 /dashboard/market | ✅ | ✅ | ❌ 无菜单项 |
| 批量删除文档 | ✅ | ✅ | ❌ 无按钮 |
| 查看设备管理页面 | ✅ 红色卡片 | ✅ 紫色卡片 | ✅ 蓝色卡片 |

**调试技巧**：

```bash
# 查看用户角色和权限
python manage.py check --verbose

# 查看用户最后登录时间
python -c "from src.api.db import get_db; from src.api.models import User; \
           db = next(get_db()); \
           users = db.query(User).filter(User.username.in_(['admin', 'manager', 'technician'])).all(); \
           [print(f'{u.username}: role={u.role}, last_login={u.last_login}') for u in users]"

# 重置测试用户密码
python scripts/init_test_users.py
```

**前端开发者检查清单**：

- [x] 角色标签正确显示在侧边栏用户菜单
- [x] Agent 列表根据角色过滤（technician 仅 3 个）
- [x] 导航菜单根据角色显示/隐藏
- [x] **知识库权限控制**（已实现 ✅）
  - 技术员可以查看知识库、预览、下载文档
  - 技术员看不到上传、删除、编辑、重新索引按钮
  - 管理员和经理有全部权限
- [x] 设备/市场页面显示角色特定提示卡片
- [x] 默认 Agent 根据角色自动选中（technician → equipment）
- [x] 页面访问权限控制（middleware 或路由守卫）
- [x] **聊天记录按用户隔离**（已实现）

### 知识库权限管理（2025-10-29 修复）

**问题**：技术员（technician）无法访问知识库页面，返回 403 Forbidden

**原因**：
- 后端 `/api/admin/files` 等接口全部要求管理员权限（`require_admin`）
- 技术员角色虽然有 `canAccessKnowledge: true`，但无法查看文档列表

**解决方案**（已实现 ✅）：

#### 1. 后端权限分级（`src/api/admin.py`）

**新增权限装饰器**：
```python
def require_manager_or_admin(user: User = Depends(_get_current_user)) -> User:
    """要求管理员或经理权限"""
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="需要管理员或经理权限")
    return user
```

**API 权限调整**：

| 接口 | 原权限 | 新权限 | 说明 |
|-----|-------|-------|-----|
| `GET /api/admin/files` | `require_admin` | `_get_current_user` | 所有登录用户可查看 |
| `GET /api/admin/files/{file_name}/preview` | `require_admin` | `_get_current_user` | 所有登录用户可预览 |
| `GET /api/admin/files/{file_name}/download` | `require_admin` | `_get_current_user` | 所有登录用户可下载 |
| `DELETE /api/admin/files/{file_name}` | `require_admin` | `require_manager_or_admin` | 仅管理员/经理可删除 |
| `POST /api/admin/files/batch-delete` | `require_admin` | `require_manager_or_admin` | 仅管理员/经理可批量删除 |

#### 2. 前端 UI 权限控制（`frontend/app/dashboard/knowledge/page.tsx`）

**权限检查**：
```typescript
import { useAuthStore } from "@/store/authStore";
import { hasPermission } from "@/lib/permissions";

const { user } = useAuthStore();
const canUpload = hasPermission(user, "canUpload");   // 技术员: false
const canDelete = hasPermission(user, "canDelete");   // 技术员: false
```

**UI 元素条件渲染**：
- ✅ 上传按钮：`{canUpload && <Button>上传文档</Button>}`
- ✅ 批量删除按钮：`{canDelete && selectedDocs.size > 0 && <Button>删除选中</Button>}`
- ✅ 勾选框列：`{canDelete && <TableHead><Checkbox /></TableHead>}`
- ✅ 删除菜单项：`{canDelete && <DropdownMenuItem>删除</DropdownMenuItem>}`
- ✅ 编辑/重新索引：`{canUpload && <DropdownMenuItem>编辑</DropdownMenuItem>}`

#### 3. 权限配置（`frontend/lib/permissions.ts`）

**技术员权限**：
```typescript
case "technician":
  return {
    canChat: true,
    canUpload: false,          // ❌ 不能上传
    canDownload: true,          // ✅ 可以下载
    canDelete: false,           // ❌ 不能删除
    canAccessKnowledge: true,   // ✅ 可以查看知识库
    canAccessEquipment: true,
    canAccessWorkflow: true,
    // ...
  };
```

#### 4. 验证步骤

```bash
# 1. 以技术员身份登录
# URL: http://localhost:3000/login
# 用户名: technician
# 密码: tech123

# 2. 访问知识库页面
# URL: http://localhost:3000/dashboard/knowledge

# 预期结果：
# ✅ 能看到文档列表
# ✅ 能预览文档（点击"预览"按钮）
# ✅ 能下载文档（点击"下载"按钮）
# ❌ 看不到"上传文档"按钮
# ❌ 看不到"批量删除"按钮
# ❌ 看不到勾选框列
# ❌ 下拉菜单中没有"删除"、"编辑"、"重新索引"选项
# ✅ 下拉菜单中只有"预览"和"下载"选项
```

#### 5. 技术细节

**类型定义修复**：
- 统一 `User` 类型定义（`frontend/lib/types/user.ts` 和 `api.ts`）
- 将 `role: string` 改为 `role: UserRoleType`（联合类型）
- 修复 TypeScript 类型不兼容错误

**日志改进**：
```python
# 后端日志记录用户角色
logger.info(f"File {file_name} downloaded by {current_user.username} ({current_user.role})")
```

### 用户聊天记录隔离

**问题**：退出登录后以其他用户身份登录时，前一个用户的聊天记录仍可见

**解决方案**（已实现 ✅）：

1. **按用户隔离存储**：
   - 聊天记录使用动态存储 key: `chat-store-user-{userId}`
   - 每个用户的聊天记录独立存储在 localStorage
   - 登录时自动加载当前用户的聊天记录

2. **登录时清除旧数据**：
   ```typescript
   // authStore.ts - login 方法
   login: (user, token) => {
       localStorage.setItem("user-id", user.id.toString());
       chatStore.clearUserData();  // 清除旧用户数据
       chatStore.setCurrentUser(user.id);  // 设置新用户 ID
   }
   ```

3. **退出登录时清理**：
   ```typescript
   // authStore.ts - logout 方法
   logout: () => {
       localStorage.removeItem("user-id");
       chatStore.clearUserData();
       chatStore.setCurrentUser(null);
   }
   ```

4. **动态存储机制**：
   ```typescript
   // chatStore.ts - 自定义 storage
   storage: createJSONStorage(() => ({
       getItem: (name) => {
           const userId = localStorage.getItem("user-id");
           const key = userId ? `${name}-user-${userId}` : name;
           return localStorage.getItem(key);
       },
       setItem: (name, value) => {
           const userId = localStorage.getItem("user-id");
           const key = userId ? `${name}-user-${userId}` : name;
           localStorage.setItem(key, value);
       },
   }))
   ```

**验证步骤**：

```bash
# 1. 以 admin 身份登录
# http://localhost:3000/login
# 用户名: admin, 密码: admin123

# 2. 创建一些聊天记录（发送几条消息）

# 3. 退出登录

# 4. 以 manager 身份登录
# 用户名: manager, 密码: manager123

# 5. 验证：
# ✅ 看不到 admin 的聊天记录
# ✅ 显示新的"新对话"会话
# ✅ 侧边栏显示 manager 角色

# 6. 再次退出并以 admin 身份登录

# 7. 验证：
# ✅ 之前的聊天记录恢复显示
# ✅ 消息内容完整保留
```

**技术细节**：

- 使用 Zustand persist 中间件的自定义 storage
- 基于 `localStorage.getItem("user-id")` 动态生成存储 key
- 登录/退出时同步清理和加载数据
- 确保不同用户的数据完全隔离

**注意事项**：

- ⚠️ 当前实现仅在前端隔离，刷新页面会保留数据
- 💡 长期方案：将聊天记录存储到后端数据库（chat_session、chat_message 表）
- 💡 未来可添加：跨设备同步、云端备份、聊天记录导出等功能
```

### Knowledge Graph Management
```bash
# 知识图谱构建（从上传的文档自动提取实体和关系）
python scripts/init_steel_knowledge_graph.py

# 知识图谱查询（通过 Agent 工具）
# Agent 会自动使用 KnowledgeGraphQueryTool 查询知识图谱
# 支持的查询类型：
# - statistics: 获取知识图谱统计信息（实体数量、关系数量等）
# - search: 搜索实体（模糊匹配）
# - properties: 查询实体属性
# - relationships: 查询实体关系
# - similar: 查询相似实体
# - steel_composition: 查询钢种成分

# 知识图谱 API 端点
# GET /api/knowledge-graph/statistics         - 获取统计信息
# POST /api/knowledge-graph/search/entities   - 搜索实体
# GET /api/knowledge-graph/entities/{id}      - 获取实体详情
# POST /api/knowledge-graph/entities/{id}/related - 获取相关实体
```

**知识图谱数据位置**：
- 数据文件：`data/knowledge_graph.json`（~6MB，6669+ 实体）
- 自动加载：Agent 启动时自动加载知识图谱
- 更新方式：重新运行 `init_steel_knowledge_graph.py` 重建知识图谱
- 📚 **详细文档**: 查看 `docs/KNOWLEDGE_GRAPH_GUIDE.md` 了解完整使用说明

**知识图谱 Web 界面（已实现 ✅）**：
- **访问路径**: `http://localhost:3000/dashboard/knowledge-graph`
- **入口位置**: 知识库页面右上角"知识图谱"按钮
- **权限控制**:
  - 所有角色可以查看知识图谱和搜索实体
  - 管理员和经理可以重新构建知识图谱
  - 技术员仅查看权限
- **功能特性**:
  - 📊 统计仪表板：实体数量、关系数量、类型分布
  - 🔍 实体搜索：支持按名称和类型过滤
  - 📋 列表视图：查看实体详情、置信度
  - 🎨 图谱视图：可视化展示（开发中）
  - 🔄 一键重建：管理员可从文档重新构建图谱

**为什么 Agent 返回文字描述？**
- Agent 的职责是回答问题（后端），不是渲染 UI（前端）
- 知识图谱可视化需要前端页面（D3.js/Cytoscape.js）
- Agent 通过 `KnowledgeGraphQueryTool` 查询数据，然后生成文字回答
- ✅ 后端已实现：API 接口 + Agent 工具
- ⏳ 待开发：前端可视化页面（`/dashboard/knowledge-graph`）

---

## Market Analysis System (市场分析系统)

### 功能说明
市场分析系统提供钢铁市场价格数据管理、新闻聚合、趋势分析和预测功能。支持数据上传、API接入（可选）和Agent查询。

### 核心特性
1. **价格数据管理**: 铁矿石、螺纹钢、焦炭、废钢等原料和产品价格
2. **市场新闻聚合**: 行业新闻、政策动态、供需分析
3. **趋势分析**: 7天/30天价格趋势、预测区间、置信度评估
4. **市场概况**: 最新价格汇总、统计信息
5. **数据上传**: Excel/CSV批量导入
6. **Agent查询**: Market Agent可查询价格、新闻、趋势

### 快速开始

#### 1. 数据库初始化
```bash
# 创建市场数据表（首次运行）
python scripts/db_migrate.py add-market

# 输出示例：
# ✅ 市场数据表创建成功！
# 📊 已创建表:
#   - market_price_data (价格数据)
#   - market_news (市场新闻)
#   - market_data_source (数据源配置)
```

#### 2. 数据上传

**方式一：通过前端上传**
1. 以管理员或经理身份登录
2. 访问 `http://localhost:3000/dashboard/market`
3. 点击"上传数据"按钮
4. 选择Excel或CSV文件
5. 系统自动验证并导入数据

**方式二：通过API上传**
```bash
# 使用curl上传CSV文件
curl -X POST http://localhost:8000/api/market/prices/batch-upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@market_data.csv"
```

**CSV文件格式示例**（`market_data.csv`）：
```csv
material_type,category,price,unit,region,source,price_date,change_rate,change_amount,volume
铁矿石,raw_material,890,元/吨,青岛港,Mysteel,2025-10-22,2.3,20,50000
螺纹钢,product,4250,元/吨,上海,钢联,2025-10-22,-1.5,-65,30000
焦炭,raw_material,2180,元/吨,唐山,煤炭资源网,2025-10-22,0.8,17,20000
废钢,raw_material,2650,元/吨,江苏,废钢网,2025-10-22,3.2,82,15000
```

**Excel文件格式**：
- 支持 `.xlsx` 和 `.xls` 格式
- 第一行为列名（同CSV）
- 必填列：`material_type`, `category`, `price`, `price_date`
- 可选列：`unit`, `region`, `source`, `change_rate`, `change_amount`, `volume`, `high_price`, `low_price`

#### 2.1. 自动计算涨跌幅（✨ 新功能）

**功能说明**：
系统会自动计算价格数据的涨跌幅（基于上周同期数据），无需手动提供 `change_rate` 字段。

**工作原理**：
1. **上传数据时**：如果 `change_rate` 为空或为 0，系统自动查询 7 天前的价格数据并计算涨跌幅
2. **计算公式**：
   ```
   change_rate = ((当前价格 - 上周价格) / 上周价格) × 100
   change_amount = 当前价格 - 上周价格
   ```
3. **前端显示**：
   - `change_rate > 0` → 显示 `+X.X%`（红色上涨）
   - `change_rate < 0` → 显示 `-X.X%`（绿色下跌）
   - `change_rate = 0` → 显示 `0.0%`（持平）
   - `change_rate = null` → 显示 `N/A`（无对比数据）

**简化的CSV格式**（无需提供 change_rate）：
```csv
material_type,category,price,unit,source,price_date
铁矿石,raw_material,870,元/吨,Mysteel,2025-10-18
铁矿石,raw_material,890,元/吨,Mysteel,2025-10-25
```
上传后，系统自动计算：`change_rate = (890 - 870) / 870 × 100 = 2.3%`

**重新计算现有数据**：
如果已有数据的 `change_rate = 0` 或 `null`，可以运行脚本重新计算：

```bash
# 查看数据统计
python scripts/recalculate_market_change_rate.py --stats

# 输出示例：
# 📊 市场数据统计
# ============================================================
# 总记录数: 156
# change_rate 为 0 或 null: 45 (28.8%)
# 按材料类型统计:
#   - 螺纹钢: 52 条
#   - 铁矿石: 48 条
#   - 焦炭: 34 条
#   - 废钢: 22 条

# 重新计算 change_rate 为 0 或 null 的数据
python scripts/recalculate_market_change_rate.py

# 输出示例：
# 🔄 重新计算 change_rate 为 0 或 null 的数据...
# 📊 找到 45 条需要重新计算的记录
# ✅ [螺纹钢] 2025-10-25 | 价格: ¥127.78 | 涨跌幅: 0.0% → 2.3%
# ✅ [铁矿石] 2025-10-25 | 价格: ¥890.0 | 涨跌幅: 0.0% → 1.8%
# ⏭️  [焦炭] 2025-10-18 | 价格: ¥2180.0 | 跳过（无历史数据）
# ============================================================
# ✅ 成功更新 42 条记录
# ⏭️  跳过 3 条记录（无历史数据）

# 强制重新计算所有数据（不推荐，除非数据有误）
python scripts/recalculate_market_change_rate.py --force
```

**注意事项**：
- ✅ 上传数据时按日期排序（从旧到新），确保计算准确
- ✅ 至少上传 7 天以上的连续数据，否则早期数据无法计算涨跌幅
- ✅ 如果手动提供了正确的 `change_rate`，系统不会覆盖
- ⚠️  脚本只计算 7 天前的数据作为基准，如果间隔超过 7 天，可能找不到对比数据

#### 3. 查看市场数据

**前端页面**：
- 访问：`http://localhost:3000/dashboard/market`
- 功能：
  - 实时价格卡片（最新4个材料价格）
  - 市场新闻列表
  - 价格预测（7天趋势）
  - 数据刷新按钮
  - 上传数据按钮（管理员/经理）

**API查询**：
```bash
# 获取价格数据
curl http://localhost:8000/api/market/prices?material_type=铁矿石&limit=10

# 获取市场新闻
curl http://localhost:8000/api/market/news?category=供应&limit=10

# 获取趋势分析
curl http://localhost:8000/api/market/analysis/trend

# 获取市场概况
curl http://localhost:8000/api/market/analysis/summary
```

#### 4. 通过Agent查询

切换到"市场分析师"Agent，询问市场问题：

**示例问题**：
- "铁矿石最近一周的价格是多少？"
- "螺纹钢的价格趋势如何？"
- "查询最近的市场新闻"
- "比较铁矿石、螺纹钢、焦炭的价格"

**Agent工具调用示例**：
```python
# Agent 内部会调用 MarketQueryTool
# 查询类型：price, news, trend, compare

# 查询价格
tool.execute(query_type="price", material_type="铁矿石", days=7)

# 查询趋势
tool.execute(query_type="trend", material_type="螺纹钢")

# 比较价格
tool.execute(query_type="compare", material_types=["铁矿石", "螺纹钢", "焦炭"])

# 查询新闻
tool.execute(query_type="news", category="供应", days=7)
```

### 数据库表结构

#### market_price_data (价格数据表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| material_type | VARCHAR(64) | 材料类型（铁矿石、螺纹钢等） | ✅ |
| category | VARCHAR(32) | 分类（raw_material/product） | ✅ |
| price | FLOAT | 价格（元/吨） | ✅ |
| unit | VARCHAR(16) | 单位（默认"元/吨"） | - |
| region | VARCHAR(64) | 地区 | - |
| source | VARCHAR(128) | 数据来源 | - |
| price_date | DATETIME | 价格日期 | ✅ |
| change_rate | FLOAT | 涨跌幅（%） | - |
| change_amount | FLOAT | 涨跌金额 | - |
| volume | FLOAT | 成交量（吨） | - |
| high_price | FLOAT | 最高价 | - |
| low_price | FLOAT | 最低价 | - |
| meta_data | JSON | 其他元数据 | - |
| created_at | DATETIME | 创建时间 | - |
| created_by | BIGINT | 创建者ID | - |

**索引**：
- `idx_material_date`: (material_type, price_date)
- `idx_category_date`: (category, price_date)
- `idx_date`: (price_date)

#### market_news (市场新闻表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| title | VARCHAR(256) | 新闻标题 | ✅ |
| content | TEXT | 新闻内容 | - |
| summary | TEXT | 摘要 | - |
| source | VARCHAR(128) | 来源 | ✅ |
| category | VARCHAR(64) | 分类（供应/需求/政策等） | ✅ |
| url | VARCHAR(512) | 原文链接 | - |
| publish_time | DATETIME | 发布时间 | ✅ |
| sentiment | VARCHAR(16) | 情绪（positive/negative/neutral） | - |
| keywords | JSON | 关键词列表 | - |
| related_materials | JSON | 相关材料列表 | - |
| is_important | BOOLEAN | 是否重要（默认False） | - |
| meta_data | JSON | 其他元数据 | - |
| created_at | DATETIME | 创建时间 | - |
| created_by | BIGINT | 创建者ID | - |

**索引**：
- `idx_category_time`: (category, publish_time)
- `idx_publish_time`: (publish_time)

#### market_data_source (数据源配置表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| name | VARCHAR(128) | 数据源名称（唯一） | ✅ |
| source_type | VARCHAR(32) | 类型（api/upload/manual） | ✅ |
| api_url | VARCHAR(512) | API地址 | - |
| api_key | VARCHAR(256) | API密钥 | - |
| headers | JSON | 请求头 | - |
| params | JSON | 请求参数 | - |
| data_format | VARCHAR(32) | 数据格式（json/xml/csv） | - |
| update_frequency | INTEGER | 更新频率（分钟） | - |
| is_active | BOOLEAN | 是否激活（默认True） | - |
| last_update | DATETIME | 最后更新时间 | - |
| error_count | INTEGER | 错误次数 | - |
| description | TEXT | 描述 | - |
| meta_data | JSON | 其他配置 | - |
| created_at | DATETIME | 创建时间 | - |
| updated_at | DATETIME | 更新时间 | - |
| created_by | BIGINT | 创建者ID | - |

### API端点列表

#### 价格数据 API
- `GET /api/market/prices` - 获取价格数据列表
  - 参数：`material_type`, `category`, `start_date`, `end_date`, `limit`
  - 返回：`PriceData[]`
  
- `POST /api/market/prices` - 创建价格数据
  - 权限：经理或管理员
  - 请求体：`PriceDataCreate`
  - 返回：`PriceData`

- `POST /api/market/prices/batch-upload` - 批量上传价格数据
  - 权限：经理或管理员
  - 请求体：`multipart/form-data` (file字段)
  - 返回：`BatchUploadResponse`

- `DELETE /api/market/prices/{price_id}` - 删除价格数据
  - 权限：经理或管理员

#### 市场新闻 API
- `GET /api/market/news` - 获取市场新闻列表
  - 参数：`category`, `start_date`, `end_date`, `is_important`, `limit`
  - 返回：`MarketNews[]`

- `POST /api/market/news` - 创建市场新闻
  - 权限：经理或管理员
  - 请求体：`NewsCreate`
  - 返回：`MarketNews`

#### 趋势分析 API
- `GET /api/market/analysis/trend` - 获取趋势分析
  - 参数：`material_types` (可选，默认["铁矿石", "螺纹钢", "焦炭", "废钢"])
  - 返回：`TrendAnalysis[]`

- `GET /api/market/analysis/summary` - 获取市场概况
  - 返回：`MarketSummary`

#### 数据源管理 API
- `GET /api/market/data-sources` - 获取数据源列表
  - 权限：经理或管理员
  - 返回：`DataSource[]`

- `POST /api/market/data-sources` - 创建数据源
  - 权限：经理或管理员
  - 请求体：`DataSourceCreate`
  - 返回：`DataSource`

### 权限控制

| 操作 | ADMIN | MANAGER | TECHNICIAN |
|-----|-------|---------|------------|
| 查看价格数据 | ✅ | ✅ | ✅ |
| 查看市场新闻 | ✅ | ✅ | ❌ |
| 查看趋势分析 | ✅ | ✅ | ❌ |
| 上传价格数据 | ✅ | ✅ | ❌ |
| 创建/删除数据 | ✅ | ✅ | ❌ |
| 管理数据源 | ✅ | ✅ | ❌ |
| 使用Market Agent | ✅ | ✅ | ❌ |

### 趋势分析算法

系统使用简单的统计方法计算趋势：

1. **7天/30天平均价格**：
   ```python
   avg_price_7d = sum(prices[-7:]) / 7
   avg_price_30d = sum(prices[-30:]) / 30
   ```

2. **涨跌幅计算**：
   ```python
   change_rate_7d = (current_price - avg_price_7d) / avg_price_7d * 100
   ```

3. **趋势判断**：
   - `change_rate_7d > 2%` → 上涨
   - `change_rate_7d < -2%` → 下跌
   - 其他 → 震荡

4. **预测区间**（简单估计）：
   ```python
   forecast_min = current_price * 0.98
   forecast_max = current_price * 1.02
   forecast_avg = (forecast_min + forecast_max) / 2
   ```

5. **置信度评估**：
   - 数据点 ≥ 7 → 高
   - 数据点 3-6 → 中等
   - 数据点 < 3 → 低

### Mysteel数据爬虫（自动采集）

#### 功能说明
系统提供基于 Selenium 的自动化爬虫工具，可从我的钢铁网（Mysteel）自动采集钢材价格数据。

**🎉 最新更新**: 
- ✅ **v2.2 (2025-10-28)**: 修复数据日期一致问题，支持按周循环爬取历史数据
- ✅ **v2.1**: 统一CLI工具（mysteel_cli.py）
- ✅ **v2.1**: 修复日期输入问题（JavaScript直接填充 + 动态查找日历）
- ✅ **v2.1**: 修复材料定位问题（多种查找方式）
- ✅ **v2.1**: 新增诊断工具（diagnose_mysteel_date_picker.py）

**🔧 v2.2 重要修复**：
- **问题**：之前所有爬取的数据日期都相同（都是"当前周的周一"）
- **原因**：代码只提取一次数据，并将所有数据标记为同一个日期
- **解决方案**：
  - 将日期范围按周拆分（如 2025-01-01 到 2025-01-31 拆分为 4-5 周）
  - 每周单独查询一次网站
  - 为每周的数据标记正确的日期（该周的周一）
  - 最后合并所有周的数据
- **效果**：现在爬取21天数据，会得到3周的数据，每周的日期都不同

#### 安装依赖
```bash
# 安装爬虫相关依赖
pip install selenium webdriver-manager pandas

# 或更新完整依赖
pip install -r requirements.txt
```

**注意**: 需要安装 Google Chrome 浏览器，ChromeDriver 会自动下载管理。

#### 快速开始（推荐使用统一CLI）

**1. 测试连接**
```bash
python scripts/mysteel_cli.py test
```

**2. 爬取单个材料**
```bash
# 爬取螺纹钢最近21天数据（默认，确保能计算涨跌幅）
python scripts/mysteel_cli.py crawl --material 螺纹 --days 21 --save-db

# 爬取铁矿石指定日期范围
python scripts/mysteel_cli.py crawl --material 铁矿石 \
    --start-date 2025-01-01 --end-date 2025-01-31 --save-db
```

**3. 批量爬取多种材料（推荐）**
```bash
# 批量爬取默认材料（螺纹、铁矿石、焦炭、热卷），默认21天
python scripts/mysteel_cli.py batch --save-db -y

# 批量爬取指定材料
python scripts/mysteel_cli.py batch \
    --materials "螺纹,铁矿石,焦炭" \
    --days 21 \
    --save-db \
    -y
```

**📌 为什么默认 21 天？**
- 涨跌幅计算需要对比 7 天前的数据
- 即使在周一爬取，也能保证有足够的历史数据（至少两周）
- 21 天 = 3 周，确保数据完整性

**4. 列出支持的材料类型**
```bash
python scripts/mysteel_cli.py list
```

**5. 诊断问题**
```bash
python scripts/mysteel_cli.py diagnose
```

#### 统一CLI命令速查

| 命令 | 说明 | 示例 |
|------|------|------|
| `crawl` | 爬取单个材料 | `python scripts/mysteel_cli.py crawl --material 螺纹` |
| `batch` | 批量爬取多个材料 | `python scripts/mysteel_cli.py batch --save-db -y` |
| `test` | 测试连接 | `python scripts/mysteel_cli.py test` |
| `list` | 列出支持的材料 | `python scripts/mysteel_cli.py list` |
| `diagnose` | 诊断网站结构 | `python scripts/mysteel_cli.py diagnose` |

**快捷脚本**:
```bash
# Windows
scripts\mysteel crawl --material 螺纹 --days 21

# Linux/Mac
./scripts/mysteel.sh crawl --material 螺纹 --days 21
```

#### 支持的材料类型

| 材料名称 | 英文ID | 分类 | 说明 |
|---------|-------|------|-----|
| 螺纹 | LUOWEN | product | 螺纹钢 |
| 热卷 | REJUAN | product | 热轧卷板 |
| 冷卷 | LENGJUAN | product | 冷轧卷板 |
| 中厚板 | ZHONGHOUBAN | product | 中厚板 |
| 铁矿石 | TEKUANGSHI | raw_material | 铁矿石 |
| 焦炭 | JIAOTA | raw_material | 焦炭 |

#### 命令行参数

| 参数 | 说明 | 默认值 | 示例 |
|-----|------|-------|------|
| `--material` | 材料类型 | `螺纹` | `--material 铁矿石` |
| `--days` | 爬取天数 | `21` | `--days 21` |
| `--start-date` | 开始日期 | 21天前 | `--start-date 2025-01-01` |
| `--end-date` | 结束日期 | 昨天 | `--end-date 2025-01-31` |
| `--output` | CSV输出路径 | 自动生成 | `--output data.csv` |
| `--save-db` | 保存到数据库 | False | `--save-db` |
| `--headless` | 无头模式 | True | `--headless` |

#### 自动化定时任务

**方法1：Python APScheduler（推荐）**
在 `main.py` 中添加：
```python
from apscheduler.schedulers.background import BackgroundScheduler
from scripts.crawl_mysteel_data import MysteelCrawler
from datetime import datetime, timedelta

def scheduled_crawl():
    """每天定时爬取最新数据"""
    crawler = MysteelCrawler(headless=True)
    try:
        materials = ["螺纹", "铁矿石", "焦炭", "热卷"]
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        for material in materials:
            df = crawler.crawl_price_data(material, yesterday, today)
            crawler.save_to_database(df)
            time.sleep(5)  # 避免频繁请求
    finally:
        crawler.close()

# 启动定时任务
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_crawl, 'cron', hour=9, minute=0)  # 每天9点
scheduler.start()
```

#### 输出格式

**CSV文件示例**:
```csv
material_type,category,price,unit,source,price_date,change_rate,change_amount
螺纹钢,product,4250.0,元/吨,Mysteel,2025-01-22,2.3,95.0
螺纹钢,product,4155.0,元/吨,Mysteel,2025-01-21,-0.5,-21.0
```

**数据库字段**:
- 自动写入 `market_price_data` 表
- 字段完全兼容系统标准格式
- `source` 字段自动标记为 "Mysteel"

#### 故障排查

**快速诊断**：
```bash
# 1. 运行连接测试（推荐首先执行）
python scripts/test_mysteel_connection.py

# 2. 如果测试通过，运行爬虫
python scripts/crawl_mysteel_data.py --material 螺纹

# 3. 如果仍然失败，查看完整故障排查指南
```

**常见问题快速解决**：

**问题1：SSL 握手失败 / 网络连接错误**
```bash
# 症状
ERROR: handshake failed; net_error -107/-100
WinError 10013 访问套接字失败

# 解决方案（按优先级）
1. 关闭防火墙/VPN 后重试
2. 检查系统代理设置: netsh winhttp show proxy
3. 运行测试脚本验证: python scripts/test_mysteel_connection.py
4. 脚本已自动忽略 SSL 错误和添加重试机制（已优化）
```

**问题2：ChromeDriver 版本不匹配**
```bash
# 症状
selenium.common.exceptions.SessionNotCreatedException

# 解决
pip install --upgrade webdriver-manager selenium
# 或手动下载匹配版本: https://chromedriver.chromium.org/
```

**问题3：GPU/WebGL 警告**
```bash
# 症状（可安全忽略）
GPU stall due to ReadPixels
Automatic fallback to software WebGL

# 说明
这些是性能警告，不影响数据爬取功能
脚本已自动优化配置以减少警告输出
```

**问题4：浏览器进程残留**
```bash
# 症状
WinError 10013 或端口占用

# 解决（Windows）
taskkill /F /IM chrome.exe /T
taskkill /F /IM chromedriver.exe /T

# 脚本已自动处理（在 close() 方法中）
```

**问题5：网站结构变化**
```bash
# 使用非无头模式调试（可以看到浏览器）
python scripts/crawl_mysteel_data.py --material 螺纹 --headless false

# 查看自动保存的错误截图
dir error_screenshot_*.png
```

**问题6：爬取被封IP**
- 增加延迟时间（每次请求间隔 ≥ 5秒）
- 降低爬取频率（每天一次而非每小时）
- 考虑使用官方 API 接口（更稳定合规）

**问题7：数据为空**
- 检查日期范围是否合理（不能超过当前日期）
- 查看日志输出的详细错误信息
- 手动访问网站验证: https://index.mysteel.com/
- 运行测试脚本诊断问题

**问题8：日期没有确定 / 日期输入失败（已修复✅）**
```bash
# 症状
ERROR: 日期没有确定
输入框仍为空 / 日期选择后未填充

# 根本原因
1. 输入框是只读的（readonly="readonly"），必须通过日历选择器填充
2. 日历容器路径动态变化（硬编码 div[3] 可能失效）
3. JavaScript 事件未正确触发（change/input/blur）

# 解决方案（v2.1 已自动修复）
✅ 优先使用 JavaScript 直接填充（成功率 >95%）
✅ 动态查找日历容器（自适应网站结构变化）
✅ 多重备用方案（一种失败自动尝试下一种）
✅ 详细日志 + 截图（便于调试）

# 诊断工具（如仍然失败）
python scripts/diagnose_mysteel_date_picker.py  # 查找日历容器路径

# 代码改进（已应用到 crawl_mysteel_data.py）
- 方法1: JavaScript 直接填充 + 触发所有事件（input/change/blur/keyup/keydown）
- 方法2: 动态查找日历选择器（遍历 div[1-15]，自动识别年份选择器）
- 方法3: 多重验证机制（每步操作后检查输入框值）
- 保存失败截图: date_input_failed_*.png

# 技术细节
输入框特性: <input id="startWeek" readonly="readonly" class="dataWekStyle">
- readonly: 禁止键盘输入，只能通过日历或 JavaScript 填充
- dataWekStyle: 绑定了日期选择器插件（Bootstrap Datepicker 或自定义）
- 动态日历: 点击后才在 <body> 中插入日历 DOM

# 验证修复
python scripts/mysteel_cli.py crawl --material 螺纹 --days 7 --headless false
# 应该看到日志：
# ✅ JavaScript填充成功：start输入框值 = 2025-01-15
# ✅ JavaScript填充成功：end输入框值 = 2025-01-22
```

**完整故障排查指南**：
详见 [Mysteel CLI 指南 - 故障排查部分](docs/MYSTEEL_CLI_GUIDE.md#故障排查)
---

### 外部API接入（可选）

如果有外部市场数据API，可以配置数据源：

**步骤**：
1. 以管理员身份登录
2. 访问 `/api/market/data-sources` 创建数据源
3. 配置API地址、密钥、更新频率
4. 编写定时任务调用外部API
5. 将获取的数据写入 `market_price_data` 表

**示例数据源配置**：
```json
{
  "name": "Mysteel API",
  "source_type": "api",
  "api_url": "https://api.mysteel.com/v1/prices",
  "api_key": "YOUR_API_KEY",
  "headers": {"Content-Type": "application/json"},
  "data_format": "json",
  "update_frequency": 60,
  "description": "Mysteel钢铁价格数据"
}
```

### 故障排查

#### 问题：上传文件失败
**解决方案**：
1. 检查文件格式（仅支持.xlsx, .xls, .csv）
2. 验证必填列：`material_type`, `category`, `price`, `price_date`
3. 检查日期格式：`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`
4. 查看后端日志：`tail -f backend.log`

#### 问题：前端显示模拟数据
**原因**：数据库中无价格数据

**解决方案**：
1. 上传数据文件
2. 或通过API创建数据：
   ```bash
   curl -X POST http://localhost:8000/api/market/prices \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "material_type": "铁矿石",
       "category": "raw_material",
       "price": 890,
       "price_date": "2025-10-22T00:00:00"
     }'
   ```

#### 问题：Agent无法查询市场数据
**解决方案**：
1. 确认MarketQueryTool已注册：
   ```bash
   python -c "from src.agent.steel_tools import register_steel_tools; \
              print('Market tool loaded' if any('market' in t.name for t in []) else 'Not found')"
   ```
2. 重启后端服务
3. 查看Agent工具列表

### 最佳实践

1. ✅ **定期更新数据**：每天或每周上传最新价格数据
2. ✅ **数据一致性**：使用相同的`material_type`命名（避免"铁矿石"和"铁矿"混用）
3. ✅ **添加数据来源**：填写`source`字段，便于追溯
4. ✅ **区分原料和产品**：正确设置`category`（raw_material/product）
5. ✅ **记录成交量**：填写`volume`字段，用于分析市场活跃度
6. ✅ **备份数据**：定期导出数据库备份
7. ❌ 避免重复上传相同日期的数据（会导致冗余）
8. ❌ 避免价格异常值（如负数、超大值）

---

## Steel Equipment Monitoring System (钢铁设备监控系统)

### 功能说明
钢铁设备监控系统提供设备传感器数据管理、故障预测和预警功能。基于机器学习模型（随机森林）实现智能故障检测，支持实时监控和历史数据分析。

### 核心特性
1. **传感器数据管理**: 温度、压力、振动、湿度等传感器数据的采集和存储
2. **智能故障预测**: 基于 ML 模型预测设备故障概率和故障类型
3. **批量预测**: 支持多设备并行故障诊断
4. **设备管理**: 设备信息管理（类型、位置、状态、维护记录）
5. **统计分析**: 设备健康度、故障率、传感器数据趋势
6. **模型训练**: 自定义模型训练和版本管理

### 快速开始

#### 1. 数据库准备（已在 `models.py` 中定义）
系统自动创建以下数据表：
- `equipment` - 设备信息表
- `sensor_data` - 传感器数据表
- `fault_prediction` - 故障预测记录表
- `ml_model` - ML 模型版本管理表

#### 2. 生成测试数据
```bash
# 生成1000条测试数据（包含15%故障样本）
python scripts/generate_test_data.py --n-samples 1000 --output equipment_fault_data.csv

# 输出示例：
# ✅ 已生成测试数据: equipment_fault_data.csv
#    样本数: 1000
#    故障样本: 153 (15.3%)
#    设备类型: {'Turbine': 339, 'Compressor': 334, 'Pump': 327}
```

**数据格式**：
```csv
temperature,pressure,vibration,humidity,equipment_type,location,faulty
70.5,40.2,1.45,50.3,Turbine,Atlanta,0
89.3,54.8,3.52,48.9,Turbine,Chicago,1
```

#### 3. 训练故障检测模型
```bash
# 训练模型（使用默认参数）
python scripts/train_fault_detector.py --data equipment_fault_data.csv

# 自定义参数训练
python scripts/train_fault_detector.py \
    --data equipment_fault_data.csv \
    --n-estimators 200 \
    --max-depth 15 \
    --test-size 0.25
```

**训练输出示例**：
```
🚀 开始训练设备故障检测模型
============================================================
📖 加载训练数据: equipment_fault_data.csv
✅ 加载完成: 1000 条记录

📋 设备类型分布:
   Turbine: 339 个样本, 故障: 52 (15.3%)
   Compressor: 334 个样本, 故障: 51 (15.3%)
   Pump: 327 个样本, 故障: 50 (15.3%)

📊 特征维度: (1000, 6)
📊 故障样本: 153 (15.3%)

🔄 开始训练随机森林模型...
   参数: n_estimators=100, max_depth=10

📈 评估模型性能...

📊 模型性能:
   准确率: 0.9650
   精确率: 0.8929
   召回率: 0.9032
   F1分数: 0.8980

🔍 特征重要性:
   temperature: 0.3245
   vibration: 0.2987
   pressure: 0.2134
   humidity: 0.0821
   equipment_type: 0.0513
   location: 0.0300

🔄 交叉验证...
   CV F1均值: 0.8912 (±0.0234)

💾 模型已保存: data/ml_models/fault_detector_20251026_133808.pkl

============================================================
✅ 训练完成!
============================================================
📊 模型版本: 1.0.0
📊 训练样本: 800
📊 测试样本: 200
📊 准确率: 0.9650
📊 F1分数: 0.8980
📂 模型路径: data/ml_models/fault_detector_20251026_133808.pkl
```

#### 4. 使用 API 进行故障预测

**方式一：单次预测**
```bash
curl -X POST http://localhost:8000/api/equipment/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "temperature": 89.5,
    "pressure": 55.2,
    "vibration": 3.45,
    "humidity": 48.7,
    "equipment_type": "Turbine",
    "location": "Chicago"
  }'
```

**响应示例**：
```json
{
  "fault_probability": 0.8723,
  "is_faulty": true,
  "confidence": 0.8723,
  "model_version": "1.0.0"
}
```

**方式二：批量预测**
```bash
curl -X POST http://localhost:8000/api/equipment/predict-batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '[
    {"temperature": 70.5, "pressure": 40.2, "vibration": 1.45, "humidity": 50.3},
    {"temperature": 89.3, "pressure": 54.8, "vibration": 3.52, "humidity": 48.9}
  ]'
```

#### 5. 管理传感器数据

**创建传感器数据**：
```bash
curl -X POST http://localhost:8000/api/equipment/sensor-data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "equipment_id": 1,
    "temperature": 70.5,
    "pressure": 40.2,
    "vibration": 1.45,
    "humidity": 50.3,
    "is_faulty": false
  }'
```

**查询传感器数据**：
```bash
# 查询指定设备的传感器数据
curl "http://localhost:8000/api/equipment/sensor-data?equipment_id=1&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查询所有设备的传感器数据
curl "http://localhost:8000/api/equipment/sensor-data?limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 6. 查看设备统计信息

```bash
curl http://localhost:8000/api/equipment/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应示例**：
```json
{
  "total_equipment": 15,
  "active_equipment": 12,
  "total_sensor_data": 5432,
  "faulty_count": 823,
  "faulty_rate": 15.15
}
```

### 数据库表结构

#### equipment (设备信息表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| equipment_type | VARCHAR(64) | 设备类型（Turbine/Compressor/Pump等） | ✅ |
| location | VARCHAR(64) | 位置 | ✅ |
| description | TEXT | 描述 | - |
| is_active | BOOLEAN | 是否激活（默认True） | - |
| installation_date | DATETIME | 安装日期 | - |
| last_maintenance | DATETIME | 最后维护时间 | - |
| created_at | DATETIME | 创建时间 | - |
| updated_at | DATETIME | 更新时间 | - |

**索引**：
- `idx_equipment_type`: (equipment_type)
- `idx_location`: (location)
- `idx_is_active`: (is_active)

#### sensor_data (传感器数据表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| equipment_id | BIGINT | 设备ID（外键） | ✅ |
| temperature | FLOAT | 温度（℃） | ✅ |
| pressure | FLOAT | 压力（psi） | ✅ |
| vibration | FLOAT | 振动（mm/s） | ✅ |
| humidity | FLOAT | 湿度（%） | ✅ |
| recorded_at | DATETIME | 记录时间 | ✅ |
| is_faulty | BOOLEAN | 是否故障 | - |
| created_at | DATETIME | 创建时间 | - |

**索引**：
- `idx_equipment_recorded`: (equipment_id, recorded_at DESC)
- `idx_recorded_at`: (recorded_at DESC)
- `idx_is_faulty`: (is_faulty)

#### fault_prediction (故障预测记录表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| equipment_id | BIGINT | 设备ID（外键） | ✅ |
| fault_probability | FLOAT | 故障概率（0-1） | ✅ |
| predicted_fault_type | VARCHAR(64) | 预测故障类型 | - |
| model_version | VARCHAR(32) | 模型版本 | ✅ |
| confidence | FLOAT | 置信度（0-1） | - |
| predicted_at | DATETIME | 预测时间 | ✅ |
| is_confirmed | BOOLEAN | 是否确认（默认False） | - |
| created_at | DATETIME | 创建时间 | - |

**索引**：
- `idx_equipment_predicted`: (equipment_id, predicted_at DESC)
- `idx_predicted_at`: (predicted_at DESC)

#### ml_model (ML 模型版本表)
| 字段 | 类型 | 说明 | 必填 |
|-----|------|------|-----|
| id | BIGINT | 主键 | - |
| model_name | VARCHAR(128) | 模型名称 | ✅ |
| model_version | VARCHAR(32) | 模型版本 | ✅ |
| model_type | VARCHAR(64) | 模型类型（RandomForest/XGBoost等） | ✅ |
| model_path | VARCHAR(256) | 模型文件路径 | ✅ |
| metrics | JSON | 模型性能指标 | - |
| hyperparameters | JSON | 超参数 | - |
| training_samples | INTEGER | 训练样本数 | - |
| is_active | BOOLEAN | 是否激活（默认False） | - |
| trained_at | DATETIME | 训练时间 | ✅ |
| created_at | DATETIME | 创建时间 | - |
| created_by | BIGINT | 创建者ID | - |

**索引**：
- `idx_model_name_version`: (model_name, model_version)
- `idx_is_active`: (is_active)

### API 端点列表

#### 传感器数据 API
- `POST /api/equipment/sensor-data` - 创建传感器数据
  - 权限：所有登录用户
  - 请求体：`SensorDataCreate`
  - 返回：`SensorDataResponse`

- `GET /api/equipment/sensor-data` - 获取传感器数据列表
  - 参数：`equipment_id` (可选), `limit`, `offset`
  - 返回：`List[SensorDataResponse]`

#### 故障预测 API
- `POST /api/equipment/predict` - 预测设备故障
  - 权限：所有登录用户
  - 请求体：`PredictRequest`
  - 返回：`PredictResponse`

- `POST /api/equipment/predict-batch` - 批量预测设备故障
  - 权限：所有登录用户
  - 请求体：`List[PredictRequest]`
  - 返回：`List[Dict[str, Any]]`

#### 设备管理 API
- `GET /api/equipment/equipment` - 获取设备列表
  - 参数：`equipment_type`, `location`, `is_active`
  - 返回：`List[EquipmentResponse]`

#### 故障预测记录 API
- `GET /api/equipment/fault-predictions` - 获取故障预测记录
  - 参数：`equipment_id` (可选), `limit`, `offset`
  - 返回：`List[FaultPredictionResponse]`

#### 统计信息 API
- `GET /api/equipment/stats` - 获取设备统计信息
  - 返回：`Dict[str, Any]`

### ML 模型技术细节

#### 1. 特征工程
**传感器特征**（连续型）：
- `temperature` - 温度（℃）
- `pressure` - 压力（psi）
- `vibration` - 振动（mm/s）
- `humidity` - 湿度（%）

**分类特征**（离散型）：
- `equipment_type` - 设备类型（Turbine/Compressor/Pump）
- `location` - 位置（Atlanta/Chicago/San Francisco/New York/Houston）

#### 2. 模型架构
- **算法**: Random Forest Classifier
- **默认参数**:
  - `n_estimators=100` - 树的数量
  - `max_depth=10` - 最大深度
  - `class_weight='balanced'` - 平衡类别权重
  - `n_jobs=-1` - 并行训练
  - `random_state=42` - 随机种子

#### 3. 模型评估指标
- **准确率** (Accuracy) - 整体预测准确度
- **精确率** (Precision) - 预测为故障的样本中真实故障的比例
- **召回率** (Recall) - 真实故障的样本中被预测出的比例
- **F1 分数** (F1 Score) - 精确率和召回率的调和平均
- **交叉验证** (Cross-Validation) - 5折交叉验证评估泛化能力

#### 4. 特征重要性示例
```
特征              重要性
temperature      0.3245  ← 最重要
vibration        0.2987
pressure         0.2134
humidity         0.0821
equipment_type   0.0513
location         0.0300
```

#### 5. 模型版本管理
- 模型文件: `data/ml_models/fault_detector_{timestamp}.pkl`
- 元数据文件: `data/ml_models/fault_detector_{timestamp}.pkl.metadata.json`
- 自动加载最新版本模型
- 支持多版本并存和回滚

### 权限控制

| 操作 | ADMIN | MANAGER | TECHNICIAN |
|-----|-------|---------|------------|
| 查看传感器数据 | ✅ | ✅ | ✅ |
| 创建传感器数据 | ✅ | ✅ | ✅ |
| 查看故障预测 | ✅ | ✅ | ✅ |
| 执行故障预测 | ✅ | ✅ | ✅ |
| 批量预测 | ✅ | ✅ | ✅ |
| 查看设备信息 | ✅ | ✅ | ✅ |
| 训练模型 | ✅ | ✅ | ❌ |
| 管理设备 | ✅ | ✅ | ❌ |

### 使用场景

#### 场景 1：实时监控预警
```python
# 定时采集传感器数据并预测
import schedule
import time

def monitor_equipment(equipment_id):
    # 1. 采集传感器数据
    sensor_data = read_sensors(equipment_id)
    
    # 2. 调用预测 API
    response = requests.post(
        "http://localhost:8000/api/equipment/predict",
        json=sensor_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # 3. 判断预警
    result = response.json()
    if result['fault_probability'] > 0.7:
        send_alert(f"设备 {equipment_id} 故障概率: {result['fault_probability']:.2%}")

# 每5分钟执行一次
schedule.every(5).minutes.do(monitor_equipment, equipment_id=1)

while True:
    schedule.run_pending()
    time.sleep(1)
```

#### 场景 2：批量健康度评估
```python
# 评估所有设备的健康度
equipment_list = requests.get(
    "http://localhost:8000/api/equipment/equipment",
    headers={"Authorization": f"Bearer {token}"}
).json()

sensor_data_list = []
for equipment in equipment_list:
    latest_data = get_latest_sensor_data(equipment['id'])
    sensor_data_list.append(latest_data)

# 批量预测
predictions = requests.post(
    "http://localhost:8000/api/equipment/predict-batch",
    json=sensor_data_list,
    headers={"Authorization": f"Bearer {token}"}
).json()

# 生成健康度报告
for equipment, prediction in zip(equipment_list, predictions):
    print(f"{equipment['equipment_type']} ({equipment['location']}): "
          f"故障概率 {prediction['fault_probability']:.2%}")
```

#### 场景 3：模型重新训练
```bash
# 1. 导出最近3个月的传感器数据
python scripts/export_sensor_data.py --start-date 2025-08-01 --end-date 2025-10-31 --output training_data.csv

# 2. 训练新模型
python scripts/train_fault_detector.py --data training_data.csv --n-estimators 200 --max-depth 15

# 3. 评估新模型性能
# 如果性能提升，新模型会自动成为活跃模型

# 4. 重启后端服务加载新模型
python manage.py start backend
```

### 故障排查

#### 问题：模型未加载
**症状**：
```json
{
  "detail": "模型未加载，请先调用 load_model() 或 train()"
}
```

**解决方案**：
1. 训练新模型：
   ```bash
   python scripts/train_fault_detector.py --data equipment_fault_data.csv
   ```
2. 重启后端服务：
   ```bash
   python manage.py start backend
   ```
3. 检查模型文件是否存在：
   ```bash
   ls data/ml_models/
   ```

#### 问题：预测准确率低
**解决方案**：
1. 增加训练样本数量
2. 调整模型超参数：
   ```bash
   python scripts/train_fault_detector.py \
       --data training_data.csv \
       --n-estimators 200 \
       --max-depth 15
   ```
3. 检查数据质量（是否有异常值、缺失值）
4. 增加特征工程（如时间窗口统计特征）

#### 问题：特定设备类型预测不准
**解决方案**：
1. 检查该设备类型的训练样本数量
2. 增加该设备类型的数据采集
3. 考虑为不同设备类型训练独立模型

#### 问题：传感器数据无法创建
**解决方案**：
1. 确认设备存在：
   ```bash
   curl "http://localhost:8000/api/equipment/equipment" -H "Authorization: Bearer $TOKEN"
   ```
2. 检查传感器数据格式
3. 验证数据类型（temperature/pressure/vibration/humidity 必须为 float）

### 最佳实践

1. ✅ **定期重新训练**: 每月或每季度重新训练模型，使用最新数据
2. ✅ **数据清洗**: 过滤异常值和缺失值
3. ✅ **特征归一化**: 对传感器数据进行标准化（如果需要）
4. ✅ **交叉验证**: 使用交叉验证评估模型泛化能力
5. ✅ **阈值调整**: 根据实际业务需求调整故障判断阈值（默认 0.5）
6. ✅ **监控日志**: 记录预测结果和实际故障情况，用于模型改进
7. ✅ **多模型对比**: 尝试不同算法（XGBoost、LightGBM、神经网络）
8. ❌ 避免过拟合：控制模型复杂度（max_depth 不宜过大）
9. ❌ 避免数据泄露：训练/测试集严格分离

### 未来扩展方向

1. 🔮 **多分类故障诊断**: 不仅判断是否故障，还判断故障类型（过热/过压/振动异常/磨损等）
2. 🔮 **时间序列预测**: 基于历史趋势预测未来故障时间
3. 🔮 **异常检测**: 使用无监督学习检测未知故障模式
4. 🔮 **深度学习**: 使用 LSTM/Transformer 捕捉时序依赖
5. 🔮 **联邦学习**: 跨工厂协同训练，保护数据隐私
6. 🔮 **可解释性**: 使用 SHAP/LIME 解释预测结果
7. 🔮 **在线学习**: 模型持续学习新数据，自动更新
8. 🔮 **多模态融合**: 结合音频、振动频谱、红外图像等多模态数据

---

## Process Workflow Management System (工艺流程管理系统)

### 功能说明
工艺流程管理系统提供钢铁生产全流程的可视化展示和工艺参数管理功能。用户可以直观地查看生产流程、检查工艺参数。

### 核心特性
1. **交互式工艺流程图**: 钢铁生产全流程可视化（原料→炼铁→炼钢→轧钢→成品）
2. **工艺节点详情**: 查看每个工序的标准参数、设备信息
3. **多视图切换**: 支持流程图视图和列表视图
4. **参数监控**: 展示标准参数值和范围
5. **缩放控制**: 支持流程图缩放（50%-150%）

### 快速开始

#### 1. 访问工艺流程页面
```bash
# 启动前端服务
cd frontend
npm run dev

# 访问页面
http://localhost:3000/dashboard/workflow
```

#### 2. 查看工艺流程
- **流程图视图**: 点击页面左上角的"流程视图"查看完整生产流程
- **列表视图**: 切换到"列表视图"查看所有工艺节点列表
- **缩放控制**: 使用 + / - 按钮调整流程图缩放比例（50%-150%）

#### 3. 查看节点详情
- 点击流程图中的任意节点（如"转炉炼钢"）
- 右侧面板显示节点详细信息：
  - 工艺参数（温度、压力、流量等）
  - 标准值和范围
  - 节点类型和参数数量

### 工艺流程节点说明

#### 钢铁生产主要工序

| 节点名称 | 类型 | 说明 | 关键参数 |
|---------|------|------|---------|
| **原料准备** | 物料 | 铁矿石、焦炭、石灰石储存和配料 | 铁矿石品位、焦炭固定碳 |
| **高炉炼铁** | 工艺流程 | 通过高炉将铁矿石还原成生铁 | 炉温(1500-1600℃)、生铁含碳量 |
| **转炉炼钢** | 工艺流程 | 将生铁转化为钢水，降低碳含量 | 冶炼温度(1600-1650℃)、氧气流量 |
| **精炼处理** | 工艺流程 | 去除钢水杂质，调整化学成分 | 真空度、脱硫率、处理时间 |
| **连续铸造** | 工艺流程 | 将钢水连续浇铸成板坯、方坯 | 拉速、结晶器温度、二冷水量 |
| **加热炉** | 设备 | 将板坯加热到轧制温度 | 出炉温度(1150-1250℃) |
| **热轧** | 工艺流程 | 高温下将板坯轧制成钢板 | 轧制温度、轧制力、厚度 |
| **冷轧** | 工艺流程 | 常温下轧制，获得更薄钢板 | 轧制速度、轧制力、厚度 |
| **退火处理** | 工艺流程 | 热处理改善钢材机械性能 | 退火温度、保温时间 |
| **质量检验** | 检验点 | 机械性能和表面质量检验 | 抗拉强度、屈服强度、延伸率 |
| **成品入库** | 物料 | 合格产品包装入库 | - |

#### 节点状态标识

- 🟢 **正常**: 绿色边框，所有参数在标准范围内
- 🟡 **预警**: 黄色边框，部分参数接近阈值
- 🔴 **异常**: 红色边框，参数超出标准范围
- 🔵 **优化中**: 蓝色边框，正在进行工艺优化

### 页面布局说明

```
┌─────────────────────────────────────────────────────────────┐
│ 页面头部                                                      │
│ ┌─────────────┬──────────────────────────┐                  │
│ │ 工艺流程管理 │ 统计信息 (11个节点, 1台设备) │                  │
│ └─────────────┴──────────────────────────┘                  │
├─────────────────────────────────────────────────────────────┤
│ 主内容区                                                      │
│ ┌────────────────────────────┬──────────────────────────┐   │
│ │ 左侧 (8/12)                │ 右侧 (4/12)              │   │
│ │ ┌──────────────────────┐   │ ┌──────────────────────┐ │   │
│ │ │ 工具栏 (视图/缩放)    │   │ │ 节点详情面板         │ │   │
│ │ └──────────────────────┘   │ │                      │ │   │
│ │ ┌──────────────────────┐   │ │ [关闭按钮]           │ │   │
│ │ │ 工艺流程图           │   │ │                      │ │   │
│ │ │ (可缩放、可点击)     │   │ │ ● 工艺参数列表       │ │   │
│ │ │                      │   │ │ ● 节点类型           │ │   │
│ │ │   [节点1] → [节点2]  │   │ │ ● 参数数量           │ │   │
│ │ │      ↓         ↓     │   │ │                      │ │   │
│ │ │   [节点3] → [节点4]  │   │ │                      │ │   │
│ │ │                      │   │ │                      │ │   │
│ │ └──────────────────────┘   │ └──────────────────────┘ │   │
│ └────────────────────────────┴──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 技术实现

#### 前端文件结构
```
frontend/
├── app/dashboard/workflow/
│   └── page.tsx                        # 主页面
├── components/workflow/
│   ├── ProcessFlowChart.tsx           # 流程图组件
│   └── NodeDetailPanel.tsx            # 节点详情面板
├── lib/
│   ├── types/workflow.ts              # 类型定义
│   └── constants/processData.ts       # 工艺流程数据
```

#### 核心类型定义
```typescript
// ProcessNode - 工艺节点
interface ProcessNode {
    id: string;
    name: string;
    type: "process" | "equipment" | "inspection" | "material";
    description: string;
    position: { x: number; y: number };
    status?: "normal" | "warning" | "error" | "optimizing";
    parameters?: ProcessParameter[];
    relatedDocs?: string[];
}

// ProcessParameter - 工艺参数
interface ProcessParameter {
    name: string;
    standardValue: string | number;
    unit: string;
    actualValue?: string | number;
    range?: { min: number; max: number };
}
```

#### 组件使用示例

**ProcessFlowChart**:
```tsx
<ProcessFlowChart
    nodes={STEEL_PROCESS_NODES}
    edges={STEEL_PROCESS_EDGES}
    selectedNodeId={selectedNode?.id}
    onNodeSelect={handleNodeSelect}
/>
```

**NodeDetailPanel**:
```tsx
<NodeDetailPanel
    node={selectedNode}
    onClose={() => setSelectedNode(null)}
/>
```

### 功能增强方向

#### 已实现 ✅
1. ✅ 静态工艺流程图展示（11个主要工序）
2. ✅ 节点点击查看标准工艺参数
3. ✅ 多视图切换（流程图/列表）
4. ✅ 缩放控制（50%-150%）
5. ✅ 节点状态标识（正常/预警/异常/优化中）
6. ✅ 参数详情展示（标准值、单位、范围）

#### 待开发 🔄
1. 🔄 **工艺文档关联**: 从知识库筛选工艺文档，绑定到节点
2. 🔄 **智能工艺助手**: 集成工艺专家 Agent，提供工艺咨询
3. 🔄 **实时数据接入**: 如果有 MES/ERP 系统，显示实时参数值
4. 🔄 **参数告警**: 参数超出范围时高亮显示并推送通知
5. 🔄 **工艺路线编辑**: 管理员可以自定义工艺流程
6. 🔄 **工艺变更管理**: 记录工艺参数修改历史

#### 高级功能 🚀
1. 🚀 **知识图谱可视化**: 展示工艺参数之间的关系网络
2. 🚀 **工艺优化建议**: Agent 基于知识库提供优化方案
3. 🚀 **A/B工艺对比**: 比较不同工艺路线的差异
4. 🚀 **3D 车间布局**: 设备空间位置可视化

### 故障排查

#### 问题：页面无法访问
**解决方案**：
1. 确认前端服务已启动：`npm run dev`
2. 检查路由路径：`/dashboard/workflow`
3. 确认已登录并有权限访问

#### 问题：节点点击无反应
**解决方案**：
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认组件导入正确
3. 刷新页面清除缓存

### 最佳实践

1. ✅ **先查看流程图**：了解完整生产流程
2. ✅ **点击节点查看详情**：深入了解每个工序的参数
3. ✅ **使用缩放功能**：调整流程图大小以获得最佳视野
4. ✅ **切换视图模式**：流程图适合整体浏览，列表视图适合快速定位
5. ✅ **关注节点状态**：注意异常节点（红色边框）的参数
6. ❌ 避免频繁切换视图（影响性能）

---

## Professional Vocabulary System (专业词汇系统)

### 功能说明
系统集成了专业词汇识别和查询增强功能，能够自动识别用户查询中的钢铁行业专业术语，并提供更准确的回答。

### 核心特性
1. **自动识别专业词汇**: 在用户查询中自动识别钢种、工艺、设备等专业术语
2. **查询增强 (Query Enhancement)**: 自动添加同义词和相关术语，提高检索准确性
3. **词汇上下文注入**: 将专业词汇的定义和相关信息注入到 Prompt，帮助 Agent 理解专业术语
4. **支持同义词和关联词**: 建立词汇之间的关联关系，提升语义理解

### 工作流程
```
用户查询 "Q235钢板的抗拉强度是多少？"
    ↓
1. 专业词汇识别
   识别到: Q235 (钢种牌号)
    ↓
2. 查询增强
   原始查询: Q235钢板的抗拉强度是多少？
   增强查询: Q235钢板的抗拉强度是多少？ 碳素结构钢 屈服强度
   (添加同义词和相关术语)
    ↓
3. 向量检索
   使用增强后的查询进行 RAG 检索
    ↓
4. 上下文注入
   【专业词汇上下文】
   Q235: 碳素结构钢，屈服强度≥235MPa
   相关术语: 抗拉强度、屈服强度、延伸率
   
   【检索上下文】
   (从知识库检索的文档片段)
    ↓
5. Agent 回答
   基于专业词汇定义 + 检索内容生成专业回答
```

### 数据库表结构
```sql
CREATE TABLE vocabulary (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    term VARCHAR(128) NOT NULL,           -- 术语名称
    definition TEXT NOT NULL,             -- 定义
    category VARCHAR(64) NOT NULL,        -- 分类 (steel_grade, process, equipment, etc.)
    synonyms JSON,                        -- 同义词列表
    related_terms JSON,                   -- 相关术语列表
    created_at DATETIME,
    updated_at DATETIME,
    created_by BIGINT,
    INDEX idx_term_category (term, category)
);
```

### API 端点
- `GET /api/admin/vocabulary` - 获取词汇列表（分页）
- `POST /api/admin/vocabulary` - 创建新词汇
- `PUT /api/admin/vocabulary/{id}` - 更新词汇
- `DELETE /api/admin/vocabulary/{id}` - 删除词汇
- `GET /api/admin/vocabulary/search?q=关键词` - 搜索词汇

### 词汇分类 (Category)
| 分类 | 说明 | 示例 |
|-----|------|-----|
| `steel_grade` | 钢种牌号 | Q235, Q345, 304, 316L |
| `steel_type` | 钢材类型 | 碳素钢、不锈钢、合金钢 |
| `alloy_element` | 合金元素 | 碳、硅、锰、铬、镍 |
| `material_property` | 材料性能 | 抗拉强度、屈服强度、延伸率 |
| `process` | 工艺流程 | 炼钢、热轧、冷轧、退火 |
| `equipment` | 设备名称 | 转炉、热轧机、冷轧机 |
| `application` | 应用领域 | 建筑结构、汽车制造、压力容器 |
| `standard` | 标准规范 | GB/T, ASTM, JIS, DIN |

### 使用示例

#### 1. 添加默认词汇库
```bash
# 添加钢铁行业常用词汇（~500个术语）
python scripts/vocabulary_manager.py add-default

# 输出示例：
# ✅ 成功添加词汇: Q235 (钢种牌号)
# ✅ 成功添加词汇: 转炉 (设备)
# ...
# 📊 总计添加: 478 个专业词汇
```

#### 2. 批量导入词汇
CSV 格式 (`vocabulary.csv`):
```csv
term,definition,category,synonyms,related_terms
Q235,碳素结构钢，屈服强度≥235MPa,steel_grade,"碳素钢,结构钢","Q345,抗拉强度,屈服强度"
转炉,炼钢的主要设备，用于将生铁转化为钢,equipment,炼钢炉,"电炉,炼钢,钢水"
```

导入命令:
```bash
python scripts/vocabulary_manager.py import vocabulary.csv
```

#### 3. 查询增强测试
```bash
python scripts/vocabulary_manager.py test-enhance "Q235钢板的抗拉强度是多少？"

# 输出示例：
# 🔍 原始查询: Q235钢板的抗拉强度是多少？
# 📝 识别到专业词汇: ['Q235', '抗拉强度']
# ✨ 增强查询: Q235钢板的抗拉强度是多少？ 碳素结构钢 屈服强度
# 
# === 专业词汇上下文 ===
# 【Q235】
# 定义: 碳素结构钢，屈服强度≥235MPa
# 分类: steel_grade
# 相关术语: Q345, 抗拉强度, 屈服强度
```

#### 4. 通过 API 管理词汇
```python
import requests

# 创建新词汇
response = requests.post("http://localhost:8000/api/admin/vocabulary", json={
    "term": "Q345",
    "definition": "低合金高强度结构钢，屈服强度≥345MPa",
    "category": "steel_grade",
    "synonyms": ["345钢", "低合金钢"],
    "relatedTerms": ["Q235", "Q420", "屈服强度"]
}, headers={"Authorization": "Bearer <admin_token>"})

# 搜索词汇
response = requests.get("http://localhost:8000/api/admin/vocabulary/search?q=Q235")
print(response.json())
```

### 代码集成示例

#### 在自定义 Agent 中使用专业词汇
```python
from src.vocabulary import VocabularyService, QueryEnhancer
from src.api.db import get_db

# 初始化服务
db = next(get_db())
vocab_service = VocabularyService(db)
vocab_service.initialize()  # 加载词汇到内存

# 创建查询增强器
enhancer = QueryEnhancer(vocab_service)

# 增强查询
query = "Q235钢板的抗拉强度是多少？"
enhanced = enhancer.enhance(query, add_synonyms=True, add_related=True)

print(f"原始查询: {enhanced.original_query}")
print(f"增强查询: {enhanced.enhanced_query}")
print(f"识别词汇: {[t['term'] for t in enhanced.identified_terms]}")
print(f"词汇上下文:\n{enhanced.vocabulary_context}")
```

#### 在文本中识别专业词汇
```python
text = "Q235和Q345是常用的碳素结构钢，广泛应用于建筑结构。"
found_terms = vocab_service.find_terms_in_text(text)

for term_info in found_terms:
    vocab = term_info['vocabulary']
    print(f"识别到: {vocab.term} ({vocab.category})")
    print(f"定义: {vocab.definition}")
    print(f"位置: {term_info['position']}")
```

### 配置选项

在 `main.py` 中配置查询增强行为:
```python
# 获取查询增强器
enhancer = get_query_enhancer()

# 增强选项
enhanced = enhancer.enhance(
    query="Q235钢板强度",
    add_synonyms=True,       # 添加同义词
    add_related=True,        # 添加相关术语
    max_related_terms=5      # 最多添加5个相关术语
)
```

### 性能优化
1. **内存缓存**: 词汇库启动时加载到内存，避免重复查询数据库
2. **索引优化**: 术语和同义词建立索引，快速查找
3. **边界检测**: 避免匹配子串（如避免将"Q2"识别为"Q235"的一部分）
4. **去重机制**: 避免重复识别重叠的术语

### 最佳实践
1. ✅ **定期维护词汇库**: 随着业务发展添加新的专业术语
2. ✅ **建立术语关联**: 为每个术语添加同义词和相关术语
3. ✅ **分类管理**: 按照分类组织词汇，便于管理和检索
4. ✅ **版本控制**: 导出词汇库到 CSV，纳入版本管理
5. ✅ **用户反馈**: 根据用户查询日志发现缺失的专业术语
6. ❌ 避免过度扩展查询（导致检索噪音）
7. ❌ 避免添加过于通用的词汇（如"钢"、"铁"）

### 故障排查

#### 问题：专业词汇未被识别
**解决方案**：
1. 检查词汇是否在数据库中：
   ```bash
   python scripts/vocabulary_manager.py search "Q235"
   ```
2. 检查大小写（词汇识别是大小写不敏感的）
3. 检查术语边界（避免子串匹配问题）
4. 刷新词汇缓存：
   ```python
   vocab_service.refresh_cache()
   ```

#### 问题：查询增强后检索结果变差
**原因**: 添加的相关术语引入噪音

**解决方案**：
1. 减少 `max_related_terms` 参数（默认5，可调整为2-3）
2. 检查相关术语的准确性
3. 暂时禁用相关术语扩展：
   ```python
   enhanced = enhancer.enhance(query, add_synonyms=True, add_related=False)
   ```

#### 问题：词汇加载慢
**解决方案**：
1. 词汇库使用单例模式（`@lru_cache`），只加载一次
2. 如果词汇量过大（>10000），考虑分类加载
3. 检查数据库索引是否正常

---

## Intelligent Query Optimization (智能查询优化)

### 功能说明
系统已集成智能意图识别和 Agent 差异化优化，实现：
1. **智能判断是否需要 RAG** - 问候/闲聊直接由 LLM 回答，专业问题才检索知识库
2. **Agent 回答差异化** - 不同 Agent 有独特的回答风格和结构
3. **性能提升** - 简单查询响应速度提升 10-20 倍

### 核心特性

#### 1. 意图识别器 (Intent Classifier)
**自动分类查询类型**：
- **问候语** (greeting) - "你好"、"谢谢"、"再见" → 跳过 RAG
- **闲聊** (chitchat) - "天气怎么样"、"你叫什么名字" → 跳过 RAG
- **知识查询** (knowledge_query) - "是什么"、"如何"、"为什么" → 使用 RAG
- **专业查询** (professional_query) - 包含钢铁术语 → 使用 RAG

**判断逻辑**：
```python
from src.intent_classifier import get_intent_classifier

classifier = get_intent_classifier()
should_use_rag, reason = classifier.should_use_rag("你好")
# 返回: (False, "意图类型=greeting，无需检索")

should_use_rag, reason = classifier.should_use_rag("Q235的抗拉强度是多少？")
# 返回: (True, "意图类型=professional_query，置信度90%（包含2个专业术语）")
```

**支持的专业术语**（钢铁行业）：
- 钢种: Q235, Q345, 304, 316L, 不锈钢, 硅钢, HiB
- 工艺: 炼钢, 轧钢, 热轧, 冷轧, 退火, 转炉, 连铸
- 性能: 抗拉强度, 屈服强度, 延伸率, 硬度, 铁损, 磁感
- 设备: 加热炉, 轧机, 冷却塔, 精轧机
- 市场: 铁矿石, 焦炭, 废钢, 螺纹钢, 价格, 趋势

#### 2. Agent 差异化 Prompt
每个 Agent 有独特的回答风格和结构：

| Agent 类型 | 回答特点 | 结构 |
|-----------|---------|------|
| **通用助手** (general) | 🎯 简洁明了，知识面广 | 核心观点 → 详细解释 → 建议 |
| **工艺专家** (process) | 🏭 工艺优先，参数敏感 | 工艺要点 → 参数控制 → 质量影响 → 优化建议 |
| **设备诊断** (equipment) | 🔧 症状优先，安全第一 | 故障判断 → 检查步骤 → 应急措施 → 维修方案 → 预防 |
| **市场分析师** (market) | 📈 数据说话，趋势预测 | 当前现状 → 影响因素 → 趋势判断 → 决策建议 |
| **质量顾问** (quality) | 🎯 标准至上，持续改进 | 质量标准 → 检测方法 → 不合格原因 → 改进措施 |
| **节能专家** (environment) | 🌱 绿色优先，能效至上 | 环保标准 → 能耗分析 → 减排方案 → 经济效益 |

**示例对比**：
```
问题: "炼钢过程中温度控制有什么注意事项？"

【工艺专家回答】
✅ "炼钢温度应控制在1600-1650℃，分为三个阶段：
   1. 预热期（1200-1400℃）...
   2. 精炼期（1600-1650℃）...
   3. 出钢期（1550-1600℃）..."

【设备诊断回答】
✅ "温度控制不当可能导致设备损坏，建议：
   1. **立即检查**温度传感器是否正常
   2. 检查加热炉耐火材料是否完好
   3. 应急措施：温度超过1700℃立即降温..."

【通用助手回答】
✅ "炼钢温度控制很重要，主要注意：
   1. 保持合适的温度范围
   2. 避免温度波动过大
   3. 定期检查设备..."
```

### 使用方法

#### 1. 增强 Agent Prompt（初次运行或升级）
```bash
# 方式一：通过数据库迁移脚本
python scripts/db_migrate.py enhance-prompts

# 方式二：直接运行增强脚本
python scripts/enhance_agent_prompts.py
```

**输出示例**：
```
✨ 增强 Agent System Prompt...
============================================================
✅ 更新 general Prompt (ID: 1)
   旧长度: 111 → 新长度: 231
✅ 更新 process Prompt (ID: 3)
   旧长度: 113 → 新长度: 374
✅ 更新 equipment Prompt (ID: 5)
   旧长度: 112 → 新长度: 405
============================================================
✨ 成功更新 6 个 Agent Prompt
============================================================
```

#### 2. 测试优化效果
```bash
# 运行综合测试
python scripts/test_optimizations.py

# 测试内容：
# 1. 意图识别准确率（问候、闲聊、专业查询）
# 2. Agent 回答差异性（相同问题不同 Agent 的对比）
```

**测试输出示例**：
```
【测试 1】意图识别 - 智能判断是否需要 RAG
================================================================================

📝 测试查询: 你好 (问候)
   预期: 跳过RAG
   实际: 跳过RAG (意图类型=greeting，无需检索)
   结果: ✅ 正确
   耗时: 0.35s

📝 测试查询: Q235的抗拉强度是多少？ (专业查询)
   预期: 使用RAG
   实际: 使用RAG (意图类型=professional_query，置信度90%)
   结果: ✅ 正确
   耗时: 2.15s

================================================================================
意图识别准确率: 8/8 = 100%
================================================================================

【测试 2】Agent 差异化 - 相同问题不同 Agent 的回答对比
================================================================================

🔍 测试问题: 炼钢过程中温度控制有什么注意事项？
--------------------------------------------------------------------------------

【process Agent】
回答长度: 1245 字符
耗时: 2.35s
前200字: 炼钢温度应控制在1600-1650℃，分为三个阶段：预热期（1200-1400℃）保证炉温均匀，精炼期（1600-1650℃）进行脱碳脱硫，出钢期（1550-1600℃）保证钢水流动性...

【equipment Agent】
回答长度: 1180 字符
耗时: 2.28s
前200字: 根据您提到的温度控制，这涉及设备安全，建议优先检查：1. **温度传感器**：热电偶是否正常，误差应<±5℃；2. **加热设备**：电极或燃烧器是否完好；3. **应急措施**：温度超1700℃立即停止加热...

📊 差异分析:
   平均长度: 1213 字符
   最大差异: 65 字符
   长度变异系数: 5.4%
```

#### 3. API 响应字段
**ChatResponse 新增字段**：
```typescript
{
  "response": "回答内容",
  "reasoning_steps": [...],
  "fallback_mode": false,          // 是否因超时降级
  "intent_skip_rag": false,        // 🆕 是否因意图判断跳过RAG
  "intent_reason": "意图类型=professional_query，置信度90%"  // 🆕 判断理由
}
```

**前端使用示例**：
```typescript
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "你好",
    agent_type: "general"
  })
});

const data = await response.json();

if (data.intent_skip_rag) {
  console.log("快速响应（无需检索）:", data.intent_reason);
  // 显示：💬 快速响应
} else if (data.fallback_mode) {
  console.log("⚠️ 检索超时，已使用通用模式回答");
} else {
  console.log("✅ 基于知识库回答");
}
```

### 性能对比

| 查询类型 | 优化前 | 优化后 | 提升 |
|---------|-------|-------|-----|
| 简单问候 | 25s (RAG超时降级) | 0.3-0.5s | **50-80倍** |
| 闲聊问题 | 25s (RAG超时降级) | 0.4-0.6s | **40-60倍** |
| 专业查询 | 2-3s (正常RAG) | 2-3s | 无变化 |
| 知识查询 | 2-4s (正常RAG) | 2-4s | 无变化 |

### 配置选项

#### 1. 意图识别阈值
```python
# src/intent_classifier.py

classifier = get_intent_classifier()
should_use_rag, reason = classifier.should_use_rag(
    query="你的查询",
    threshold=0.7  # 置信度阈值，默认0.7
)
```

#### 2. 专业术语扩展
```python
# 添加自定义专业术语
classifier = IntentClassifier()
classifier.professional_keywords.extend([
    "自定义术语1",
    "自定义术语2",
])
```

#### 3. RAG 超时时间
```bash
# .env 文件
RAG_TIMEOUT_SECONDS=25  # 默认25秒
```

### 故障排查

#### 问题：意图识别不准确
**现象**：专业问题被误判为闲聊，或闲聊被误判为专业查询

**解决方案**：
1. 检查查询中是否包含专业术语：
   ```python
   python src/intent_classifier.py  # 运行测试
   ```
2. 调整置信度阈值（降低阈值使用更多 RAG）
3. 添加自定义专业术语到 `professional_keywords`

#### 问题：Agent 回答差异不明显
**解决方案**：
1. 确认 Prompt 已更新：
   ```bash
   python scripts/test_agent_prompts.py
   ```
2. 重启后端服务清除缓存：
   ```bash
   python manage.py start backend
   ```
3. 检查 LLM 参数（temperature 应 ≥ 0.7）

#### 问题：简单问候仍然很慢
**解决方案**：
1. 检查后端日志是否显示 "💬 跳过RAG检索"
2. 验证意图分类器正常工作：
   ```python
   from src.intent_classifier import get_intent_classifier
   classifier = get_intent_classifier()
   print(classifier.should_use_rag("你好"))
   # 应输出: (False, "意图类型=greeting，无需检索")
   ```
3. 如仍然慢，检查 LLM API 响应时间

### 最佳实践

1. ✅ **首次部署**：运行 `python scripts/db_migrate.py enhance-prompts` 更新 Prompt
2. ✅ **定期测试**：运行 `python scripts/test_optimizations.py` 验证效果
3. ✅ **监控日志**：观察后端日志中的意图识别信息
   ```
   💬 跳过RAG检索: 意图类型=greeting，无需检索
   🔍 使用RAG检索: 意图类型=professional_query，置信度90%
   ```
4. ✅ **用户反馈**：收集用户对 Agent 回答差异的反馈，持续优化 Prompt
5. ❌ 避免过度依赖意图识别（保守策略：不确定时使用 RAG）
6. ❌ 避免频繁修改 Prompt（影响回答稳定性）

### 技术实现

**工作流程**：
```
用户查询
   ↓
意图识别器 (IntentClassifier)
   ↓
├── 问候/闲聊 → 直接LLM（0.3-0.5s）
└── 专业/知识查询 → RAG检索 + LLM（2-4s）
   ↓
根据 agent_type 加载专属 Prompt
   ↓
生成差异化回答
```

**核心文件**：
- `src/intent_classifier.py` - 意图识别器
- `scripts/enhance_agent_prompts.py` - Prompt 增强脚本
- `scripts/test_optimizations.py` - 综合测试脚本
- `main.py` (line 685-702) - 意图判断集成
- `scripts/db_migrate.py` (enhance-prompts 命令) - 数据库迁移

---

## Development Standards

1. Setup: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` (Python 3.10+)
2. Start: `python manage.py start all` or `python manage.py start backend` (FastAPI on port 8000)
3. Tests: all `pytest -q`; single file `pytest tests/integration.py`; single test `pytest tests/integration.py::test_name`; keyword `pytest -k search`.
4. Async: use `pytest-asyncio`; mark coroutines with `@pytest.mark.asyncio`.
5. Imports order: stdlib, third-party, local (no wildcards); blank line between groups.
6. Types: annotate all public functions; prefer `list[str]` / `str | None`; no implicit Any.
7. Docstrings: Google style (Args, Returns, Raises) for public APIs; brief summary line first.
8. Naming: modules snake_case; classes PascalCase; functions/vars snake_case; constants UPPER_SNAKE; internal helpers `_prefixed`.
9. Errors: never silent; log then raise domain or ValueError; no bare `except`; preserve context (`raise ... from e`).
10. Logging: use `config.logging_config.setup_logging`; levels => INFO workflow, DEBUG internals, WARNING recoverable, ERROR failjsonure, CRITICAL outage; no `print` in src.
11. Data/paths: use `pathlib.Path`; directories created lazily in `get_settings()`.
12. Vector/RAG metadata keys: `file, chunk_id, hash, preview, score, rank`; keep embeddings float32; batch for performance.
13. **Vector Store**: 已升级为 `VectorStoreFast` 自动优化版本（<10k向量用Flat精确检索，≥10k自动升级IVF+PQ近似检索，5-10倍加速）
14. Tool/Agent: extend `Tool`, register via `BaseAgent.add_tool`; duplicate names raise ValueError; reasoning path via `ReasoningEngine`.
15. Formatting: recommend `ruff format` or `black`; line length ≤ 100; strip unused imports (ruff).
16. Lint (optional): `ruff check .`; type check (if added) `mypy src tests`.
17. Commits: Conventional (`feat:`, `fix:`, `refactor:`); PR must pass `pytest -q`; keep diffs focused.
18. Config: only through `get_settings()`; no hardcoded secrets; `.env` ignored; add `.env.example` when new vars.
19. Performance: batch embeddings; avoid redundant FAISS loads; consider caching frequent queries.
20. Security: validate user input before search/LLM; never log secrets; plan filters (`tenant_id`, `visibility`).
21. **RAG Timeout & Fallback**: RAG检索+LLM调用有25秒超时（可配置`RAG_TIMEOUT_SECONDS`），超时自动降级为直接使用LLM（不带RAG上下文），确保用户始终能获得响应。前端总超时60秒。
22. **Documentation Management**: 
    - ✅ ONLY update AGENTS.md for project documentation, standards, and guides
    - ❌ NEVER create new documentation files (README.md, GUIDE.md, STANDARDS.md, FIX.md, etc.)
    - ❌ NEVER create temporary markdown files for fixes or features
    - ✅ Add sections to AGENTS.md instead: append to existing sections or create new ones
    - ✅ Keep AGENTS.md as single source of truth for all project information

---

## AI-Assisted Development Standards

### Project Initialization & Scaffolding
1. **Use Official CLI Tools**: Always use framework-specific CLI for project setup
   - ✅ `npx create-next-app@latest` for Next.js projects
   - ✅ `npm create vite@latest` for Vite projects
   - ✅ `npx create-react-app` for CRA projects
   - ❌ Never manually create boilerplate files when CLI exists
   - **Rationale**: CLI ensures correct configuration, dependencies, and structure

2. **Scaffold with Templates**: Leverage official templates when available
   - ✅ `create-next-app --typescript --tailwind --app`
   - ✅ `create-vite --template react-ts`
   - **Benefit**: Reduces initial setup errors, follows best practices

### Code Organization & Reusability

3. **DRY Principle (Don't Repeat Yourself)**
   - ✅ Extract repeated UI patterns into reusable components
   - ✅ Create custom hooks for shared logic
   - ✅ Use utility functions for common operations
   - ❌ Never copy-paste code blocks more than twice
   - **Rule**: If code appears 3+ times, refactor into shared module

4. **Component Composition**
   ```tsx
   // ✅ Good: Composable, reusable
   <Button variant="primary" size="lg" icon={<SaveIcon />}>
     Save Changes
   </Button>

   // ❌ Bad: Non-reusable, hardcoded
   <button className="bg-blue-500 text-white px-4 py-2">
     Save Changes
   </button>
   ```

5. **Atomic Design Hierarchy**
   - `components/ui/` - Atoms (Button, Input, Card)
     - **For shadcn/ui projects**: Use MCP tools to discover and install UI components
     - **MCP Query First**: Before creating custom components, search shadcn registry
   - `components/shared/` - Molecules (SearchBar, UserAvatar)
   - `components/layout/` - Organisms (Header, Sidebar)
   - `app/*/` - Templates & Pages

5a. **shadcn/ui Component Discovery Workflow**
   ```typescript
   // ❌ Don't manually create components that may exist in shadcn/ui
   // ✅ Do: Query MCP tools first
   
   // Step 1: Search for components
   // Use: mcp_shadcn_search_items_in_registries({ query: "button" })
   
   // Step 2: View component details and source
   // Use: mcp_shadcn_view_items_in_registries({ items: ["@shadcn/button"] })
   
   // Step 3: Check usage examples
   // Use: mcp_shadcn_get_item_examples_from_registries({ query: "button demo" })
   
   // Step 4: Get install command
   // Use: mcp_shadcn_get_add_command_for_items({ items: ["@shadcn/button"] })
   ```

### TypeScript Best Practices

6. **Type Safety First**
   - ✅ Define interfaces/types for all data structures
   - ✅ Use strict mode in `tsconfig.json`
   - ✅ Avoid `any` - use `unknown` or generics instead
   - ❌ Never disable TypeScript errors with `@ts-ignore` (use `@ts-expect-error` with explanation)

7. **Shared Type Definitions**
   ```typescript
   // lib/types/api.ts - Centralized API types
   export interface User {
     id: string;
     username: string;
     role: UserRole;
   }

   // ✅ Import from single source of truth
   import type { User } from '@/lib/types/api';
   ```

### State Management

8. **Collocate State Close to Usage**
   - ✅ Use local state (`useState`) when possible
   - ✅ Lift to context/store only when shared across 3+ components
   - ❌ Don't put everything in global store

9. **Zustand Store Organization**
   ```typescript
   // ✅ Good: Sliced stores by domain
   store/
   ├── authStore.ts      // Authentication state
   ├── chatStore.ts      // Chat messages & sessions
   └── uiStore.ts        // UI preferences

   // ❌ Bad: Monolithic store
   store/index.ts        // Everything in one file
   ```

### API & Data Fetching

10. **Centralized API Clients**
    ```typescript
    // ✅ Good: Single Axios instance with interceptors
    // lib/api/client.ts
    const apiClient = axios.create({ baseURL: API_URL });
    apiClient.interceptors.request.use(addAuthToken);

    // ❌ Bad: Scattered fetch calls throughout components
    ```

11. **Use TanStack Query for Server State**
    - ✅ Leverage caching, refetching, and invalidation
    - ✅ Separate server state from client state
    - ❌ Don't store API responses in Zustand/Redux

### Styling & UI

12. **Consistent Styling Approach**
    - ✅ Use **shadcn/ui** components as primary UI library
    - ✅ Built on Radix UI primitives with Tailwind CSS
    - ✅ CSS variables for theming (defined in `globals.css`)
    - ✅ OKLCH color space for better color perception
    - ❌ Avoid inline styles except for dynamic values
    - **⚡ shadcn/ui Workflow**:
      1. Search components using `mcp_shadcn_search_items_in_registries`
      2. View component details with `mcp_shadcn_view_items_in_registries`
      3. Check usage examples via `mcp_shadcn_get_item_examples_from_registries`
      4. Get install command from `mcp_shadcn_get_add_command_for_items`
      5. Never manually copy component code - always use MCP tools first

13. **Design System & Theming**
    - ✅ All colors defined as CSS variables in `app/globals.css`
    - ✅ Use semantic color tokens: `--primary`, `--secondary`, `--destructive`, `--muted`, etc.
    - ✅ Automatic dark/light mode support via CSS variables
    - ✅ Never use hardcoded color values or Tailwind color classes (e.g., `slate-500`)
    - ✅ Always reference colors via `var(--*)` or semantic Tailwind classes (e.g., `bg-primary`)
    - ❌ Don't define custom color values - extend existing CSS variables if needed

### Performance Optimization

14. **Code Splitting**
    - ✅ Use `React.lazy()` and `Suspense` for route-based splitting
    - ✅ Dynamic imports for heavy components (charts, editors)
    - ✅ Next.js `dynamic()` for SSR-safe lazy loading

15. **Image Optimization**
    - ✅ Always use Next.js `<Image>` component
    - ✅ Specify width/height to prevent layout shift
    - ✅ Use `priority` for above-the-fold images

16. **Memoization**
    ```tsx
    // ✅ Good: Memoize expensive computations
    const processedData = useMemo(() => 
      heavyCalculation(rawData), [rawData]
    );

    // ✅ Good: Prevent unnecessary re-renders
    const MemoizedChart = memo(ExpensiveChart);
    ```

### Error Handling

17. **Graceful Error Boundaries**
    ```tsx
    // ✅ Implement error boundaries for route segments
    // app/error.tsx (Next.js App Router)
    export default function Error({ error, reset }) {
      return <ErrorFallback error={error} onReset={reset} />;
    }
    ```

18. **User-Friendly Error Messages**
    - ✅ Show actionable error messages with recovery options
    - ✅ Log technical details, display simple messages to users
    - ❌ Never expose stack traces or API errors directly

### Testing Strategy

19. **Test Pyramid**
    - Unit Tests: Pure functions, utilities (70%)
    - Integration Tests: API clients, stores (20%)
    - E2E Tests: Critical user flows (10%)

20. **Test File Colocation**
    ```
    components/
    ├── Button/
    │   ├── Button.tsx
    │   ├── Button.test.tsx    ✅ Colocated
    │   └── Button.stories.tsx ✅ Storybook
    ```

### Security Best Practices

21. **Authentication & Authorization**
    - ✅ Store JWT in httpOnly cookies (not localStorage)
    - ✅ Implement CSRF protection for mutations
    - ✅ Validate permissions on both frontend and backend

22. **Input Validation**
    - ✅ Use Zod for schema validation
    - ✅ Sanitize user input before rendering
    - ✅ Validate file uploads (type, size, content)

### Documentation

23. **Self-Documenting Code**
    ```typescript
    // ✅ Good: Clear naming, JSDoc for complex logic
    /**
     * Calculates steel production cost based on raw material prices
     * @param materials - Raw material quantities and prices
     * @param energyCost - Current energy cost per kWh
     * @returns Total production cost in USD
     */
    function calculateProductionCost(
      materials: MaterialCost[],
      energyCost: number
    ): number {
      // Implementation...
    }
    ```

24. **Component Documentation**
    - ✅ Add prop descriptions for complex components
    - ✅ Include usage examples in Storybook or comments
    - ✅ Document edge cases and limitations

### Git & Version Control

25. **Conventional Commits**
    ```bash
    # ✅ Good commit messages
    feat(chat): add streaming AI response support
    fix(upload): resolve file size validation error
    refactor(api): extract auth logic to middleware
    docs(readme): update installation instructions

    # ❌ Bad commit messages
    "fix bug"
    "update"
    "wip"
    ```

26. **Atomic Commits**
    - ✅ One logical change per commit
    - ✅ All tests pass before committing
    - ❌ Don't commit commented-out code or console.logs

### AI Collaboration Guidelines

27. **Provide Context to AI**
    - ✅ Share relevant files, error messages, and goals
    - ✅ Specify framework versions and environment
    - ✅ Describe expected behavior vs actual behavior

28. **Review AI-Generated Code**
    - ✅ Always review suggested code before applying
    - ✅ Test AI-generated functions with edge cases
    - ✅ Verify security implications (especially auth/validation)
    - ❌ Never blindly accept code that you don't understand

29. **Iterative Refinement**
    - ✅ Start with high-level architecture questions
    - ✅ Drill down into specific implementation details
    - ✅ Request alternatives when unsure about approach

30. **Development Server Management**
    - ❌ 不要主动运行开发服务器或打开预览界面
    - ✅ Only start servers when explicitly requested by user
    - ✅ Confirm before launching any long-running processes

### Accessibility (a11y)

31. **WCAG Compliance**
    - ✅ Use semantic HTML (`<button>`, `<nav>`, `<main>`)
    - ✅ Provide alt text for images
    - ✅ Ensure keyboard navigation works
    - ✅ Maintain color contrast ratios (WCAG AA: 4.5:1)

32. **ARIA Labels**
    ```tsx
    // ✅ Good: Accessible button
    <button aria-label="Close dialog" onClick={onClose}>
      <X />
    </button>

    // ❌ Bad: Icon-only button without label
    <button onClick={onClose}>
      <X />
    </button>
    ```

### Environment Configuration

33. **Environment Variables**
    - ✅ Use `.env.local` for secrets (gitignored)
    - ✅ Provide `.env.example` with dummy values
    - ✅ Prefix public vars with `NEXT_PUBLIC_`
    - ❌ Never commit real API keys or credentials

34. **Type-Safe Environment**
    ```typescript
    // lib/env.ts
    import { z } from 'zod';

    const envSchema = z.object({
      NEXT_PUBLIC_API_URL: z.string().url(),
      DATABASE_URL: z.string(),
    });

    export const env = envSchema.parse(process.env);
    ```

### Deployment & CI/CD

35. **Pre-deployment Checks**
    ```json
    // package.json scripts
    {
      "scripts": {
        "build": "next build",
        "lint": "eslint . --ext .ts,.tsx",
        "type-check": "tsc --noEmit",
        "test": "jest",
        "precommit": "lint-staged",
        "prebuild": "npm run lint && npm run type-check"
      }
    }
    ```

36. **Continuous Integration**
    - ✅ Run tests on every PR
    - ✅ Enforce code coverage thresholds
    - ✅ Block merge if build fails



## Frontend Architecture Design (Steel Industry AI Decision Hub)

### Product Positioning
- **Domain**: Vertical AI decision hub for steel industry
- **Target Users**: Technicians, production managers, procurement staff, environmental experts
- **Core Value**: From "information retrieval" to "decision support"

### Tech Stack

#### Core Framework
- **Next.js 14+** (App Router) - React full-stack framework with SSR/SSG support
- **TypeScript** - Type safety
- **React 18+** - UI component foundation

#### UI Component Library
- **shadcn/ui** - Modern headless UI component library
  - Built on Radix UI primitives with full accessibility support
  - Customizable components (copy to your project, you own the code)
  - Tailwind CSS integration with CSS variables theming
  - OKLCH color space for better color perception
  - Automatic dark/light mode support
  - **🔧 MCP Tool Integration**: Use MCP shadcn tools for component management
    - `mcp_shadcn_list_items_in_registries` - List all available components
    - `mcp_shadcn_search_items_in_registries` - Search for specific components
    - `mcp_shadcn_view_items_in_registries` - View component source code
    - `mcp_shadcn_get_item_examples_from_registries` - Get usage examples
    - `mcp_shadcn_get_add_command_for_items` - Get CLI command to add components
  - **Best Practice**: Always query MCP tools before manually adding components

#### State Management
- **Zustand** - Lightweight state management
- **TanStack Query (React Query)** - Server state management and caching

#### Data Visualization
- **Apache ECharts** - Industry data charts (price trends, equipment monitoring)
- **D3.js** - Process flowcharts and knowledge graph visualization
- **Cytoscape.js** - Knowledge graph network display

#### Real-time Communication
- **Server-Sent Events (SSE)** - Streaming AI responses
- **Socket.io Client** (optional) - WebSocket real-time chat

#### Utility Libraries
- **Axios** - HTTP request wrapper
- **React Hook Form + Zod** - Form management and validation
- **date-fns** - Date manipulation
- **react-markdown** - Markdown rendering (AI responses)
- **framer-motion** - Animation effects

#### Internationalization (i18n)
- **Default Language**: Chinese (zh-CN) - Primary language for steel industry users in China
- **Secondary Language**: English (en-US) - For international collaboration and documentation
- **i18n Implementation**: Custom translation hook (`useTranslation`) with locale files
- **Language Switching**: Stored in `uiStore.language` state, persisted in localStorage
- **Translation Scope**:
  - UI labels, buttons, navigation
  - Form validation messages
  - System notifications and alerts
  - AI response interface labels
  - Technical terminology (bilingual support for steel industry terms)
- **Content Strategy**:
  - User-uploaded documents: Support both Chinese and English analysis
  - AI responses: Match user's selected language preference
  - Knowledge base: Multilingual document indexing with language detection
- **Translation Management**:
  ```typescript
  // lib/i18n/locales/zh-CN.ts
  export const zhCN = {
    common: { login: '登录', logout: '退出', submit: '提交', cancel: '取消' },
    auth: { username: '用户名', password: '密码', loginTitle: '钢铁行业 AI 决策中心' },
  };
  // lib/i18n/locales/en-US.ts
  export const enUS = {
    common: { login: 'Login', logout: 'Logout', submit: 'Submit', cancel: 'Cancel' },
    auth: { username: 'Username', password: 'Password', loginTitle: 'Steel Industry AI Hub' },
  };
  ```
- **Best Practices**:
  - ✅ All user-facing text must be translatable (no hardcoded strings)
  - ✅ Use semantic keys: `auth.loginButton` not `button1`
  - ✅ Support Chinese technical terminology with English equivalents
  - ✅ Date/number formatting according to locale (date-fns with locale)
  - ❌ Never mix languages in the same UI component

### Directory Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/            # Authentication page group
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/       # Main app page group (requires auth)
│   │   │   ├── layout.tsx     # Dashboard layout
│   │   │   ├── page.tsx       # Home/Overview
│   │   │   ├── chat/          # Intelligent Q&A
│   │   │   ├── equipment/     # Equipment management
│   │   │   ├── market/        # Market analysis
│   │   │   ├── knowledge/     # Knowledge base management
│   │   │   ├── workflow/      # Process workflow
│   │   │   └── admin/         # Admin panel
│   │   ├── api/               # API routes (optional, Next.js middleware)
│   │   ├── layout.tsx         # Global layout
│   │   └── page.tsx           # Landing page
│   ├── components/            # React components
│   │   ├── ui/                # Base UI components (buttons, cards, etc.)
│   │   ├── layout/            # Layout components (Header, Sidebar, etc.)
│   │   ├── chat/              # Chat-related components
│   │   ├── equipment/         # Equipment-related components
│   │   ├── market/            # Market analysis components
│   │   ├── knowledge/         # Knowledge graph components
│   │   └── shared/            # Shared components
│   ├── lib/                   # Utility library
│   │   ├── api/               # API client wrappers
│   │   │   ├── client.ts      # Axios instance
│   │   │   ├── auth.ts        # Authentication API
│   │   │   ├── chat.ts        # Chat API
│   │   │   ├── upload.ts      # File upload API
│   │   │   └── admin.ts       # Admin API
│   │   ├── hooks/             # Custom hooks
│   │   ├── utils/             # Utility functions
│   │   ├── constants/         # Constants
│   │   └── types/             # TypeScript type definitions
│   ├── store/                 # Zustand state management
│   │   ├── authStore.ts       # Authentication state
│   │   ├── chatStore.ts       # Chat state
│   │   └── uiStore.ts         # UI state
│   ├── styles/                # Style files
│   │   └── globals.css
│   └── middleware.ts          # Next.js middleware (auth guard)
├── public/                    # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.ts
```

### Core Feature Modules

> **Note**: Features support both **production mode** (with real data integration) and **demo mode** (with simulated/sample data for testing).

#### 1. Role-based Permission System
- **Role Definitions**: ADMIN, PRODUCTION, MANAGER, PURCHASER, ENV_EXPERT, TECHNICIAN
- **Permission Control**: canUpload, canChat, canViewMarket, canManageEquipment, canAccessAdmin
- ✅ **Agent-type Specific Prompts**: 每个 Agent 类型自动加载专属 system_prompt（已实现）
  - **工作原理**: `/api/chat` 端点根据 `agent_type` 参数从数据库加载对应 Prompt
  - **支持的 Agent 类型**: `general`, `process`, `equipment`, `market`, `quality`, `environment`
  - **数据库表**: `agent` 表存储 Agent 定义，`system_prompt` 表存储 Prompt 内容
  - **缓存机制**: Prompt 加载后缓存在内存，提升响应速度
  - **前端使用**:
    ```typescript
    // 发送聊天请求时指定 agent_type
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: '炼钢过程中如何控制温度？',
        agent_type: 'process',  // 指定使用工艺专家 Agent
        session_id: 'user_session_123'
      })
    });
    ```
  - **测试验证**: 运行 `python scripts/test_agent_prompts.py` 查看所有 Agent 和 Prompt
  - **API 测试**: 运行 `python scripts/test_chat_api.py --comprehensive` 验证功能
- 🆕 **Smart Role Switching**: AI automatically adjusts response depth and terminology based on detected user expertise
- 🆕 **Collaboration Mode**: Multi-role team chat rooms for cross-functional decision-making
- 🆕 **Conversation Context Sharing**: Share chat sessions with annotations between team members

#### 2. Steel Process Intelligent Q&A
- 💬 Streaming AI responses (typewriter effect)
- 📎 File upload as context (PDF, DOCX, images of equipment/diagrams)
- 🔍 Display retrieved document snippets with source attribution
- 🧠 Visualize reasoning steps (show Agent's thought process)
- 🏷️ Role-based preset prompts
- 📌 Conversation history management
- 🆕 **Multi-modal Input**: Support image upload (equipment photos, process diagrams) for visual Q&A
- 🆕 **Smart Follow-up Questions**: AI proactively suggests 3-5 related questions based on context
- 🆕 **Answer Confidence Score**: Display retrieval relevance score and reasoning confidence
- 🆕 **Comparative Analysis**: "Compare A vs B" - Agent analyzes multiple solutions side-by-side
- 🆕 **Solution Templates**: AI generates actionable checklists/step-by-step guides from knowledge base
- 🆕 **Citation Tracking**: Trace every claim back to source documents with snippets
- 🆕 **Question Refinement**: Agent helps rephrase vague questions for better results

#### 3. Intelligent Equipment Maintenance Assistant
- 📋 Equipment knowledge base (manuals, fault logs, maintenance guides)
- 🔧 Conversational fault diagnosis based on symptoms
- 📖 Retrieve relevant troubleshooting procedures from documents
- 💡 Multi-step reasoning for complex equipment issues
- 🆕 **Symptom-to-Solution Mapping**: Agent asks clarifying questions to narrow down fault causes
- 🆕 **Maintenance Procedure Generator**: Auto-generate step-by-step repair guides from manuals
- 🆕 **Historical Case Retrieval**: "Similar issues in the past" based on RAG search
- 🆕 **Safety Protocol Advisor**: Auto-extract and highlight safety warnings from manuals
- 🆕 **Parts Cross-reference**: Agent helps find alternative part numbers across different suppliers
- 🆕 **Diagnostic Decision Tree**: Interactive fault diagnosis with yes/no questions

#### 4. Market Intelligence & Analysis Assistant
- 📰 Industry news and report aggregation (uploaded documents)
- 📊 Document-based trend analysis (AI summarizes price reports, market analyses)
- 🤖 AI-powered insight extraction from market reports
- 🆕 **Multi-document Synthesis**: Agent combines insights from multiple reports into unified analysis
- 🆕 **Trend Narrative Generation**: AI writes executive summaries from raw data/reports
- 🆕 **Competitive Intelligence Extraction**: Auto-extract competitor info from news/reports
- 🆕 **Custom Alert Builder**: Define keywords/topics, Agent monitors new uploads and notifies
- 🆕 **What-If Scenario Analysis**: "What if iron ore price increases 20%?" - Agent reasons through implications
- 🆕 **Report Comparison Tool**: Side-by-side comparison of different analyst reports with discrepancy highlights

#### 5. Knowledge Base Management
- 📁 File upload and management (PDF, DOCX, TXT, Markdown, code files)
- 🔍 Full-text semantic search across all documents
- 🕸️ Knowledge graph visualization (entity extraction and relationship mapping)
- 📝 Document preview and metadata editing
- 🏷️ AI-powered auto-tagging and categorization
- 🆕 **Auto-tagging & Categorization**: AI automatically tags documents by content (equipment type, process stage, etc.)
- 🆕 **Version Control**: Track document uploads with diff visualization for text files
- 🆕 **Smart Recommendations**: "Documents similar to this" based on embedding similarity
- 🆕 **Knowledge Gap Detection**: AI identifies missing documentation based on frequent unanswered queries
- 🆕 **Multi-language Support**: Auto-translate document snippets between Chinese/English during retrieval
- 🆕 **Collaborative Annotation**: Team members can highlight and comment on documents
- 🆕 **Document Quality Score**: Rate document usefulness based on retrieval frequency and user feedback
- 🆕 **Intelligent Chunking Preview**: Show how documents are split into chunks with overlap visualization
- 🆕 **Entity Extraction Dashboard**: Auto-extract equipment names, process parameters, standards from documents

#### 6. Process Workflow & Quality Intelligence

**📊 Production Mode (with real data)**:
- 🏭 **Real-time Process Monitoring**: Live data overlay on flowchart (temperature, pressure, flow rates)
- 📊 **Quality Prediction Dashboard**: Predict product quality based on current process parameters
- ⚡ **Bottleneck Detection**: AI identifies process bottlenecks from production data
- 📈 **Parameter Optimization**: ML suggests optimal parameter ranges for quality/efficiency
- 🎯 **Yield Analysis**: Track and analyze production yield with defect categorization
- 🔔 **Process Deviation Alerts**: Real-time alerts when parameters drift from optimal ranges

**🎭 Demo Mode (without real data)**:
- 📋 Process SOP document repository
- 🔄 **Static Flowchart**: Interactive steel production flowchart with knowledge linking
- 📊 **Sample Process Data**: Historical process runs for case study analysis
- 🎲 **Simulated Scenarios**: Pre-configured parameter sets showing good/bad outcomes

**🤖 Agent Capabilities (both modes)**:
- 🎯 Parameter reasoning: "Why does temperature affect quality?" - Agent explains from knowledge base and data
- 🆕 **SOP Query Interface**: Natural language queries like "How to handle furnace overheating?"
- 🆕 **Process Parameter Explainer**: Agent explains correlations between parameters using documents + data patterns
- 🆕 **Best Practice Extraction**: AI extracts best practices from successful production runs in knowledge base
- 🆕 **Workflow Comparison**: Compare different process variants documented in knowledge base
- 🆕 **Root Cause Analysis Assistant**: Guide users through 5-Whys analysis with knowledge base + data support
- 🆕 **Standard Compliance Checker**: Agent cross-references processes with uploaded regulatory documents
- 🆕 **Automated SOP Summarization**: Generate concise summaries of lengthy procedures
- 🆕 **Quality Issue Diagnosis**: Agent analyzes quality problems by correlating parameters with defect patterns
- 🆕 **Energy Efficiency Advisor**: Identify energy-intensive stages and suggest optimizations

#### 7. Environment Monitoring & Energy Management
- 🌱 **Real-time Environmental Metrics**: Monitor CO₂ emissions, energy consumption, water usage, waste recycling rate
- ⚡ **Energy Consumption Tracking**: Track energy usage by equipment and production stage
- 💧 **Water Resource Management**: Monitor water consumption and recycling efficiency
- ♻️ **Waste Management**: Track waste recycling rate and disposal compliance
- 📊 **Emission Monitoring**: Real-time monitoring of air quality parameters (smoke, dust, COD, noise)
- ✅ **Compliance Checking**: Track environmental permits, certifications, and regulatory compliance status
- 🎯 **AI-powered Optimization Suggestions**: Intelligent recommendations for energy saving and emission reduction
- 📈 **Trend Analysis**: Historical trends and comparative analysis of environmental metrics
- 🔔 **Alert System**: Automatic alerts when parameters exceed regulatory thresholds
- 📋 **Compliance Reports**: Auto-generate environmental reports for regulatory submissions

**🎭 Demo Mode (current implementation)**:
- 📊 **Simulated Metrics**: Display realistic environmental data for demonstration
- 🎯 **Optimization Suggestions**: AI-generated energy-saving and emission reduction recommendations
- ✅ **Compliance Dashboard**: View environmental permits and certification status
- 📈 **Performance Cards**: Energy consumption, CO₂ emissions, water usage, recycling rate with trend indicators

**🔮 Future Enhancements**:
- 🔌 **Real-time Data Integration**: Connect to environmental monitoring equipment and sensors
- 📊 **Advanced Analytics**: Predictive modeling for emissions and energy consumption trends
- 🌍 **Carbon Footprint Tracking**: Comprehensive carbon accounting and offset management
- 📱 **Mobile Alerts**: Real-time push notifications for environmental threshold breaches
- 🤖 **AI Optimization Engine**: Machine learning-based recommendations for energy efficiency
- 📈 **Benchmarking**: Compare environmental performance against industry standards

**👥 Role-based Access**:
- **Admin**: Full access to all features, system configuration, data export
- **Manager**: View metrics, optimization suggestions, compliance status, energy analysis
- **Technician**: Read-only access (not available)

**🔗 Agent Integration**:
- 💬 **Environment Expert Agent**: Dedicated AI assistant for environmental and energy optimization queries
- 🎯 **Query Examples**:
  - "How can we reduce energy consumption in our heating furnaces?"
  - "What are the latest emission standards for steel production?"
  - "Analyze our water recycling efficiency trends"
  - "Generate a monthly environmental compliance report"

#### 8. Admin Panel
- 👥 User management (CRUD)
- 🔐 Permission configuration
- 📊 System usage statistics (chat volume, upload frequency, top queries)
- 🗂️ Data management (vector store, document library)
- ⚙️ Model configuration (embedding model, LLM settings)
- 🆕 **Query Analytics Dashboard**: Track most common questions, failed queries, response quality
- 🆕 **Document Performance Metrics**: Which documents are most/least retrieved
- 🆕 **RAG Performance Monitor**: Track retrieval accuracy, average response time, token usage
- 🆕 **Prompt Template Manager**: Create and test different system prompts for each role
- 🆕 **A/B Testing Framework**: Test different retrieval strategies or prompt variations
- 🆕 **Feedback Loop**: Collect user ratings on AI responses (👍👎) to improve prompts
- 🆕 **Knowledge Base Health Check**: Identify outdated documents, low-quality chunks, orphaned files
- 🆕 **Semantic Search Debugger**: Visualize embedding similarity scores for troubleshooting

### Backend Integration Design

#### API Client
- Axios instance configuration
- Automatic JWT token injection
- Unified error handling
- Request/response interceptors

#### Key API Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/chat` - Send chat message
- `POST /api/upload` - File upload (multipart/form-data, field: `file`, max 50MB)
  - Supported formats: PDF, DOC, DOCX, TXT, MD, CSV, JSON, XML
  - Auto-indexes into vector store after upload
  - Returns: `{success, message, fileId, fileName, fileSize, contentType, chunks}`
- `GET /api/admin/users` - Get user list
- `PUT /api/admin/users/:id` - Update user
- `GET /api/admin/files` - Get file list (with pagination & search)
- `DELETE /api/admin/files/{file_name}` - Delete single file
- `POST /api/admin/files/batch-delete` - Batch delete files (body: `{"fileNames": ["file1.pdf", "file2.txt"]}`)

#### Streaming Response Handling
- Receive AI streaming output via SSE or WebSocket
- Typewriter effect display
- Support interruption of generation

#### RAG Timeout & Fallback Strategy
**问题**: RAG检索或LLM调用可能因网络、模型响应慢等原因导致超时（30秒前端超时）

**解决方案**: 智能降级机制
- ⏱️ **后端超时**: 25秒（可通过`RAG_TIMEOUT_SECONDS`配置）
- 🔄 **降级策略**: 超时时自动跳过RAG检索，直接使用原生LLM回答
- 📊 **前端超时**: 60秒（给降级LLM留35秒余量）
- 🏷️ **降级标志**: 响应中包含`fallback_mode: true`，前端可显示提示

**配置方法**:
```bash
# .env文件
RAG_TIMEOUT_SECONDS=25  # 默认25秒
```

**工作流程**:
1. 用户发送消息 → 后端开始RAG检索
2. 如果25秒内完成 → 返回带上下文的答案（`fallback_mode: false`）
3. 如果超过25秒 → 自动降级，跳过RAG，直接用LLM（`fallback_mode: true`）
4. 前端收到响应后，如果`fallback_mode: true`可显示："⚠️ 检索超时，已使用通用模式回答"

**优势**:
- ✅ 确保用户始终能获得响应（不会因为RAG慢导致完全失败）
- ✅ 降级后仍有LLM的推理能力（只是缺少知识库上下文）
- ✅ 透明化：前端可知道是否使用了降级模式

### UI/UX Design

#### Design Style
- **Theme System**: 
  - Dark/light mode toggle via CSS variables
  - OKLCH color space for consistent colors across themes
  - Semantic color tokens: `primary`, `secondary`, `destructive`, `muted`, `accent`
  - All colors defined in `app/globals.css` using CSS variables
- **Color Usage**:
  - ✅ Always use semantic tokens: `bg-primary`, `text-muted-foreground`, etc.
  - ✅ Use `var(--primary)` when direct CSS variable access is needed
  - ❌ Never hardcode color values or use Tailwind color classes like `blue-500`

#### Responsive Layout
- Desktop (≥1280px): Three-column layout
- Tablet (768-1279px): Two-column layout
- Mobile (<768px): Single column + bottom navigation

#### Key Interactions
- Skeleton screen loading
- Toast notifications
- Keyboard shortcuts (Ctrl+K for search)
- First-time user onboarding

### Performance Optimization
1. Code splitting (Next.js dynamic imports)
2. Image optimization (Next.js Image component)
3. TanStack Query caching
4. Virtual scrolling (react-window)
5. Debouncing/throttling

### Development Roadmap
- **Phase 1**: Foundation setup (auth, layout)
- **Phase 2**: Core features (Q&A, knowledge base)
- **Phase 3**: Data visualization (market analysis, workflows)
- **Phase 4**: Optimization and testing

### Data Integration Architecture

#### Production Data Connectors (Optional)
```typescript
// lib/connectors/productionData.ts
interface DataConnector {
  type: 'equipment' | 'market' | 'process';
  isConnected: boolean;
  fetchRealTimeData: () => Promise<any>;
  fallbackToDemo: () => DemoData;
}
```

**Supported Data Sources**:
1. **Equipment Sensors**: OPC UA, MQTT, Modbus protocols
2. **Market Data APIs**: Bloomberg, Refinitiv, custom feeds
3. **MES/ERP Systems**: SAP, Oracle, custom databases via REST API
4. **Quality Systems**: LIMS, QMS data exports

**Demo Mode Features**:
- 🎬 **Scenario Library**: Pre-loaded realistic scenarios for each feature
- 📊 **Sample Datasets**: Historical data (anonymized) for visualization
- 🔄 **Data Generator**: Synthetic data generator for continuous simulation
- 🎭 **Interactive Playback**: Step through historical events in demo mode

### Competitive Advantages
1. **Dual-mode Operation**: Seamlessly works with or without production data integration
2. **Industry-specific depth**: Dedicated steel domain embedding model, 30% improvement in technical terminology understanding
3. ✅ **Agent-type based prompts**: 已实现 - 每个 Agent 类型（general/process/equipment/market/quality/environment）自动加载数据库中的专属 system_prompt
4. **Knowledge graph**: Process parameter correlation reasoning
5. **Real-time + Historical**: Combines live data analysis with document-based knowledge
6. **Graceful Degradation**: Full functionality in demo mode for testing and training
7. **Incremental Deployment**: Start with documents, add data sources progressively

---

## Knowledge Base File Upload

### 功能说明
知识库页面提供拖拽上传和点击上传两种方式，支持批量上传多个文件。

**支持的文件格式**：
- 文档：`.pdf`, `.doc`, `.docx`, `.txt`, `.md`
- 数据：`.csv`, `.json`, `.xml`

**文件大小限制**：50MB

**上传流程**：
1. 点击"上传文档"按钮或拖拽文件到上传区域
2. 自动验证文件类型和大小
3. 显示上传进度条（实时进度）
4. 上传完成后自动索引到向量库
5. 刷新文档列表显示新文件

**前端组件**：
- `FileUploadDialog` (`frontend/components/knowledge/FileUploadDialog.tsx`)
  - 拖拽上传区域
  - 多文件批量上传
  - 实时进度显示
  - 错误处理和重试功能
  - 上传统计信息

**后端接口**：
- `POST /api/upload`
- Content-Type: `multipart/form-data`
- Form field: `file`
- 自动保存到 `data/raw/`
- 自动处理并索引到 `data/processed/` 和 FAISS 向量库

**使用示例**：
```typescript
import { uploadChatFile } from '@/lib/api/files';

const handleUpload = async (file: File) => {
  const result = await uploadChatFile(file, (progress) => {
    console.log(`Upload progress: ${progress.loaded}/${progress.total}`);
  });
  console.log('Uploaded:', result.fileId);
};
```

---

## Agent 类型与 Prompt 管理

### 已实现功能 ✅

#### 1. Agent 类型系统
每个 Agent 类型都有独特的 system_prompt，在聊天时自动加载：

| Agent 类型 | 英文名 | 专业领域 | Prompt 示例 |
|-----------|--------|---------|------------|
| 通用助手 | `general` | 多领域知识问答 | "你是一个专业的AI助手，具备广泛的知识基础..." |
| 工艺专家 | `process` | 钢铁生产工艺优化 | "你是钢铁生产工艺专家，专注于生产流程的优化..." |
| 设备诊断 | `equipment` | 设备故障诊断维护 | "你是设备维护和故障诊断专家，具备丰富的设备管理经验..." |
| 市场分析师 | `market` | 市场情报趋势分析 | "你是市场分析专家，专注于钢铁行业的市场情报..." |
| 质量顾问 | `quality` | 质量控制改进 | "你是质量控制专家，专注于钢材质量管理..." |
| 节能专家 | `environment` | 节能环保 | "你是环保节能专家，专注于钢铁生产的能耗优化..." |

#### 2. 技术实现

**后端 (main.py)**:
```python
# ChatRequest 模型扩展
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    agent_type: str = "general"  # 新增：Agent类型
    user_role: str | None = None  # 新增：用户角色

# Agent 创建时注入 system_prompt
def _get_agent(session_id, agent_type="general", user_role=None):
    # 1. 从数据库查询该 agent_type 的 Agent
    agents = prompt_service.list_agents(agent_type=agent_type, is_active=True, limit=1)
    
    # 2. 获取该 Agent 的活跃 Prompt
    prompt_response = prompt_service.get_agent_prompt(agent_id=agent.id, language="zh-CN")
    system_prompt = prompt_response.content if prompt_response else None
    
    # 3. 创建 LLM 客户端时传入 system_prompt
    llm = OpenAIClient(cfg, system_prompt=system_prompt)
    agent = create_agent(llm, system_prompt=system_prompt)
```

**LLM 客户端 (src/llm/client.py)**:
```python
class OpenAIClient(LLMClient):
    def __init__(self, config: OpenAIConfig, system_prompt: str | None = None):
        self.system_prompt = system_prompt  # 存储 system_prompt
    
    def generate(self, prompt: str, system_prompt: str | None = None):
        # 构建消息时添加 system 角色
        messages = []
        if system_prompt or self.system_prompt:
            messages.append({"role": "system", "content": system_prompt or self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        # 调用 OpenAI API
```

**前端使用示例**:
```typescript
// components/chat/ChatInterface.tsx
const [agentType, setAgentType] = useState('general');

// 发送消息时携带 agent_type
const sendMessage = async (message: string) => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      agent_type: agentType,  // 🔑 关键：指定 Agent 类型
      session_id: sessionId
    })
  });
};

// Agent 类型选择器
<select value={agentType} onChange={(e) => setAgentType(e.target.value)}>
  <option value="general">通用助手</option>
  <option value="process">工艺专家</option>
  <option value="equipment">设备诊断</option>
  <option value="market">市场分析师</option>
  <option value="quality">质量顾问</option>
  <option value="environment">节能专家</option>
</select>
```

#### 3. 测试与验证

**查看所有 Agent 和 Prompt**:
```bash
python scripts/test_agent_prompts.py
```

**测试聊天 API**:
```bash
# 测试单个 Agent 类型
python scripts/test_chat_api.py --agent-type process --message "炼钢过程中如何控制温度？"

# 综合测试所有 Agent 类型
python scripts/test_chat_api.py --comprehensive

# 对比测试（相同问题不同 Agent 的回答差异）
python scripts/test_chat_api.py --compare
```

**后端日志验证**:
```bash
tail -f backend.log | grep "Agent 加载"
# 输出示例：
# ✅ 已为 process Agent 加载专属 Prompt (ID: 3, 名称: 默认process提示词)
# ✅ 已为 equipment Agent 加载专属 Prompt (ID: 5, 名称: 默认equipment提示词)
```

#### 4. 数据库管理

**查看 Agent 列表**:
```bash
python manage.py check --verbose
```

**管理 Prompt (通过 API)**:
- `GET /api/prompts/agents` - 获取所有 Agent
- `GET /api/prompts/agents/{agent_id}` - 获取单个 Agent
- `GET /api/prompts/{prompt_id}` - 获取 Prompt 详情
- `POST /api/prompts` - 创建新 Prompt
- `PUT /api/prompts/{prompt_id}` - 更新 Prompt
- `POST /api/prompts/{prompt_

## Vector Store Architecture (Fast Version)

### 概述
系统已升级为 **VectorStoreFast** 优化版本，支持自动索引选择和性能优化。

### 技术特性

#### 1. 自动索引选择策略
```python
# VectorStoreFast 自动选择最优索引类型
- 向量数 < 10,000:  IndexFlatIP (精确检索，O(n))
- 向量数 ≥ 10,000:  IndexIVFPQ (近似检索，O(log n)，5-10倍加速)
```

#### 2. 性能对比

| 索引类型 | 向量数 | 搜索速度 | 精度 | 适用场景 |
|---------|-------|---------|-----|---------|
| **IndexFlatIP** | < 10k | 快 (~1ms) | 100% | 小型知识库 |
| **IndexIVFPQ** | ≥ 10k | 极快 (~0.1ms) | ~98% | 大型知识库 |

#### 3. 自动升级机制
当向量数量达到 10,000 时，系统会自动升级索引：

```python
# 自动触发条件
if vector_count >= 10000 and not is_ivf:
    print("🚀 向量数量达到 10000，升级为IVF+PQ索引...")
    upgrade_to_ivf()  # 自动完成，无需手动操作
```

**升级过程**：
1. 提取现有向量
2. 训练 IVF 聚类中心（nlist=100）
3. 应用 PQ 压缩（m=8, nbits=8）
4. 重新添加所有向量
5. 保存新索引（自动备份旧索引）

#### 4. 配置参数

```python
# main.py 中的配置
VectorStoreFast(
    dim=384,                 # 向量维度（all-MiniLM-L6-v2）
    use_ivf=None,           # None=自动判断，True=强制IVF，False=强制Flat
    nlist=100,              # IVF聚类数（影响检索速度和精度）
    m=8,                    # PQ子向量数（压缩率）
    nbits=8,                # 每个子向量位数
)
```

**参数调优建议**：
- `nlist`: 聚类数 = sqrt(向量数)，100-1000 之间
- `m`: 子向量数，越大压缩率越低、精度越高，推荐 8-16
- `nbits`: 比特数，推荐 8（平衡精度和内存）

#### 5. 使用场景

**✅ 当前使用 Flat（推荐）**：
- 向量数 < 10,000
- 精度要求 100%
- 搜索速度已足够快（< 1ms）

**🚀 未来自动升级到 IVF**：
- 向量数 ≥ 10,000
- 需要更快检索速度
- 可接受 ~2% 精度损失

#### 6. 手动迁移（可选）

如果需要立即升级到 IVF（不推荐，除非向量数已 > 10k）：

```bash
# 备份现有索引并升级
python scripts/migrate_to_fast_index.py --auto

# 性能对比测试
python scripts/benchmark_rag_performance.py
```

#### 7. 监控和统计

```bash
# 查看索引状态
python scripts/rag_cli.py info

# 输出示例：
# 📥 加载向量库: 1345 个向量, 索引类型: Flat
# 向量库大小: 1345 个块
# 索引路径: D:\...\data\embeddings\index.faiss
```

**关键指标**：
- `索引类型`: Flat（精确）或 IVF+PQ（近似）
- `向量数量`: 当前存储的向量数
- `搜索性能`: 平均检索时间（通过 benchmark 测试）

#### 8. 故障排查

**问题：升级后搜索结果不准确**
- **原因**: IVF 近似检索可能丢失部分结果
- **解决**: 增加 `nprobe` 参数（探测更多聚类）
  ```python
  store.search(query_vec, top_k=5, nprobe=20)  # 默认10，增加到20提高召回
  ```

**问题：索引文件损坏或不兼容**
- **原因**: Fast 版本索引格式不同
- **解决**: 重新构建索引
  ```bash
  python scripts/rag_cli.py build --rebuild
  ```

---

## Troubleshooting & Known Issues

### 批量删除文档功能 (Batch Delete Documents)

#### 问题：前端批量删除返回 405 Method Not Allowed
**症状**：点击批量删除按钮后，控制台显示：
```
POST /api/admin/files/batch-delete HTTP/1.1" 405 Method Not Allowed
```

**原因**：后端缺少批量删除接口（已修复）

**解决方案**：
1. 确认后端 `src/api/admin.py` 包含批量删除接口：
   ```python
   @router.post("/files/batch-delete")
   def batch_delete_files(
       request: BatchDeleteRequest,
       db: Session = Depends(get_db),
       admin: User = Depends(require_admin),
   ):
   ```

2. 重启后端服务：
   ```bash
   python manage.py start backend
   ```

3. 测试批量删除：
   - 登录管理员账号
   - 访问 `http://localhost:3000/dashboard/knowledge`
   - 勾选多个文档
   - 点击"批量删除"按钮
   - 应该看到成功通知

**API 规格**：
- **端点**：`POST /api/admin/files/batch-delete`
- **权限**：管理员
- **请求体**：
  ```json
  {
    "fileNames": ["file1.pdf", "file2.txt"]
  }
  ```
- **响应体**：
  ```json
  {
    "success": ["file1.pdf"],
    "failed": [{"fileName": "file2.txt", "reason": "文件不存在"}],
    "total": 2
  }
  ```

**安全措施**：
- ✅ 路径遍历防护（拒绝包含 `..`、`/`、`\` 的文件名）
- ✅ 管理员权限验证
- ✅ 详细的操作日志记录

**前端类型定义** (`frontend/lib/types/api.ts`)：
```typescript
export interface BatchDeleteRequest {
    fileNames: string[];  // 使用 fileNames 而非 fileIds
}

export interface BatchDeleteResponse {
    success: string[];    // 成功删除的文件名列表
    failed: Array<{ fileName: string; reason: string }>;
    total: number;
}
```

#### 问题：删除后文件仍显示在列表中
**解决方案**：
1. 检查前端是否调用了缓存失效：
   ```typescript
   queryClient.invalidateQueries({ queryKey: ["documents"] });
   ```
2. 手动刷新页面验证
3. 检查后端日志确认删除成功

#### 问题：权限错误 403 Forbidden
**解决方案**：
1. 确认当前用户是管理员角色（role = "ADMIN"）
2. 检查 JWT token 有效性
3. 重新登录

### RAG 检索超时问题

#### 问题：查询响应缓慢或超时
**解决方案**：
1. 检查 `.env` 配置：
   ```bash
   RAG_TIMEOUT_SECONDS=25  # 调整超时时间
   ```
2. 检查后端日志是否显示 `fallback_mode: true`（表示已降级）
3. 优化 FAISS 索引或减少文档数量

### PDF 文档显示异常问题

#### 问题 1：检索结果显示全角字符（半角转全角）
**症状**：
- 文档预览中英文和数字显示为全角字符，例如：
  ```
  ｈｏｗｔｏｃｏｎｔｒｏｌｔｈｅｔｙｐｅ，ｔｏｔａｌａｍｏｕｎｔａｎｄｓｉｚｅ
  ２０２４，Ｖｏｌ. ３８，Ｎｏ. ３
  ```
- 搜索时使用半角字符无法正确匹配文档中的全角内容
- 影响搜索准确性和可读性

**原因**：
某些 PDF 文件（特别是学术期刊）使用特殊字体编码，导致提取的文本为全角字符。原有的 `_postprocess_pdf_text` 方法只处理了字母空格分离问题，未处理全角转半角。

**解决方案（已修复）**：
1. **代码修复**：在 `src/data_processing/loader.py` 中新增 `_convert_fullwidth_to_halfwidth` 方法
   - 自动将全角数字（０-９）转换为半角（0-9）
   - 自动将全角英文字母（Ａ-Ｚ，ａ-ｚ）转换为半角（A-Z, a-z）
   - 自动将全角标点和空格转换为半角
   - 基于 Unicode 范围 `0xFF01-0xFF5E` 和 `0x3000` 进行转换

2. **重建索引**：修复后需重建 RAG 索引以应用更新
   ```bash
   python scripts/rag_cli.py build --rebuild
   ```

3. **验证修复**：
   ```bash
   # 测试 PDF 加载是否正确转换
   python -c "from src.data_processing.loader import DataLoader; \
              loader = DataLoader(); \
              text = loader.load('your_file.pdf'); \
              print(text[:500])"
   ```

**技术细节**：
```python
def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
    """全角转半角：
    - 全角空格 (0x3000) -> 半角空格 (0x0020)
    - 全角 ASCII (0xFF01-0xFF5E) -> 半角 ASCII (0x0021-0x007E)
    - 转换公式：半角码 = 全角码 - 0xFEE0
    """
    result = []
    for char in text:
        code = ord(char)
        if code == 0x3000:
            result.append(' ')
        elif 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        else:
            result.append(char)
    return ''.join(result)
```

**已修复 - 连续英文智能分词**：
- **问题**：某些 PDF 中英文为连续全角字母无分隔（如 `Ｔｈｉｓｗｏｒｋｗａｓ`）
- **解决方案**：集成 `wordninja` 智能分词工具
  - 自动检测长连续英文字符串（10+ 字符）
  - 智能分词为正常单词，如 `Thisworkwas` → `This work was`
  - 对正常单词不产生影响（避免误伤）
- **效果对比**：
  ```
  查询: "how to control micro inclusions"
  
  ❌ 全角字符（修复前）:      -0.8% 相似度
  ⚠️  半角无空格（简单转换）:  14.0% 相似度
  ✅ 智能分词（修复后）:      98.8% 相似度 🎉
  ```
- **性能提升**：相比简单转换提升 **605.7%**，接近完美！
- **依赖安装**：
  ```bash
  pip install wordninja
  # 或重新安装依赖
  pip install -r requirements.txt
  ```

#### 问题 2：明确存在的文档检索不到或相关度低
**症状**：
- 知识库中存在文件 `高精度冷连轧数字孪生与信息.CPS关键技术研发及应用.pdf`
- 查询 "高精度冷连轧数字孪生与信息是什么" 时，该文档未出现在 Top 10 结果中
- 或相关度得分较低（如 64.9%），排名靠后

**原因分析**：
1. **文档结构问题**：
   - 文档标题在第一个分块中，但没有实际内容解释"是什么"
   - 其他分块包含具体技术细节，但缺少概念性解释
   - 查询意图（"是什么"）与文档内容（技术实现）语义不匹配

2. **分块策略问题**：
   - 默认分块大小 600 字符，overlap 100 字符
   - 标题和正文可能被分隔到不同块中
   - 关键信息分散在多个块中，降低单块相关度

3. **查询-文档语义差距**：
   - 用户查询："高精度冷连轧数字孪生与信息是什么"（概念查询）
   - 文档内容："多策略厚度张力解耦控制算法"（技术实现）
   - Embedding 模型将它们视为不同语义空间

**解决方案**：

1. **优化查询策略**：
   ```bash
   # 使用更具体的关键词
   "高精度冷连轧数字孪生 CPS 关键技术"  # ✅ 更接近文档内容
   "高精度冷连轧数字孪生与信息是什么"    # ❌ 过于概念化
   ```

2. **调整分块参数**（可选）：
   ```bash
   # 增大分块大小以保留更多上下文
   python scripts/rag_cli.py build --chunk-size 1000 --chunk-overlap 200
   ```

3. **增加 top_k 值**：
   ```python
   # 在 config/settings.py 中调整
   top_k: int = 10  # 默认 5，增加到 10 可能找到更多相关文档
   ```

4. **使用文件名搜索**（临时方案）：
   - 如果知道文件名，可以在知识库页面直接搜索文件名
   - 或使用管理后台的文件列表筛选

5. **检查文档内容**：
   ```bash
   # 查看文档的实际分块内容
   python -c "import json; from pathlib import Path; \
              p = Path('data/processed/YOUR_FILE.pdf.chunks.jsonl'); \
              lines = p.read_text(encoding='utf-8').split('\n'); \
              [print(f'块{i}:', json.loads(line)['content'][:200], '\n') \
               for i, line in enumerate(lines[:5])]"
   ```

**为什么相关度是 64.9%？**
- FAISS 使用归一化余弦相似度，范围 `[0, 1]`
- 0.649 表示查询向量与文档向量的余弦相似度为 64.9%
- 这个得分说明**语义相关但不完全匹配**
- 对于概念查询 vs 技术实现文档，60-70% 的相关度是正常的

**最佳实践**：
1. ✅ 上传文档时确保包含概念性介绍（摘要、引言）
2. ✅ **查询时使用文档中实际出现的技术术语**（如"板形控制"、"张力解耦"、"协同优化"）
3. ✅ 对于特定文档查询，结合文件名搜索
4. ✅ 定期检查分块质量（使用 `rag_cli.py info`）
5. ✅ **使用诊断工具测试查询效果**（`python scripts/diagnose_retrieval.py`）
6. ❌ 避免过于宽泛或概念化的查询（"是什么"、"介绍一下"等）
7. ❌ 避免只使用文档标题查询（标题可能被元数据稀释）

### 前端开发服务器问题

#### 问题：npm run dev 失败
**解决方案**：
1. 删除依赖并重新安装：
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```
2. 检查 Node.js 版本（需要 18+）：
   ```bash
   node --version
   ```

#### 问题：shadcn 组件未正确显示
**解决方案**：
1. 确认已安装 shadcn 组件：
   ```bash
   npx shadcn@latest add sonner
   ```
2. 检查 `components.json` 配置
3. 验证 Tailwind CSS 配置正确

### 数据库问题

#### 问题：数据库连接失败
**解决方案**：
1. 重置数据库：
   ```bash
   python scripts/db_migrate.py reset
   ```
2. 重新初始化：
   ```bash
   python manage.py init
   ```

#### 问题：找不到表或字段
**解决方案**：
1. 运行迁移：
   ```bash
   python scripts/db_migrate.py add-prompts
   ```
2. 检查数据库状态：
   ```bash
   python manage.py check --verbose
   ```

### 文件上传问题

#### 问题：上传后显示重复文件或文件名包含哈希前缀
**症状**：
- 上传一个文件后，列表中显示两个文件
- 其中一个文件大小为 2 Bytes（.done 文件）
- 文件名包含 `.chunks.jsonl` 扩展名
- 预览/下载失败，返回 404 错误

**根本原因**：
1. `list_files` 接口原本从 `data/processed` 读取，列出了内部处理文件（.chunks.jsonl, .done）
2. 文件 ID 使用 `doc.fileName`（显示名称）而不是完整的 `doc.id`（包含哈希前缀）

**解决方案（已修复）**：
1. **后端修改** (`src/api/admin.py`):
   - `list_files` 改为从 `data/raw` 读取原始文件
   - 过滤掉内部处理文件（.chunks.jsonl, .done）
   - 使用实际文件名作为 ID，提取显示名称（移除哈希前缀）
   - `delete_file` 同时删除 `data/raw` 和 `data/processed` 中的文件
   - 新增 `preview_file` 和 `download_file` 接口

2. **前端修改** (`frontend/app/dashboard/knowledge/page.tsx`):
   - 所有 API 调用使用 `doc.id`（完整文件 ID）而不是 `doc.fileName`
   - 预览：`previewDocument(doc.id)`
   - 下载：`downloadDocument(doc.id)`
   - 删除：`deleteDocument(doc.id)`
   - 批量删除：使用 `doc.id` 数组
   - 重新索引：`reindexDocument(doc.id)`

**文件存储结构**：
```
data/
├── raw/                          # 原始上传文件
│   └── {hash}_{filename}         # 完整 file_id
└── processed/                    # 处理后的文件
    ├── {hash}_{filename}.chunks.jsonl  # 分块数据
    └── {hash}_{filename}.done          # 处理完成标记
```

**API 端点更新**：
- `GET /api/admin/files` - 从 data/raw 读取，返回 `{id: 完整file_id, fileName: 显示名称}`
- `GET /api/admin/files/{file_name}/preview` - 预览原始文件 + 分块信息
- `GET /api/admin/files/{file_name}/download` - 下载原始文件
- `DELETE /api/admin/files/{file_name}` - 删除原始文件 + 处理文件

#### 问题：上传按钮点击无反应
**解决方案**：
1. 检查 `FileUploadDialog` 组件是否正确导入
2. 确认 `isUploadDialogOpen` 状态已添加
3. 验证按钮 `onClick` 事件绑定正确

#### 问题：文件上传失败
**常见原因**：
1. 文件大小超过 50MB 限制
2. 文件格式不支持（只支持 PDF, DOC, DOCX, TXT, MD, CSV, JSON, XML）
3. 后端服务未启动或无权限
4. 磁盘空间不足

**解决方案**：
1. 检查文件大小：`ls -lh data/raw/`
2. 验证文件格式扩展名
3. 检查后端日志是否有错误
4. 确认 `data/raw/` 和 `data/processed/` 目录存在且可写

#### 问题：文件上传后无法检索
**解决方案**：
1. 检查向量索引是否成功：
   ```bash
   python scripts/rag_cli.py info
   ```
2. 重建 RAG 索引：
   ```bash
   python scripts/rag_cli.py build --rebuild
   ```
3. 检查文档是否在 `data/processed` 目录
4. 验证 `.done` 标记文件是否存在

#### 问题：上传进度条不显示
**解决方案**：
1. 检查 `Progress` 组件是否正确安装
2. 验证 Axios `onUploadProgress` 回调是否正确
3. 检查浏览器控制台是否有 JavaScript 错误

#### 问题：预览/下载返回 404 Not Found
**症状**：
```
GET /api/admin/files/xxx.chunks.jsonl/preview HTTP/1.1" 404 Not Found
```

**原因**：前端使用 `doc.fileName`（显示名称）而不是 `doc.id`（完整文件 ID）

**解决方案**：
1. 确保前端所有文件操作使用 `doc.id`
2. 检查后端接口从 `data/raw` 读取文件
3. 验证文件 ID 格式正确：`{hash}_{original_name}`

### 通用调试步骤

1. **检查后端日志**：查看详细错误信息
2. **检查前端 Console**：查看 JavaScript 错误
3. **检查 Network 标签**：验证 API 请求/响应
4. **重启服务**：
   ```bash
   python manage.py start backend
   npm run dev  # 在 frontend 目录
   ```
5. **清除缓存**：浏览器开发者工具 → Application → Clear storage