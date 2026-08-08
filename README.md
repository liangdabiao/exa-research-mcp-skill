# Exa Research MCP Skills

面向 **Codex、OpenClaw、Claude Code** 等 `SKILL.md` 兼容智能体的 Exa 企业与市场研究技能包。

本仓库最初基于 Claude Code + Exa MCP 构建，现在新增了可移植的 `skills/` 目录：每个技能都使用标准 `SKILL.md`（仅 `name` + `description` frontmatter）和可选的 `agents/openai.yaml`，便于 Codex/OpenAI 界面识别，也便于 OpenClaw 按技能目录加载。

## 项目定位

这不是传统软件应用，而是一组可复用研究工作流：通过 Exa 高级搜索、网页检索和智能体分析，完成公司情报、竞争对手分析、外贸市场调研，以及长任务进度追踪。

核心目标：

- **跨智能体复用**：同一套技能可复制到 Codex、OpenClaw、Claude Code 或其他支持 `SKILL.md` 的代理环境。
- **研究可追溯**：输出报告要求保留来源、区分事实与推断、标注不确定性。
- **上下文节省**：搜索结果先提炼再综合，避免把大量原始网页噪声塞入主对话。
- **长任务可恢复**：通过 `feature_list.json` / `agent-progress.md` 等文件记录阶段成果。

## 目录结构

```text
.
├── skills/                         # Codex/OpenClaw 可移植技能
│   ├── company-research/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── foreign-trade-research/
│   │   ├── SKILL.md
│   │   └── agents/openai.yaml
│   ├── renewable-market-research/
│   │   ├── SKILL.md
│   │   ├── references/
│   │   ├── scripts/
│   │   └── agents/openai.yaml
│   └── effective-harnesses/
│       ├── SKILL.md
│       └── agents/openai.yaml
├── .claude/skills/                 # 原 Claude Code 技能，保留兼容
├── research-output/                # 示例研究报告
├── feature_list.json               # 长任务/研究 feature 追踪示例
├── AGENTS.md                       # Codex/OpenClaw 读项目时的仓库级说明
└── CLAUDE.md                       # Claude Code 仓库级说明
```

## 技能列表

### `company-research`

用于公司情报、竞争对手分析、公司列表发现、市场格局速览。

适合请求：

- “研究一下 Tesla 的竞争对手”
- “帮我找到东南亚做仓储机器人的公司”
- “分析某公司的融资、营收、员工规模、新闻动态”

输出可为公司快照、竞争对手表格、市场简报或带来源的结构化 JSON。

### `foreign-trade-research`

用于“目标国家 + 产品/品类”的外贸市场深度调研，尤其适合中国出口商、制造商、跨境团队。

默认五步法：

1. 识别目标市场 TOP20 公司（品牌商 7 + 制造商 7 + 经销商/进口商 6）
2. 逐个拆解竞品背景、产品线、价格、渠道、客户、优劣势
3. 生成竞争对手对比矩阵与市场空白分析
4. 多源验证官网、电商、新闻、社交媒体、评论数据
5. 输出 5000-8000 字中文商务报告

### `renewable-market-research`

用于“任意国家 + 任意新能源技术”的深度市场情报采集，采用 effective-harnesses 风格的文件模式：多维度搜索写入 `data/renewable-market/depth/*.json`，主会话汇总为主 JSON、CSV、index，并输出完整版/交付版两套 MD/PDF 报告。

适合请求：

- “帮我调研乌兹别克斯坦风电市场，输出完整版和交付版报告”
- “调研沙特储能项目管道、融资和中国企业机会”
- “更新越南光伏市场数据，基于已有 JSON 做增量采集”

#### 推荐使用方式：bounded dynamic frontier

在 Codex/OpenClaw 中直接点名或触发 `$renewable-market-research`，并给出国家、技术、目标企业/读者、时间窗口和交付物。例如：

```text
使用 $renewable-market-research 调研乌兹别克斯坦风电市场，目标读者是明阳海外销售团队。
采用文件模式，先生成 search plan，再做高召回动态 frontier，最后输出 project ledger、full report、lite report 和销售机会表。
```

当前版本的风电市场研究默认使用两段式：

1. **Recall Mode**：先高召回，不假设项目名、开发商、SPV、OEM、EPC、融资方、法令和地区入口已经完整。搜索过程按 `seed -> search -> extract entities -> enqueue -> search again` 扩展 `search_frontier.json`，至少运行 5 轮。
2. **Bounded Frontier**：高召回不是无限扩展。P0/P1 自动追踪并阻止过早进入 Verification；P2 只做 one-hop；P3 只有影响风电机会才展开；P4 泛能源宏观信息默认 deferred，不进正文。
3. **Verification Mode**：只从 `candidate_project_pool.json` 和去重后的 `{slug}-pipeline-ledger.json` 入账，分类为 operational / financing_closed / under_construction / ppa_signed / decree_backed / mou_or_early_stage / watchlist / duplicate / rejected / unresolved。

如果只想先生成调度契约，可以运行：

```powershell
python .\skills\renewable-market-research\scripts\search_orchestration.py plan `
  --country Uzbekistan `
  --technology wind `
  --audience "Mingyang OEM commercial entry" `
  --official-languages "Uzbek,Russian" `
  --known-projects "Zarafshan,Bash,Dzhankeldy,Nukus,Karatau,Sho'rkul,Nurota" `
  --slug uzbekistan-wind `
  --output .\data\renewable-market\uzbekistan-wind-search-plan.json
```

重点检查这些输出：

- `data/renewable-market/{slug}-seed_entities.json`
- `data/renewable-market/{slug}-search_frontier.json`
- `data/renewable-market/{slug}-discovered_entries.json`
- `data/renewable-market/{slug}-candidate_project_pool.json`
- `data/renewable-market/{slug}-pipeline-ledger.json`
- `data/renewable-market/{slug}-frontier_execution_review.json`
- `data/renewable-market/{slug}-search_coverage_matrix.md`
- `data/renewable-market/{slug}-frontier_convergence.json`
- `data/renewable-market/{slug}-report.md`
- `data/renewable-market/{slug}-lite.md`

进入正式报告前，必须确认：Recall 已完成至少 5 轮；所有 P0/P1 frontier 已搜索、分类或明确 deferred；P0/P1 已有执行/评估分离的 artifact 且 `evaluation_status` 允许入账；历史 baseline seed 没有静默消失；政府/法令、IFI、开发商、OEM/EPC、中文、本地语言权威来源都已尝试；连续两轮没有新增 P0/P1 高价值入口；容量汇总来自 ledger，而不是叙述笔记。

### `effective-harnesses`

用于长时间运行的开发或研究任务管理。

维护这些可恢复文件：

- `feature_list.json`：功能/研究任务清单、优先级、测试状态
- `agent-progress.md`：进度日志、决策、阻塞、下一步
- `init.sh`：可选启动脚本
- `CODING_STANDARDS.md`：可选项目规范

## 安装到 Codex

把需要的技能目录复制或软链接到 Codex 技能目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/company-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/foreign-trade-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/renewable-market-research "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/effective-harnesses "${CODEX_HOME:-$HOME/.codex}/skills/"
```

也可以在项目内保留 `skills/`，让支持项目级技能发现的 Codex 环境读取。

## 安装到 OpenClaw

把技能复制到 OpenClaw 的技能目录或工作区技能目录：

```bash
mkdir -p "$HOME/.openclaw/skills"
cp -R skills/company-research "$HOME/.openclaw/skills/"
cp -R skills/foreign-trade-research "$HOME/.openclaw/skills/"
cp -R skills/renewable-market-research "$HOME/.openclaw/skills/"
cp -R skills/effective-harnesses "$HOME/.openclaw/skills/"
```

如果你的 OpenClaw 使用工作区级技能目录，请把 `skills/<skill-name>` 复制到对应 workspace 的 `skills/` 下。

## 配置 Exa MCP

推荐配置 Exa MCP，以获得更好的公司、新闻、人物和网页搜索能力。若你已经配置并脱敏 Chrome-mcp，也可以把它作为真人浏览器 fallback，用于动态网页、PDF 下载、电商页面、地图/表格和人工核验。

### Claude Code 示例

```bash
claude mcp add --transport http exa https://mcp.exa.ai/mcp
```

### Codex / OpenClaw

在宿主工具中添加 Exa MCP server，URL 使用：

```text
https://mcp.exa.ai/mcp
```

不同宿主的 MCP 配置文件位置和命令可能不同；技能中不会硬编码 Claude 专属工具名，而是要求优先使用“当前环境可用的 Exa advanced search / web search MCP 工具”。

## Windows native 使用建议

如果在 Windows native 环境运行，不要假设有 Bash/WSL。优先使用 PowerShell 或 Python：

```powershell
New-Item -ItemType Directory -Force data/renewable-market/depth | Out-Null
py -3 -m json.tool feature_list.json > $env:TEMP\feature_list.validated.json
.\skills\renewable-market-research\scripts\export_projects_csv.ps1 -InputJson .\data\renewable-market\uzbekistan-wind.json -OutputCsv .\data\renewable-market\uzbekistan-wind.csv
```

需要启动项目时，优先提供 `init.ps1` 或 `init.py`；不要强依赖 `make.sh`、`chmod`、`sed/awk` 等 Bash/Unix 工具。

## 使用示例

```text
使用 $company-research 调研 Cursor、Windsurf、Continue 的竞品格局，输出表格并标注来源。
```

```text
使用 $foreign-trade-research 调研巴西太阳能逆变器市场，排除中国公司，输出中文市场进入报告。
```

```text
使用 $renewable-market-research 调研乌兹别克斯坦风电市场，采用文件模式采集，生成完整版和交付版报告。
```

```text
使用 $effective-harnesses + $renewable-market-research + $company-research 调研哈萨克斯坦风电市场（明阳视角），采用多 agent 文件模式；worker 只写各自 depth JSON，主 agent 统一归一化并输出主 JSON/CSV/项目时间轴 CSV/Full+Lite 报告（如环境支持再输出 PDF）。
```

### 可复用的多 Agent 研究骨架（推荐）

针对长周期市场研究，推荐显式声明以下约束：

- 主 agent：初始化 harness、定义 schema、分派模块、归一化合并、生成可读报告与验收。
- worker agent：仅负责自己模块与 `data/renewable-market/depth/*.json` 文件。
- worker 禁止修改：主 JSON、Markdown/PDF、build scripts、harness 文件、其他 worker 的 depth 文件。
- 关键事实字段：`statement`、`sources[]`（含 `url/title/publisher/accessedAt/sourceLanguage/collectionMethod`）、`confidence`、`uncertainty`。
- 项目时间轴字段：`stage/auctionDate/ppaDate/fidDate/constructionStart/codOrTargetCod/timingConfidence/timingUncertainty`。
- 搜索完整性：先用 `skills/renewable-market-research/scripts/search_orchestration.py plan` 生成维度搜索计划，再用 `search_orchestration.py validate` 校验 depth JSON 覆盖率。

推荐验收产物（以哈萨克斯坦风电为例）：

- `data/renewable-market/index.json`
- `data/renewable-market/kazakhstan-wind.json`
- `data/renewable-market/kazakhstan-wind.csv`
- `data/renewable-market/kazakhstan-wind-project-timeline.csv`
- `data/renewable-market/kazakhstan-wind-report.md`
- `data/renewable-market/kazakhstan-wind-lite.md`
- `data/renewable-market/kazakhstan-wind-report.pdf`（环境支持）
- `data/renewable-market/kazakhstan-wind-lite.pdf`（环境支持）

```text
使用 $effective-harnesses 初始化这个研究项目，把任务拆成 6 个 feature 并创建 feature_list.json。
```

## 技能开发约定

- 可移植技能放在 `skills/<skill-name>/SKILL.md`。
- `SKILL.md` frontmatter 仅保留 `name` 和 `description`，提升 Codex/OpenClaw 兼容性。
- Codex UI 元数据放在 `agents/openai.yaml`。
- Claude Code 专属版本继续保留在 `.claude/skills/`，不要依赖它们实现跨平台兼容。
- 研究型技能应保持来源引用、置信度、事实/推断分离。

## 示例研究输出

仓库包含多份历史研究报告，例如：

- 东南亚/巴西/越南等市场中国公司出海业务调研
- 泡泡玛特全球竞争对手深度调研
- 张雪机车（ZXMOTO）海外竞争对手调研
- CNC 切割行业与阿联酋 CNC 产业链分析

这些文件可作为报告结构和分析深度参考，但新研究必须重新检索和验证最新信息。

## 许可

本项目用于合法、授权的企业研究、市场分析、教育和自动化工作流实践。请遵守目标网站条款、数据隐私要求和所在地区法律法规。
