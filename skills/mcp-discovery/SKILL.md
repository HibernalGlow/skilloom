---
name: mcp-discovery
description: Find the user's canonical MCP server table at ~/.mcp.json before installing, adding, or configuring any MCP server. Use when a task needs an MCP tool, when no already-loaded server fits, or when the user mentions MCP config/servers. Discovers and reuses; never creates a competing configuration.
---

# MCP discovery

`~/.mcp.json` is this user's canonical MCP inventory: the list of servers that exist and how to launch them. It is a registry, not a loader — reading it does not make a server available.

## Procedure

1. Read `~/.mcp.json` and take its `mcpServers` as the inventory.
2. List what this harness actually loaded (e.g. `mcp_list`). Match by name, then by command+args — the same server can be registered under a different key.
3. Loaded → use it. Never reinstall, re-register, or "repair" a server that already works.
4. In the registry but not loaded → this harness does not read `~/.mcp.json`. Say so, name the file it does read (table below), and offer to project that one entry there. Write only on explicit agreement, and tell the user a restart/reload is needed for it to appear.
5. Not in the registry at all → `~/.mcp.json` is where the new entry goes first; project afterwards.
6. Never add a third config file, a wrapper, a shim, or a per-project copy as a workaround. One registry plus each harness's own projection.

## Where each harness reads MCP config

| consumer | file | key |
|---|---|---|
| Qoder CLI | `~/.qoder-cn/settings.json` | `mcpServers` |
| Qoder IDE | `~/.qoder/mcp.json` | `mcpServers` |
| Claude Code | `~/.claude.json` | `mcpServers` |
| Codex CLI | `~/.codex/config.toml` | `[mcp_servers.<name>]` |

Unlisted harness: read its documented MCP file rather than guessing, and say which one you used.

## Secret handling

`~/.mcp.json` keeps live API keys in `env`. Use them only to launch a server. Never paste `env` values into chat, logs, commits, or another config file; when describing a server, name it and its command and leave `env` out.
