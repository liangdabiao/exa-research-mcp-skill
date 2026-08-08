# /harness-init 命令

## 功能

初始化一个新的开发项目，创建完整的框架结构。

## 执行步骤

### 1. 检查当前目录状态

```bash
ls -la
```

确认这是一个新项目目录（没有 feature_list.json）。

### 2. 收集项目信息

使用 AskUserQuestion 询问：
- 项目名称
- 开发服务器启动命令（如 `npm run dev`、`python manage.py runserver` 等）
- 测试命令（如 `npm test`、`pytest` 等）
- 项目描述（可选）

### 3. 创建 init.sh 脚本

创建 `init.sh` 文件，包含用户提供的启动命令：

```bash
#!/bin/bash
# 项目启动脚本
npm run dev
```

确保脚本可执行：
```bash
chmod +x init.sh
```

### 4. 初始化 Git 仓库

如果尚未初始化 Git：

```bash
git init
git add .
git commit -m "Initial commit: project initialization"
```

### 5. 创建 feature_list.json

```json
{
  "version": "1.0",
  "project": "项目名称",
  "created": "2026-02-14",
  "features": []
}
```

### 6. 创建 claude-progress.txt

```
# Claude Progress Log

## Project: 项目名称
Created: 2026-02-14

## History
- 2026-02-14: Project initialized
```

### 7. 创建代码规范文件 (CODING_STANDARDS.md)

创建 `CODING_STANDARDS.md` 文件，包含项目的代码规范：

```markdown
# 代码规范

## 1. 代码风格

- 遵循项目默认的代码风格
- 使用 ESLint/Prettier 进行代码格式化
- 保持代码简洁、可读

## 2. 命名规范

- 变量/函数: camelCase
- 常量: UPPER_SNAKE_CASE
- 组件/类: PascalCase
- 文件: kebab-case

## 3. Git 提交规范

- 使用 Conventional Commits 格式
- feat: 新功能
- fix: Bug 修复
- refactor: 重构
- docs: 文档更新
- test: 测试相关
- chore: 维护任务

## 4. 测试要求

- 每个功能必须有对应的单元测试
- 测试覆盖率目标: > 80%
- 运行测试: npm test

## 5. 代码审查

- 提交前自检
- 确保无 console.log/debugger
- 确保无未使用的变量
```

### 8. 提交初始文件

```bash
git add .
git commit -m "Add: effective-harnesses framework files"
```

## 输出

完成初始化后，显示：
- 创建的文件列表
- 下一步建议（添加第一个 feature）
