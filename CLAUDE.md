# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains both legacy Claude Code skills and portable Codex/OpenClaw-compatible `SKILL.md` skills for AI-powered company and market research using Exa's advanced web search capabilities. The project is not a traditional software application but rather a specialized research tool built around reusable agent skills and research workflows.

## Architecture

The system uses an agent-based architecture with strict context isolation:

```
User Request → Company Research Skill → Task Agent → Exa Search → Distilled Output → User
```

### Key Components

- **Skills System**: Portable skills live in `skills/` for Codex/OpenClaw-compatible agents. Legacy Claude Code skills remain in `.claude/skills/`. Each skill defines specialized research capabilities with strict rules about evidence, tool usage, and execution patterns.
- **MCP Integration**: Uses Exa's Model Context Protocol server for advanced web search (`mcp__exa__web_search_advanced_exa`).
- **Task Agents**: All search operations run in isolated task contexts to prevent token pollution in the main conversation.

### Current Skills

Portable Codex/OpenClaw skills live under `skills/<skill-name>/SKILL.md`; Claude Code legacy copies live under `.claude/skills/<skill-name>/SKILL.md`.

**company-research** (`skills/company-research/SKILL.md`, legacy `.claude/skills/company-research/SKILL.md`):
- Company intelligence, competitor analysis, market research
- Finds company info, news, tweets, financials, LinkedIn profiles
- Exa categories: `company`, `news`, `tweet`, `people`

**foreign-trade-research** (`skills/foreign-trade-research/SKILL.md`, legacy `.claude/skills/foreign-trade-research/SKILL.md`):
- 深度外贸市场调研，针对目标国家+产品领域进行全面竞争对手分析
- 5步法：竞争格局识别 → 竞品深度拆解 → 对比矩阵 → 多源验证 → 报告生成
- 覆盖品牌商（TOP7）、制造商（TOP7）、经销商（TOP6）
- 输出完整调研报告（5000-8000字），含中国供应商进入策略建议
- Exa categories: `company`, `news`, `tweet`, `people`

**renewable-market-research** (`skills/renewable-market-research/SKILL.md`):
- 任意国家 + 任意新能源技术市场情报采集
- effective-harnesses 文件模式：子任务写 `data/renewable-market/depth/*.json`，主会话汇总 JSON/CSV/index
- 输出完整版与交付版 MD/PDF 报告
- 覆盖项目管道、政策、开发商、融资、技术/EPC、环境、碳市场/绿氢、中国企业机会

## Critical Skill Constraints

When working with or modifying skills, follow these rules:

1. **Tool Restriction**: Only use `web_search_advanced` from Exa. Never use `web_search_exa` or other Exa tools.

2. **Token Isolation**: Never run Exa searches in the main context. Always spawn Task agents to:
   - Run Exa searches internally
   - Process results using LLM intelligence
   - Return only distilled output (compact JSON or brief markdown)

3. **Dynamic Tuning**: Don't hardcode `numResults`. Scale based on user intent:
   - "a few" → 10-20 results
   - "comprehensive" → 50-100 results
   - User specifies → match exactly
   - Ambiguous → ask for clarification

4. **Query Variation**: Generate 2-3 query variations and run in parallel for better coverage.

5. **Exa Categories**:
   - `company` - homepages with metadata (headcount, location, funding, revenue)
   - `news` - press coverage
   - `tweet` - social presence
   - `people` - public LinkedIn profiles

6. **Browser Fallback**: Use Claude in Chrome when:
   - Exa returns insufficient results
   - Content is auth-gated
   - Dynamic pages need JavaScript

## Windows native and browser fallback

- Portable skills should work on Windows native. Prefer PowerShell (`.ps1`) or Python (`.py`) startup/validation scripts over Bash-only `make.sh` workflows.
- Chrome-mcp may be used as a sanitized human-browser fallback in addition to Exa for dynamic pages, source verification, PDF downloads, ecommerce pages, maps, and tables. Store only distilled source evidence.

## Configuration

**`.claude/settings.local.json`** controls MCP and shell permissions. It now allows Exa, sanitized Chrome MCP tool patterns, and Windows-native PowerShell/Python command entry points:
```json
{
  "permissions": {
    "allow": [
      "mcp__exa__web_search_advanced_exa",
      "mcp__chrome-mcp__*",
      "mcp__chrome__*",
      "Bash(pwsh *)",
      "Bash(powershell *)",
      "Bash(py *)",
      "Bash(python *)"
    ]
  }
}
```

To add new MCP tools, add them to the `allow` list. This is a security-conscious approach to limit API surface. Chrome MCP naming varies by installation, so keep both `mcp__chrome-mcp__*` and `mcp__chrome__*` patterns only when the user has configured a sanitized browser profile.

## Model Selection

- **haiku**: Fast extraction tasks (listing, discovery)
- **opus**: Synthesis, analysis, browser automation

## Skill Development

For cross-agent skills, create or update `skills/<skill-name>/SKILL.md` and keep YAML frontmatter limited to `name` and `description`. Put Codex UI metadata in `skills/<skill-name>/agents/openai.yaml`. Avoid Claude-only fields such as `triggers`, `requires_mcp`, `context`, or `allowed-tools` in portable skills.

For Claude Code-only compatibility copies, keep using `.claude/skills/<skill-name>/SKILL.md` if needed. Document each skill's rules, constraints, and execution patterns.

## Research Outputs

Research results are typically saved as `.md` files in the project root (e.g., `cnc切割行业industry.md` contains a CNC industry market analysis).
