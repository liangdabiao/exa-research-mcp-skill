# /harness-status 命令

## 功能

查看当前项目的开发进度。

## 执行步骤

### 1. 检查项目是否已初始化

确认 feature_list.json 存在：

```bash
ls feature_list.json
```

如果不存在，提示用户先运行 `/harness-init`。

### 2. 读取 feature_list.json

```bash
Read feature_list.json
```

### 3. 读取进度日志（如果存在）

```bash
Read claude-progress.txt
```

### 4. 读取最近 git 提交

```bash
git log --oneline -5
```

### 5. 统计并展示进度

计算：
- 总 feature 数
- 已完成数（passes: true）
- 进行中数（status: in_progress）
- 未开始数（status: pending）

按 category 分类展示：

```
## Project: 项目名称
Created: 2026-02-14

## Progress
Total: X | Completed: X | In Progress: X | Pending: X

### Completed (X)
- [x] feat-001: 功能描述

### In Progress (X)
- [ ] feat-002: 功能描述

### Pending (X)
- [ ] feat-003: 功能描述
```

## 输出

- 项目基本信息
- 分类展示所有 feature 及其状态
- 最近 git 提交记录
- 下一个建议执行的 feature
