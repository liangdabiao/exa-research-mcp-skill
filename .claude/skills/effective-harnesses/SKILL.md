---
name: effective-harnesses
description: 长时间运行 Agent 框架 - 项目初始化、feature 管理、进度追踪
allowed-tools: ["Read", "Glob", "Grep", "Edit", "Write", "Bash", "Task", "AskUserQuestion"]
---

# Effective Harnesses Skill

本 skill 提供完整的长时间运行 Agent 框架实现，支持项目初始化、feature 管理、会话恢复和进度追踪。

## 核心原则

- **单 feature 原则**: 每次只处理一个 feature，完成后再处理下一个
- **状态追踪**: 所有 feature 状态必须记录在 feature_list.json 中
- **会话恢复**: 每次会话开始时自动恢复上下文
- **及时提交**: 会话结束时必须提交 git
- **单元测试**: 每个 feature 完成后必须运行单元测试验证

## 可用命令

| 命令 | 功能 |
|------|------|
| `/harness-init` | 初始化新项目 |
| `/harness-add` | 添加新 feature |
| `/harness-status` | 查看项目进度 |
| `/harness-complete` | 标记 feature 完成 |

## 会话恢复流程

每次新会话开始时自动执行：

1. 检查当前目录是否存在 feature_list.json
2. 读取 git log 了解项目历史
3. 读取进度文件了解当前状态
4. 选择最高优先级的未完成 feature
5. 运行 init.sh 启动开发服务器
6. 验证基础功能未被破坏

## feature_list.json 结构

```json
{
  "version": "1.1",
  "project": "项目名称",
  "test_command": "npm test",
  "created": "2026-02-14",
  "features": [
    {
      "id": "feat-001",
      "category": "functional",
      "priority": 1,
      "description": "功能描述",
      "steps": ["步骤1", "步骤2", "步骤3"],
      "test_command": "npm test",
      "test_status": "passed",
      "test_output": "测试输出摘要",
      "status": "completed",
      "passes": true
    }
  ]
}
```

## Category 类型

- `functional`: 新功能开发
- `bugfix`: Bug 修复
- `refactor`: 代码重构

## 单元测试要求

每个 feature 完成后必须运行单元测试：

1. **测试命令**: 在添加 feature 时需要指定测试命令（如 `npm test`、`pytest` 等）
2. **测试验证**: 标记 feature 完成前必须运行测试并确认通过
3. **测试覆盖**: 新功能应有对应的单元测试

### feature 测试字段

```json
{
  "id": "feat-001",
  "test_command": "npm test",
  "test_status": "passed", // pending, running, passed, failed
  "test_output": "测试输出摘要"
}
```
