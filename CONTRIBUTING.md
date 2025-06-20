# 贡献指南

感谢你对MySQL MCP服务项目的关注和贡献！本指南将帮助你了解如何参与项目开发。

## 🚀 快速开始

### 开发环境准备

1. **系统要求**
   - Python 3.8+
   - MySQL 5.7+ 或 MySQL 8.0+
   - Git

2. **克隆仓库**
   ```bash
   git clone https://github.com/Gcluowenqiang/Mysql-mcp.git
   cd mysql-mcp
   ```

3. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

4. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   ```

5. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，配置你的MySQL连接信息
   ```

## 📝 开发规范

### 代码风格

我们遵循以下代码风格标准：

- **PEP 8**: Python代码风格指南
- **类型注解**: 使用类型提示增强代码可读性
- **文档字符串**: 使用Google风格的docstring

#### 代码格式化工具
```bash
# 使用black格式化代码
black *.py

# 使用isort整理导入
isort *.py

# 使用flake8检查代码质量
flake8 *.py
```

### 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>[可选 作用域]: <描述>

[可选 正文]

[可选 脚注]
```

#### 提交类型
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

#### 示例
```bash
git commit -m "feat(database): 添加MySQL 8.0连接支持"
git commit -m "fix(config): 修复环境变量验证错误"
git commit -m "docs(readme): 更新安装指南"
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_database.py

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 编写测试

1. **测试文件命名**: `test_*.py`
2. **测试函数命名**: `test_*`
3. **使用pytest fixtures**: 共享测试数据和设置

#### 测试示例
```python
import pytest
from database import MySQLDatabase

@pytest.fixture
def db_instance():
    return MySQLDatabase()

def test_connection(db_instance):
    assert db_instance.test_connection() == True

def test_sql_validation():
    from database import SQLValidator
    assert SQLValidator.validate_sql("SELECT * FROM users", "readonly") == True
    assert SQLValidator.validate_sql("DROP TABLE users", "readonly") == False
```

## 🐛 问题报告

### 报告Bug

使用GitHub Issues报告bug时，请包含以下信息：

1. **环境信息**
   - 操作系统
   - Python版本
   - MySQL版本
   - 项目版本

2. **问题描述**
   - 详细的问题描述
   - 预期行为 vs 实际行为
   - 重现步骤

3. **错误信息**
   - 完整的错误日志
   - 相关配置信息（敏感信息请脱敏）

#### Bug报告模板
```markdown
## 环境信息
- OS: Ubuntu 20.04
- Python: 3.9.7
- MySQL: 8.0.28
- Project: v1.0.0

## 问题描述
连接MySQL时出现超时错误

## 重现步骤
1. 配置环境变量
2. 运行 python main.py
3. 调用 test_connection 工具

## 错误信息
```
ERROR: Connection timeout after 30 seconds
```

## 预期行为
应该成功连接到数据库
```

### 功能请求

提交功能请求时，请说明：

1. **用例场景**: 为什么需要这个功能
2. **功能描述**: 详细的功能说明
3. **实现建议**: 如果有技术想法可以分享
4. **优先级**: 功能的重要程度

## 🔄 提交流程

### 1. Fork & Clone
```bash
# Fork项目到你的GitHub账户
# 然后克隆你的fork
git clone https://github.com/your-username/mysql-mcp.git
cd mysql-mcp
```

### 2. 创建分支
```bash
# 从main分支创建功能分支
git checkout -b feature/amazing-feature
# 或修复分支
git checkout -b fix/issue-123
```

### 3. 开发
- 编写代码
- 添加测试
- 更新文档
- 确保测试通过

### 4. 提交
```bash
git add .
git commit -m "feat: 添加新的功能"
```

### 5. 推送
```bash
git push origin feature/amazing-feature
```

### 6. 创建Pull Request

在GitHub上创建PR时：
- 使用清晰的标题
- 详细描述变更内容
- 链接相关的issue
- 确保CI检查通过

#### PR模板
```markdown
## 变更描述
简要描述这个PR的变更内容

## 变更类型
- [ ] Bug修复
- [ ] 新功能
- [ ] 代码重构
- [ ] 文档更新
- [ ] 其他

## 测试
- [ ] 单元测试通过
- [ ] 手动测试完成
- [ ] 添加了新的测试

## 检查清单
- [ ] 代码符合项目规范
- [ ] 提交信息清晰明确
- [ ] 更新了相关文档
- [ ] 无冲突和编译错误

## 相关Issue
关闭 #123
```

## 📚 文档贡献

### 文档类型
- **README**: 项目介绍和快速开始
- **API文档**: 代码接口文档
- **教程**: 详细的使用指南
- **FAQ**: 常见问题解答

### 文档规范
- 使用Markdown格式
- 添加目录结构
- 包含代码示例
- 保持更新性

## 🏷️ 发布流程

### 版本号规则
遵循 [语义化版本](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- 例如：`1.2.3`

### 发布步骤
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Git标签
4. 发布GitHub Release
5. 更新文档

## 🛡️ 安全相关

### 安全漏洞报告
如果发现安全漏洞，请：
1. **不要**在公开issue中报告
2. 发送邮件到：security@example.com
3. 包含详细的漏洞信息
4. 等待安全团队回复

### 安全最佳实践
- 不在代码中硬编码敏感信息
- 使用环境变量管理配置
- 定期更新依赖库
- 遵循最小权限原则

## 🤝 社区准则

### 行为规范
- 尊重他人，包容不同观点
- 建设性地提供反馈
- 专注于技术讨论
- 帮助新贡献者

### 沟通渠道
- **GitHub Issues**: Bug报告和功能请求
- **GitHub Discussions**: 技术讨论和问答
- **Email**: security@example.com（安全问题）

## 🎯 贡献指南

### 优先级项目
- 性能优化
- 错误处理改进
- 文档完善
- 测试覆盖率提升

### 适合新手的任务
查找标有以下标签的issue：
- `good first issue`
- `help wanted`
- `documentation`

## 📞 联系我们

- 维护者：qyue
- 邮箱：wxhn1217@outlook.com
- GitHub：[@Gcluowenqiang](https://github.com/Gcluowenqiang)

---

**感谢你的贡献！** 🎉

每一个贡献都让这个项目变得更好。无论是代码、文档、测试还是反馈，我们都非常欢迎和感激。 