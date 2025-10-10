# MySQL数据库 MCP 服务

这是一个专为 Cursor 设计的MySQL数据库 MCP (Model Context Protocol) 服务，提供表结构查询、文档生成和数据查询功能。

## 功能特性

- **Cursor 专用集成**: 专为 Cursor MCP 协议设计的数据库服务
- **多种安全模式**: 支持只读、限制写入、完全访问三种安全级别
- **表结构查询**: 获取数据库表的详细结构信息
- **文档生成**: 生成 Markdown、JSON、SQL 格式的表结构文档
- **数据库概览**: 生成整个数据库的概览文档
- **SQL 查询执行**: 根据安全模式执行不同级别的 SQL 操作
- **查询缓存**: 自动缓存查询结果，提升性能

## 安全模式

### 1. 只读模式 (readonly) - 默认模式
- 仅允许 SELECT、SHOW、DESCRIBE、EXPLAIN 等查询操作
- 禁止所有写入和危险操作
- 适用于数据分析和报表查询

### 2. 限制写入模式 (limited_write)
- 允许 SELECT、INSERT、UPDATE 操作
- 禁止 DELETE、DROP、CREATE、ALTER 等危险操作
- 适用于需要数据录入但要保护结构的场景

### 3. 完全访问模式 (full_access)
- 允许所有 SQL 操作
- 谨慎使用，仅在完全信任的环境中启用
- 适用于数据库管理和维护

## 安装和配置

### 1. 本地安装依赖

```bash
cd mysql-mcp
pip install -r requirements.txt
```

### 2. 在 Cursor 中配置

在 Cursor 的设置中找到 MCP 配置，添加以下内容：

```json
{
  "mcpServers": {
    "mysql-mcp": {
      "command": "python",
      "args": ["F:/path/to/mysql-mcp/main.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USERNAME": "your_username",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_database",
        "MYSQL_SECURITY_MODE": "readonly",
        "MYSQL_ALLOWED_SCHEMAS": "*",
        "MYSQL_ENABLE_QUERY_LOG": "false"
      }
    }
  }
}
```

### 3. 环境变量说明

**必需环境变量：**
- `MYSQL_HOST`: 数据库主机地址
- `MYSQL_PORT`: 数据库端口
- `MYSQL_USERNAME`: 数据库用户名
- `MYSQL_PASSWORD`: 数据库密码
- `MYSQL_DATABASE`: 数据库名称

**可选环境变量：**
- `MYSQL_SECURITY_MODE`: 安全模式 (readonly/limited_write/full_access，默认：readonly)
- `MYSQL_ALLOWED_SCHEMAS`: 允许访问的数据库列表，支持三种配置方式：
  - `"*"`: 允许访问所有有权限的数据库（推荐）
  - `"auto"`: 自动发现有权限的数据库  
  - `"db1,db2,db3"`: 明确指定数据库列表（逗号分隔）
- `MYSQL_CONNECT_TIMEOUT`: 连接超时时间（秒，默认：30）
- `MYSQL_QUERY_TIMEOUT`: 查询超时时间（秒，默认：60）
- `MYSQL_MAX_RETRIES`: 最大重试次数（默认：3）
- `MYSQL_ENABLE_QUERY_LOG`: 是否启用查询日志（true/false，默认：false）
- `MYSQL_MAX_RESULT_ROWS`: 最大返回行数（默认：1000）

## 使用示例

### 获取安全信息
在 Cursor 中输入：
```
@mysql-mcp 获取当前安全配置信息
```

### 查看可访问的数据库
```
@mysql-mcp 获取所有可访问的数据库
```

### 查询表列表
```
@mysql-mcp 列出 mydb 数据库中的所有表
```

### 查看表结构
```
@mysql-mcp 描述 users 表的结构
```

### 执行查询（只读模式）
```
@mysql-mcp 查询用户表前10条记录
```

### 生成表文档
```
@mysql-mcp 为users表生成Markdown文档
```

### 生成数据库概览
```
@mysql-mcp 生成mydb数据库的概览文档
```

## 可用工具

| 工具名称 | 功能描述 | 主要参数 |
|---------|---------|---------|
| `test_connection` | 测试数据库连接 | - |
| `get_security_info` | 获取安全配置信息 | - |
| `list_tables` | 获取数据库表列表 | `database`(可选) |
| `describe_table` | 获取表详细结构 | `table_name`, `database`(可选) |
| `generate_table_doc` | 生成表文档 | `table_name`, `format`, `database`(可选) |
| `generate_database_overview` | 生成数据库概览 | `database`(可选) |
| `execute_query` | 执行SQL语句 | `sql` |
| `list_schemas` | 获取可用数据库列表 | - |

## 文档生成说明

文档生成功能会将生成的文档保存为实际文件：

- **保存位置**: mysql-mcp目录下的 `docs/` 文件夹
- **文件命名**: `{database}_{table_name}_{timestamp}.{ext}` 格式
- **支持格式**: Markdown (.md)、JSON (.json)、SQL (.sql)

**示例输出**:
```
✅ 文档生成成功!
📁 保存路径: docs/mydb_users_20250110_142000.md
📂 MCP服务目录: F:/path/to/mysql-mcp
📊 表名: mydb.users
📝 格式: markdown
⏰ 生成时间: 2025-01-10 14:20:00
```

## 缓存管理

该服务提供查询缓存功能，自动缓存只读查询的结果：

```
# 获取缓存统计信息
@mysql-mcp 获取查询缓存统计信息

# 清空缓存
@mysql-mcp 清空查询缓存
```

## 安全注意事项

1. **生产环境**建议使用 `readonly` 模式
2. **敏感环境**中避免使用 `full_access` 模式
3. **密码安全**：避免在配置中使用弱密码
4. **网络安全**：确保数据库连接使用安全的网络通道
5. **权限最小化**：数据库用户只应获得必要的最小权限

## 错误处理

- **配置错误**: 检查 Cursor MCP 配置中的环境变量设置
- **连接失败**: 验证数据库连接参数和网络连通性
- **权限不足**: 检查数据库用户权限和安全模式设置
- **SQL 被拒绝**: 当前安全模式不允许执行该类型的 SQL 操作

## 技术架构

### 核心模块
- `main.py`: MCP服务主程序
- `config.py`: 环境变量配置模块
- `database.py`: 数据库操作和安全控制模块
- `document_generator.py`: 文档生成模块

### 安全控制
- 多级安全模式验证
- SQL语句类型检查
- 数据库访问权限控制
- 查询结果行数限制
- 连接超时和重试机制

### MySQL适配
- 使用 mysql-connector-python 驱动连接
- 适配MySQL系统表查询语法
- 支持MySQL约束类型识别
- 适配MySQL数据类型映射

## 许可证

本项目基于 [MIT 许可证](./LICENSE) 开源发布。

- ✅ **自由使用**: 允许任何人免费使用、复制、修改本软件
- ✅ **商业友好**: 支持商业使用和分发
- ✅ **修改自由**: 可以修改源代码并发布衍生作品
- ✅ **最小限制**: 只需保留版权声明即可

---

**版本**: 1.0.0  
**更新时间**: 2025-01-10  
**设计目标**: 专为MySQL数据库和 Cursor MCP 集成优化 