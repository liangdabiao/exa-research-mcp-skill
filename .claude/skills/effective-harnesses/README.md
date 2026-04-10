# Effective Harnesses

基于 [Anthropic 工程博客](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 经验总结的 Claude Code Skill，用于构建长时间运行 Agent 的有效框架。

## 概述

本项目提供了一套完整的框架，帮助你在长时间运行的开发项目中保持进度追踪和上下文记忆。特别适合：

- 复现论文算法
- 大型项目开发
- 多阶段研究项目

## 核心特性

- **项目初始化**: 一键创建完整的开发框架
- **Feature 管理**: 将复杂任务分解为可追踪的小任务
- **会话恢复**: 每次打开项目自动恢复上下文
- **进度追踪**: 实时查看项目完成状态
- **Git 集成**: 自动记录每次工作内容
- **单元测试**: 每个 feature 完成后必须通过测试验证
- **代码规范**: 自动生成项目代码规范文档

## 快速开始

### 1. 安装

```bash
git clone https://github.com/Suibosama/effective-harnesses.git ~/.claude/skills/effective-harnesses
```

### 2. 初始化项目

在项目目录中告诉 Claude：
> "使用 effective-harnesses 初始化项目"

Claude 会询问：
- 项目名称
- 开发服务器启动命令
- 测试命令（如 npm test、pytest 等）

### 3. 添加 Feature

> "添加一个 feature：实现数据加载模块"

### 4. 查看进度

> "查看项目状态"

### 5. 标记完成

> "完成当前 feature"

## 项目结构

```
├── SKILL.md                    # 主 skill 文件
├── commands/
│   ├── init.md                # 初始化命令
│   ├── add-feature.md         # 添加 feature 命令
│   ├── status.md              # 查看进度命令
│   └── complete.md            # 标记完成命令
├── templates/
│   ├── feature-list.json      # Feature 列表模板
│   ├── init.sh                # 启动脚本模板
│   └── progress.txt           # 进度日志模板
└── README.md
```

## 框架文件

使用后会生成以下文件：

| 文件 | 说明 |
|------|------|
| `feature_list.json` | 所有 feature 的状态清单 |
| `init.sh` | 启动开发服务器的脚本 |
| `claude-progress.txt` | 进度日志 |
| `CODING_STANDARDS.md` | 项目代码规范 |

## feature_list.json 结构

```json
{
  "version": "1.1",
  "project": "项目名称",
  "test_command": "npm test",
  "features": [
    {
      "id": "feat-001",
      "category": "functional",
      "priority": 1,
      "description": "功能描述",
      "steps": ["步骤1", "步骤2"],
      "test_command": "npm test",
      "test_status": "passed",
      "test_output": "测试输出摘要",
      "status": "completed",
      "passes": true
    }
  ]
}
```

## 单元测试要求

每个 feature 完成后必须运行单元测试：

1. **添加 feature 时**: 指定测试命令（如 `npm test`、`pytest` 等）
2. **完成 feature 时**: 强制运行测试，只有测试通过才能标记为完成
3. **测试状态**: feature 包含 `test_status` 字段，记录测试结果

## Category 类型

- `functional`: 新功能开发
- `bugfix`: Bug 修复
- `refactor`: 代码重构

## 使用示例：复现论文

假设要复现"基于流批融合的端到端自动驾驶算法"：

1. 初始化项目
2. 添加 feature：
   - 数据集准备
   - 感知模块
   - 预测模块
   - 规划模块
   - 训练流程

3. 逐个完成每个 feature
4. 随时查看进度

## 参考

- [Anthropic 工程博客: Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code)

## License

MIT
