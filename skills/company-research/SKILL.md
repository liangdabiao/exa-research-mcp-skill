---
name: company-research
description: Company, competitor, and market intelligence research using Exa or an equivalent web-search/MCP tool. Use for requests to research a company, build competitor lists, find company news, summarize financial/funding/headcount/location facts, discover public LinkedIn/people profiles, or produce cited market landscape briefs in Codex, OpenClaw, and other SKILL.md-compatible agents.
---

# Company Research

## Core Rules

- Prefer Exa advanced web search when available. In Claude this is commonly `mcp__exa__web_search_advanced_exa`; in Codex/OpenClaw use the configured Exa MCP search tool or the host's web-search tool.
- Do not use weaker/basic Exa search tools when an advanced Exa search tool is available.
- Keep raw search noise out of the final answer. Work from distilled notes, merged entities, and citations.
- Use independent research passes only when the host supports them and the user/task policy allows them; otherwise run compact searches sequentially and summarize after each batch.
- Cite primary or high-quality sources for factual claims, especially current facts such as funding, revenue, executives, headcount, product launches, and pricing.

## Research Workflow

1. **Clarify scope if needed**
   - Identify target company, geography, sector, time horizon, and requested depth.
   - If the user gives an ambiguous quantity, ask for the desired number of companies or choose a reasonable default and state it.

2. **Plan query variants**
   - Generate 2-3 phrasings per topic to improve coverage.
   - Include local-language terms for non-English markets.
   - Mix source intents: official company pages, news, databases, social profiles, and analyst/industry sources.

3. **Run focused searches**
   - Use `company` category for homepages and metadata when Exa supports categories.
   - Use `news` for press coverage, launches, funding, earnings, partnerships, and recent events.
   - Use `people` for public LinkedIn-style profiles and leadership discovery.
   - Use `tweet` or social search only for brand/social presence when relevant.

4. **Merge and deduplicate**
   - Normalize company names, domains, subsidiaries, and brands.
   - Separate confirmed facts from inference.
   - Flag uncertain or conflicting data instead of silently choosing one source.

5. **Synthesize output**
   - Produce the format the user asked for: brief, table, competitor map, JSON, or full report.
   - Include citations next to key claims.
   - End with gaps, assumptions, and recommended follow-up searches when evidence is incomplete.

## Dynamic Search Depth

- "A few" / quick scan: 10-20 results total.
- Standard competitor/company brief: 20-50 results total.
- Comprehensive landscape: 50-100 results total across variants.
- User-specified number: match the requested number.
- If the search budget is constrained, prioritize official sites and recent reputable sources.

## Output Patterns

### Company Brief

Use this structure for single-company research:

```markdown
## Company Snapshot
| Field | Finding | Sources |
|---|---|---|
| Legal/brand name | ... | ... |
| Website | ... | ... |
| HQ / locations | ... | ... |
| Employees / scale | ... | ... |
| Funding / revenue | ... | ... |
| Products | ... | ... |

## Recent Signals
- ...

## Competitors
| Company | Why comparable | Differentiator | Source |
|---|---|---|---|

## Risks / Unknowns
- ...
```

### Competitor List

Use this structure for market discovery:

```markdown
| # | Company | Website | Category | Geography | Evidence | Confidence |
|---|---|---|---|---|---|---|
```

Confidence levels:
- **High**: official website plus an independent source.
- **Medium**: one strong source or multiple weaker sources.
- **Low**: partial match, outdated page, or inferred relevance.

## Browser / Direct Page Fallback

Use Chrome MCP as the preferred browser fallback when the user has configured and sanitized it. Use browser or direct page access when:

- Search snippets are insufficient.
- Pages require JavaScript rendering.
- Pricing, product catalogs, or reviews must be verified directly.
- A source appears contradictory and needs manual inspection.

When using Chrome MCP, behave like a careful human browser user: record only distilled facts, page title, URL, publisher, accessed date, and confidence; do not persist cookies, credentials, private account data, or unrelated browsing history.
