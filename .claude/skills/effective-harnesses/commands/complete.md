# /harness-complete 命令

## 功能

标记指定 feature 为已完成，并更新进度。

## 执行步骤

### 1. 确认项目已初始化

检查 feature_list.json 是否存在。

### 2. 列出所有未完成的 feature

```bash
Read feature_list.json
```

提取所有 passes: false 的 feature。

### 3. 让用户选择要完成的 feature

使用 AskUserQuestion 让用户选择：
- 列出所有未完成的 feature
- 或者选择 "全部完成" 选项

### 4. 运行单元测试（必须步骤）

**这是强制要求**，在标记为完成前必须执行：

1. **读取 test_command**: 从 feature 中获取测试命令

2. **运行测试**:
   - 如果 test_command 不是 "none"，执行测试命令
   - 记录测试输出

3. **检查测试结果**:
   - 如果测试失败，显示错误信息
   - 询问用户是否修复测试或标记为已完成（即使测试失败）
   - 只有测试通过才能将 passes 设置为 true

4. **更新测试状态**:
   - 如果测试通过: `test_status: "passed"`
   - 如果测试失败: `test_status: "failed"`，并记录错误摘要

### 5. 验证功能是否真正完成

在标记为完成前，需要验证：

1. **代码完整性**: 所有预期的代码变更都已实现
2. **功能测试**: 功能是否按预期工作
3. **无回归**: 现有功能未被破坏
4. **单元测试通过**: 测试必须通过（除非用户明确允许跳过）

可以询问用户：
- "功能是否已经实现完成？"
- "单元测试是否全部通过？"
- "是否允许跳过测试？（不推荐）"

### 6. 更新 feature 状态

对于要完成的 feature：
- 设置 `status: "completed"`
- 只有测试通过才设置 `passes: true`
- 记录完成时间（可选）

### 7. 更新进度日志

在 claude-progress.txt 中添加记录：

```
## 2026-02-14
- Completed: feat-001 - 功能描述 (测试通过)
```

### 8. Git 提交

```bash
git add feature_list.json claude-progress.txt
git commit -m "Complete: feat-001 - feature description"
```

## 输出

显示已完成的 feature：
- Feature ID
- 描述
- 下一个建议的 feature（如果有）
