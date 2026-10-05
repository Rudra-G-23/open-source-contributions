
<!-- contributions:begin -->

## 🧑‍💻 Merged Open Source Contributions

**14** merged PRs across **11** repos.

### traccia-ai/traccia-py (3)

| PR | Impact |
| :--- | :--- |
| [#33 feat: Gemini SDK Integration](https://github.com/traccia-ai/traccia-py/pull/33) | Gemini compatibility on traccia platform |
| [#25 docs: add GitHub templates](https://github.com/traccia-ai/traccia-py/pull/25) | Adds bug, feature, and documentation issue templates, so reporters get structured forms instead of a free-form issue and triage stops depending on the reporter knowing what to include |
| [#24 CONTRIBUTING.md formatting fixes](https://github.com/traccia-ai/traccia-py/pull/24) | Repairs CONTRIBUTING.md — working table-of-contents links, a correct LICENSE reference, and issue-reporting steps that no longer render as broken code blocks |

### pytorch/pytorch (2)

| PR | Impact |
| :--- | :--- |
| [#196498 [Dynamo] Port CPython 3.13 test_str to Dynamo test suite](https://github.com/pytorch/pytorch/pull/196498) | Ports CPython 3.13 `test_str` to the Dynamo suite: 135 tests run under Dynamo with the 74 currently-unsupported cases recorded as expected failures, part of the #196238 porting meta-issue |
| [#196482 [Dynamo] Port CPython 3.13 test_grammar to Dynamo test suite](https://github.com/pytorch/pytorch/pull/196482) | Ports CPython 3.13 `test_grammar` to the Dynamo suite with the unsupported cases marked as expected failures, closing one task under the #196238 porting meta-issue |

### AgentPostmortem/Agentrace (1)

| PR | Impact |
| :--- | :--- |
| [#50 feat: detect risky operational verdicts without evidence](https://github.com/AgentPostmortem/Agentrace/pull/50) | Adds the risky_verdict check for unsupported operational recommendations involving destructive or high-impact actions |

### AgentPostmortem/VaultRAG (1)

| PR | Impact |
| :--- | :--- |
| [#30 fix: Search limit validation](https://github.com/AgentPostmortem/VaultRAG/pull/30) | Validate limit and candidates before database access in search(). |

### apache/iggy (1)

| PR | Impact |
| :--- | :--- |
| [#4149 fix(configs): allow sibling IGGY variables](https://github.com/apache/iggy/pull/4149) | Prevents valid sibling variables rejection |

### HelpCode-ai/anythingmcp (1)

| PR | Impact |
| :--- | :--- |
| [#610 feat(mcp): add Airtable read-only adapter](https://github.com/HelpCode-ai/anythingmcp/pull/610) | Adds Airtable as a read-only MCP adapter (base discovery, schemas, records, formula filtering, pagination), so agents can read Airtable data through AnythingMCP without a custom connector |

### kayba-ai/agentic-context-engine (1)

| PR | Impact |
| :--- | :--- |
| [#143 fix: isolate recursive child SkillManager state](https://github.com/kayba-ai/agentic-context-engine/pull/143) | Isolates SkillManager state per recursive child session, so failed or parallel child agents can no longer leak skill mutations back into the parent session |

### lancedb/lancedb (1)

| PR | Impact |
| :--- | :--- |
| [#4211 fix(python): convert objects for JSON fields](https://github.com/lancedb/lancedb/pull/4211) | Python dict/list values now serialize to JSON strings on ingestion, including inside structs and lists, so JSON columns accept nested objects instead of erroring on add and merge_insert |

### sickn33/agentic-awesome-skills (1)

| PR | Impact |
| :--- | :--- |
| [#818 feat: add warehouse skill](https://github.com/sickn33/agentic-awesome-skills/pull/818) | Adds a vendor-neutral warehouse analytics skill scoped to authorized read-only work, with explicit access, privacy, and least-privilege boundaries instead of vendor-specific assumptions |

### systempromptio/awesome-ai-agent-governance (1)

| PR | Impact |
| :--- | :--- |
| [#40 Add Traccia to Audit, Observability, and Cost Control](https://github.com/systempromptio/awesome-ai-agent-governance/pull/40) | Adds Traccia to the governance index's Audit, Observability, and Cost Control section, listing it as an OpenTelemetry-native option alongside the OpenAI Agents, CrewAI, and LangChain integrations |

### traccia-ai/traccia-node (1)

| PR | Impact |
| :--- | :--- |
| [#22 feat: add Gemini auto-instrumentation](https://github.com/traccia-ai/traccia-node/pull/22) | Adds auto-instrumentation for `@google/genai` Interactions calls, and fixes BatchSpanProcessor dropping queued spans on forceFlush/shutdown — spans were being lost whenever an export was already in flight |

<!-- contributions:end -->
