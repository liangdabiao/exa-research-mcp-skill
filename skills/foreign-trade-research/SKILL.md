---
name: foreign-trade-research
description: Deep foreign-trade and overseas market-entry research for a target country plus product/category. Use for Chinese exporters, manufacturers, and cross-border teams that need competitor landscapes, local brands, manufacturers, distributors/importers, pricing, channels, market gaps, risks, and a cited Chinese business report. Portable across Codex, OpenClaw, Claude Code, and other SKILL.md-compatible agents.
---

# Foreign Trade Research

## Core Rules

- Prefer Exa advanced web search when available; otherwise use the best configured web-search/MCP tool in the host agent.
- Search in English plus the target market's local language when possible.
- Keep evidence traceable: cite official sites, marketplaces, company databases, regulator/import records, credible news, and review/social platforms.
- Distinguish verified facts from estimates and strategic inference.
- If the user asks to exclude Chinese companies, explicitly filter them during search and mark any unavoidable Chinese-owned subsidiaries.

## Five-Step Workflow

### 1. Identify the Competitive Landscape

Build a TOP20 market map for the target country and product:

- **Local or market-facing brands**: TOP7 companies with visible branded products.
- **Manufacturers**: TOP7 local factories or international manufacturers with local production/distribution.
- **Distributors / wholesalers / importers**: TOP6 major channel players.

For each company capture: full name, website, HQ/location, role, market position, and evidence.

Search patterns:

```text
[target country] [product] leading companies manufacturers brands 2026
best [product] brands in [target country] distributors importers
[target country local-language product term] manufacturer distributor retailer
site:. [target country TLD] [product] supplier distributor
```

### 2. Deep-Dive Each Competitor

For each prioritized company, extract:

1. Company background: size, history, ownership, subsidiaries, locations.
2. Product lines: models/SKUs, technical claims, certifications, differentiators.
3. Pricing strategy: premium/mid/economy positioning, listed prices, promos, MOQ if available.
4. Customers/channels: B2B/B2C, ecommerce, distributors, dealers, sectors served.
5. Strengths/weaknesses: evidence-based advantages, gaps, complaints, unmet needs.

Use official websites first, then marketplaces, news, social, reviews, and trade databases.

### 3. Build a Comparison Matrix

Create a table with:

```markdown
| Company | Role | Market position | Core products | Price band | Channels/customers | Strengths | Weaknesses | Sources |
|---|---|---|---|---|---|---|---|---|
```

Then analyze:

- Is the market monopolistic, oligopolistic, or fragmented?
- Which players are the most threatening competitors?
- Where are the product, price, channel, or service gaps?
- What entry points are realistic for Chinese suppliers?

### 4. Cross-Validate Key Data

Validate important claims across multiple source types:

- Official company/product pages for identity and product claims.
- Ecommerce/B2B marketplaces for price, assortment, sales signals, and reviews.
- Local news and trade media for launches, partnerships, expansion, and regulation.
- Social/professional pages for activity, headcount signals, and decision makers.
- Customer review sites and forums for complaints and unmet demand.

When sources conflict, show the conflict and assign confidence instead of hiding uncertainty.

### 5. Write the Final Report

Default report structure in Chinese:

```markdown
# [目标国]_[产品/品类]_市场调研报告

## 一、执行摘要
- 核心发现（3-5条）
- 市场机会评级（高/中/低）与理由

## 二、市场概述
1. 市场规模与增长趋势（注明年份和来源）
2. 需求驱动因素与主要挑战
3. 竞争格局总览

## 三、主要品牌商分析（TOP7）

## 四、主要制造商分析（TOP7）

## 五、主要经销商/进口商分析（TOP6）

## 六、竞争格局深度分析
1. 市场份额或影响力估算
2. 价格竞争
3. 渠道竞争
4. 产品/技术竞争
5. 市场空白点

## 七、中国供应商进入机会与建议
1. 市场切入点
2. 产品定位
3. 定价策略
4. 渠道策略
5. 本地化与认证建议

## 八、风险提示
- 政策/认证/关税风险
- 汇率/物流/售后风险
- 竞争与合规风险

## 九、资料来源与置信度说明
```

Report requirements:

- Default length: 5,000-8,000 Chinese characters unless the user requests otherwise.
- Save to `[目标国]_[产品]_市场调研报告.md` when working in a repository or workspace and the user expects a file.
- Use citations inline for key numbers, company claims, and current events.
- Preserve original English/local company names and technical terms where useful.

## Search Depth

- Quick scan: landscape 20-30 results; company deep dives 5-10 results each for priority players.
- Standard report: landscape 30-50 results; company deep dives 10-25 results each.
- Comprehensive report: landscape 50-100 results; company deep dives 25-50 results each.
- For tight time budgets, reduce company count before reducing citation quality.

## Chrome MCP / Browser Fallback

Use Chrome MCP as the preferred fallback when Exa/search results are insufficient and the user has configured/sanitized Chrome MCP. It is appropriate for official websites, dynamic pages, ecommerce listings, review pages, PDF downloads, maps, or source verification that needs a real browser.

Store only distilled evidence in the report or JSON notes: source title, URL, publisher/platform, accessed date, key facts, and confidence. Do not store cookies, credentials, account identifiers, private profile data, or unrelated browsing history.
