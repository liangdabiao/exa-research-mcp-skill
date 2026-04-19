---
name: foreign-trade-research
description: 深度外贸市场调研技能。对目标国家+产品领域进行全面竞争对手分析，覆盖品牌商、制造商、经销商，生成含市场格局、定价策略、渠道分析和进入建议的完整调研报告。
triggers: 外贸市场调研, 外贸调研, 市场调研, 海外市场分析, 竞争对手分析, 目标国市场调研, 外贸市场分析, trade market research, market entry research, competitor landscape, foreign trade analysis
requires_mcp: exa
context: fork
---

# 外贸市场深度调研

## Tool Restriction (Critical)

ONLY use `web_search_advanced_exa` from Exa. Do NOT use `web_search_exa` or any other Exa tools.

## Token Isolation (Critical)

Never run Exa searches in main context. Always spawn Task agents:

- Agent runs Exa search internally
- Agent processes results using LLM intelligence
- Agent returns only distilled output (compact JSON or brief markdown)
- Main context stays clean regardless of search volume

## 调研流程（5步法）

整个调研按以下5步执行，每步使用独立的 Task Agent：

### 第1步：识别行业竞争格局

生成该市场 TOP20 活跃公司名单，分为三类：
- **本土品牌商**（TOP7）：拥有自有品牌的公司
- **制造商**（TOP7）：本土制造商 + 在当地有生产基地的国际制造商
- **主要经销商/批发商/进口商**（TOP6）

每家公司需包含：公司全称、成立时间、总部所在地、官方网站、市场地位。

**搜索策略**：
- 查询变体示例（目标国=Thailand，产品=solar panels）：
  - `Thailand solar panels leading companies manufacturers brands 2025 2026`
  - `top solar panel companies Thailand market share distributors`
  - `Thailand solar energy industry key players importers wholesalers`
- 使用 `company` category 搜索公司主页和元数据
- 使用 `news` category 获取最新行业动态
- numResults: 30-50 per query, 2-3 queries in parallel

**输出格式**：结构化 markdown，三类分组，每家公司一行摘要。

### 第2步：逐个深度拆解竞品

对第1步识别出的每家公司进行深度分析，覆盖维度：

1. **公司背景**：员工人数、年营业额、发展历史和重要里程碑、主要股东和子公司
2. **核心产品线**：该产品领域的主要产品系列、产品特点和技术优势、最新产品发布
3. **定价策略**：价格区间（高端/中端/经济型）、与竞争对手价格对比、促销策略
4. **主要客户群体**：目标客户类型、主要销售渠道、重点服务的行业和地区
5. **竞争优劣势**：核心竞争力、存在的弱点和市场空白

**搜索策略**：
- 每家公司独立搜索，查询变体：
  - `[Company Name] [product] Thailand company profile revenue employees`
  - `[Company Name] products pricing strategy customers`
  - `[Company Name] [product] competitors advantages disadvantages`
- 使用 `company` category 获取公司元数据
- 使用 `news` category 获取最新动态和财报信息
- 使用 `tweet` category 获取社交媒体动态
- numResults: 15-25 per company, 可并行处理多家公司

**输出格式**：每家公司一段结构化分析，标注信息来源。

### 第3步：生成竞争对手对比矩阵

汇总所有公司信息，生成横向对比矩阵：

对比维度：公司名称、市场地位、核心产品线、价格定位、主要客户群体、核心优势、主要劣势

然后回答：
1. 目前市场的竞争格局是怎样的？（垄断/寡头/碎片化）
2. 哪些公司是最主要的竞争对手？
3. 市场上存在哪些未被满足的需求和空白点？
4. 对于中国供应商，有哪些潜在的市场切入点？

**输出格式**：markdown 表格 + 分析文本。

### 第4步：多源数据验证

对关键数据点进行交叉验证：

- 官网验证：访问竞争对手官网核对产品信息和公司介绍
- 电商平台验证：Amazon、eBay、当地 B2B 平台查看产品价格和销量
- 社交媒体验证：LinkedIn、Facebook、Instagram 查看最新动态
- 客户反馈验证：Trustpilot、Google Reviews 查看用户评价

**搜索策略**：
- 查询变体：
  - `[Company Name] site:amazon.com [product]`
  - `[Company Name] reviews rating Trustpilot`
  - `[Company Name] LinkedIn employees`
- 可使用 `includeDomains` 过滤特定平台
- numResults: 10-15 per query

**浏览器回退**：当 Exa 结果不足时，使用 Playwright 浏览器直接访问页面。

### 第5步：生成最终调研报告

整合所有信息，生成完整的市场调研报告。

**报告结构**：

```
一、执行摘要
   - 核心发现（3-5条）
   - 市场机会评级

二、市场概述
   1. 市场规模和增长趋势（2025-2026）
   2. 主要驱动因素和挑战
   3. 市场竞争格局总览

三、主要品牌商分析（TOP7）

四、主要制造商分析（TOP7）

五、主要经销商分析（TOP6）

六、竞争格局深度分析
   1. 各公司市场份额估算
   2. 价格竞争分析
   3. 渠道竞争分析
   4. 技术竞争分析

七、中国供应商进入机会与建议
   1. 市场切入点
   2. 产品定位建议
   3. 定价策略建议
   4. 渠道策略建议

八、风险提示
```

**报告要求**：
- 数据准确，注明来源
- 逻辑清晰，结构完整
- 语言专业，适合商务使用
- 总字数 5000-8000 字
- 以 `.md` 文件保存到项目根目录，命名规则：`[目标国]_[产品]_市场调研报告.md`

## Query Variation

Exa 返回不同查询的结果不同。为了更广泛的覆盖：

- 生成 2-3 个查询变体
- 并行运行
- 合并并去重
- 覆盖英文和当地语言关键词

## Categories

根据调研阶段使用适当的 Exa 类别：

- `company` → 公司主页，大量元数据（员工人数、地点、融资、收入）
- `news` → 新闻报道，获取最新市场动态和财报
- `tweet` → 社交媒体存在，了解品牌声量
- `people` → 公开 LinkedIn 个人资料，获取公司高管和关键决策人信息

## Dynamic Tuning

不要硬编码 numResults。根据用户意图调整：

- "快速了解" → 第1步 20-30 results，第2步 10-15 results/company
- "标准调研" → 第1步 30-50 results，第2步 15-25 results/company
- "全面深度" → 第1步 50-100 results，第2步 25-50 results/company
- 用户指定数量 → 精确匹配
- 模糊？询问："您需要什么深度？快速了解 / 标准调研 / 全面深度"

## 排除中国公司

在搜索查询中，当用户要求排除中国公司时，添加 `exclude China Chinese` 等排除词，使用 `excludeText: ["China", "Chinese", "中国"]` 参数。

## Browser Fallback

自动回退到 Playwright 浏览器：

- Exa 返回结果不足
- 内容需要认证
- 动态页面需要 JavaScript 渲染
- 需要验证电商平台价格和库存

## Models

- `haiku`：快速提取任务（公司列表发现、基础信息收集）
- `opus`：综合分析、对比矩阵生成、最终报告撰写、浏览器自动化

## 语言

报告默认使用中文撰写。当目标市场为英语国家时，公司名称和技术术语保留英文原文。

## 输出保存

调研报告保存到项目根目录，文件名格式：`[目标国]_[产品]_市场调研报告.md`

例如：`泰国_太阳能板_市场调研报告.md`、`巴西_电子产品_市场调研报告.md`
