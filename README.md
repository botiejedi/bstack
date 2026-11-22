# bstack

My agent skills, published the way I use them day to day. They work in Claude Code and Codex, and in any agent that reads `SKILL.md` folders.

## Install

Copy any skill folder into your agent's skills directory:

```bash
git clone https://github.com/botiejedi/bstack.git
cp -R bstack/skills/board ~/.claude/skills/      # Claude Code
cp -R bstack/skills/board ~/.agents/skills/      # Codex
```

Many skills expect a local tool or MCP server (for example the Apple skills use the `apple-events`, `apple-mail` and `apple-notes` MCPs). Each `SKILL.md` lists what it needs. Vault skills ship with a **Vault layout (configurable)** table: change the folder names to match your own Obsidian vault.

## Skills

### Thinking and decisions
| Skill | What it does |
| --- | --- |
| `board` | Puts a decision, plan or draft before 3 or 5 frontier models that score it, peer-review and vote |
| `grill` | Interviews you when a request is vague, before any work starts |
| `yap` | Turns rambling into a clear agent prompt or brief |
| `prompt-agent` / `prompt-agent-haiku` | Compiles rough input into a ready-to-paste Claude Code or Cowork prompt |
| `reporpoise` / `reporpoise-review` | Finds existing projects to reuse before you build, then vets a candidate |

### Research
| Skill | What it does |
| --- | --- |
| `deep-research-orchestration` | Scopes and routes multi-domain research with evidence |
| `service-business-market-research` | Researches a local service business: territory, pricing, competitors |
| `storm-watch` | Monitors official storm alerts with confirmed watch rules |
| `firecrawl` | Scrapes, crawls and maps sites, including JS-rendered pages and PDFs |

### Obsidian vault workflow
| Skill | What it does |
| --- | --- |
| `blurb` | Routes a braindump into organized notes |
| `clip` | Saves a conversation snapshot with a summary and links |
| `grab` | Pulls vault context into the conversation |
| `stash` | Pushes insights and decisions from the conversation into the vault |
| `scout` | Queues or runs topic research and writes a brief |
| `garden` | Report-only vault health check (broken links, frontmatter gaps, inbox age) |

### Agent operations
| Skill | What it does |
| --- | --- |
| `handoff` | Checkpoints progress before compaction or the end of a session |
| `agent-context-management` | Strategies for long context windows |
| `central-skill-registry` / `cross-agent-skill-distribution` | Keeps one skill library in sync across agents and verifies it |
| `mods` | Recommends Claude Code plugins and writes usage guides |
| `rule` | Toggles Claude Code state via `/rule <subcommand>` |
| `ntfy` | Sends phone notifications through ntfy when something finishes |

### macOS apps
`apple-calendar`, `apple-mail`, `apple-messages`, `apple-notes`, `apple-reminders`

### Game servers
`pelican`, `pelican-deploy`, `pelican-servers`, `pelican-upgrade`: run, deploy and upgrade a [Pelican](https://pelican.dev) panel and its Wings nodes.

### Vendored from other authors
`impeccable`, `last30days`, `skill-creator`, `defuddle`, `json-canvas`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown`. See [THIRD_PARTY.md](THIRD_PARTY.md) for sources and licences.

## Licence

My own skills are MIT ([LICENSE](LICENSE)). Vendored skills keep their original licences.
