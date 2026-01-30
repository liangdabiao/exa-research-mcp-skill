# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code project for AI-powered company and market research using Exa's advanced web search capabilities. The project is not a traditional software application but rather a specialized research tool built on Claude Code's skill and agent system.

## Architecture

The system uses an agent-based architecture with strict context isolation:

```
User Request → Company Research Skill → Task Agent → Exa Search → Distilled Output → User
```

### Key Components

- **Skills System**: Located in `.claude/skills/`. Each skill defines specialized research capabilities with strict rules about tool usage and execution patterns.
- **MCP Integration**: Uses Exa's Model Context Protocol server for advanced web search (`mcp__exa__web_search_advanced_exa`).
- **Task Agents**: All search operations run in isolated task contexts to prevent token pollution in the main conversation.

### Current Skills

**company-research** (`.claude/skills/company-research/SKILL.md`):
- Company intelligence, competitor analysis, market research
- Finds company info, news, tweets, financials, LinkedIn profiles
- Exa categories: `company`, `news`, `tweet`, `people`

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

## Configuration

**`.claude/settings.local.json`** controls MCP permissions:
```json
{
  "permissions": {
    "allow": ["mcp__exa__web_search_advanced_exa"]
  }
}
```

To add new MCP tools, add them to the `allow` list. This is a security-conscious approach to limit API surface.

## Model Selection

- **haiku**: Fast extraction tasks (listing, discovery)
- **opus**: Synthesis, analysis, browser automation

## Skill Development

To create a new skill:

1. Create a new directory in `.claude/skills/<skill-name>/`
2. Create a `SKILL.md` file with the following frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What the skill does
   triggers: comma, separated, phrases, that, invoke, the skill
   requires_mcp: mcp-server-name
   context: fork
   ---
   ```
3. Document the skill's rules, constraints, and execution patterns

## Research Outputs

Research results are typically saved as `.md` files in the project root (e.g., `cnc切割行业industry.md` contains a CNC industry market analysis).
