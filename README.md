# MySQL数据库MCP服务

专为Cursor IDE集成设计的MySQL数据库MCP（Model Context Protocol）服务，提供安全的MySQL数据库访问和管理功能。

## 🌟 功能特性

- **🔒 多层安全控制**：三种安全模式（只读、限制写入、完全访问）
- **📊 智能文档生成**：支持Markdown、JSON、SQL等多种格式
- **🎯 Cursor深度集成**：专为Cursor IDE优化的MCP协议支持
- **🛡️ SQL安全验证**：智能SQL验证器防止危险操作
- **⚡ 高性能连接**：连接池和超时控制
- **📋 完整表管理**：表结构、索引、约束等全方位信息

## 🔧 安装配置

### 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+
- Cursor IDE

### 快速安装

```bash
# 克隆项目
git clone https://github.com/Gcluowenqiang/Mysql-mcp.git
cd mysql-mcp

# 安装依赖
pip install -r requirements.txt
```

### Cursor MCP配置

在Cursor IDE中，添加以下配置到 MCP 设置：

```json
{
  "mcpServers": {
    "mysql-db": {
      "command": "python",
      "args": ["path/to/mysql-mcp/main.py"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306", 
        "MYSQL_USERNAME": "your_username",
        "MYSQL_PASSWORD": "your_password",
        "MYSQL_DATABASE": "your_database",
        "MYSQL_SECURITY_MODE": "readonly",
        "MYSQL_ALLOWED_SCHEMAS": "*",
        "MYSQL_MAX_RESULT_ROWS": "1000"
      }
    }
  }
}
```

## 🚀 使用指南

### 基本操作

1. **测试连接**
   ```
   在Cursor中使用MCP工具: test_connection
   ```

2. **查看数据库概览**
   ```
   使用工具: generate_database_overview
   ```

3. **查询表结构**
   ```
   使用工具: describe_table
   参数: table_name = "your_table"
   ```

4. **执行SQL查询**
   ```
   使用工具: execute_query
   参数: sql = "SELECT * FROM users LIMIT 10"
   ```

### 安全模式说明

#### 🟢 只读模式 (readonly)
- ✅ SELECT、SHOW、DESCRIBE等查询操作
- ❌ 禁止任何写入和修改操作
- 🎯 **推荐**：生产环境查询、数据分析

#### 🟡 限制写入模式 (limited_write)  
- ✅ 查询操作 + INSERT、UPDATE
- ❌ 禁止DELETE、DROP、ALTER等危险操作
- 🎯 **适用**：开发环境、数据维护

#### 🔴 完全访问模式 (full_access)
- ✅ 所有SQL操作
- ⚠️ **警告**：仅在完全可控的环境使用

## 📋 可用工具

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

## ⚙️ 配置参数

### 必需环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `MYSQL_HOST` | 数据库主机地址 | `localhost` |
| `MYSQL_PORT` | 数据库端口 | `3306` |
| `MYSQL_USERNAME` | 数据库用户名 | `myuser` |
| `MYSQL_PASSWORD` | 数据库密码 | `mypassword` |
| `MYSQL_DATABASE` | 默认数据库名 | `mydatabase` |

### 可选环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_SECURITY_MODE` | `readonly` | 安全模式 |
| `MYSQL_ALLOWED_SCHEMAS` | `["*"]` | 允许访问的数据库列表 |
| `MYSQL_CONNECT_TIMEOUT` | `30` | 连接超时（秒） |
| `MYSQL_QUERY_TIMEOUT` | `60` | 查询超时（秒） |
| `MYSQL_MAX_RESULT_ROWS` | `1000` | 最大返回行数 |
| `MYSQL_ENABLE_QUERY_LOG` | `false` | 启用查询日志 |

## 📖 文档生成

### 支持格式

- **Markdown**: 人类友好的文档格式
- **JSON**: 机器可读的结构化数据
- **SQL**: 可执行的建表语句

### 生成示例

```python
# 生成单表Markdown文档
generate_table_doc(table_name="users", format="markdown")

# 生成数据库概览
generate_database_overview()

# 生成SQL建表语句
generate_table_doc(table_name="orders", format="sql")
```

## 🔒 安全最佳实践

1. **生产环境**：始终使用 `readonly` 模式
2. **权限最小化**：仅授予必要的数据库权限
3. **网络安全**：使用SSL连接，限制网络访问
4. **监控日志**：启用查询日志监控异常操作
5. **定期更新**：保持依赖库和数据库版本更新

## 🔍 故障排除

### 常见问题

**Q: 连接失败？**
```
A: 检查以下项目：
   1. 数据库服务是否运行
   2. 网络连接是否正常
   3. 用户名密码是否正确
   4. 防火墙设置
```

**Q: 权限不足？**
```
A: 确保数据库用户具有：
   - 目标数据库的访问权限
   - INFORMATION_SCHEMA的查询权限
   - 根据安全模式配置相应的操作权限
```

**Q: SQL被拒绝？**
```
A: 检查当前安全模式设置：
   - readonly: 仅允许查询操作
   - limited_write: 不允许DELETE/DROP等危险操作
   - 调整安全模式或修改SQL语句
```

## 🧪 开发测试

```bash
# 运行单元测试
pytest tests/

# 启动开发服务器
python main.py

# 检查代码质量
flake8 *.py
```

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新信息。

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙋‍♂️ 支持

- 📧 邮箱: wxhn1217@outlook.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/Gcluowenqiang/Mysql-mcp/issues)
- 📖 文档: [项目Wiki](https://github.com/Gcluowenqiang/Mysql-mcp/wiki)

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！ 