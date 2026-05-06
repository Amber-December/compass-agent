# Errors

## [ERR-20260505-001] lark-cli auth login

**Logged**: 2026-05-05T20:30:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: config

### Summary
lark-cli auth login TUI 交互卡住，无法通过 send-keys 完成选择

### Error
TUI 显示业务域选择界面，发送 'a' 和 'Enter' 键无响应

### Context
- 命令: lark-cli auth login --domain base
- 环境: OpenClaw exec with pty=true
- 问题: TUI 多选列表交互在自动化环境下不稳定

### Suggested Fix
使用 --profile 参数直接指定预配置的应用身份，避免交互式登录

### Resolution
- **Resolved**: 2026-05-05T21:46:00+08:00
- **方法**: 使用 lark-cli auth login --domain base --profile compass
- **Notes**: 司南应用已有预配置，直接切换 profile 即可

---

## [ERR-20260505-002] wiki_ingest.py regex

**Logged**: 2026-05-05T22:08:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
正则表达式匹配时未检查 group(1) 是否为 None，导致 AttributeError

### Error
AttributeError: 'NoneType' object has no attribute 'strip'

### Context
- 文件: agents/wiki-manager/tools/wiki_ingest.py
- 函数: extract_entities()
- 问题: match.group(1) 可能为 None，直接调用 .strip() 报错

### Suggested Fix
所有正则匹配后检查 group 是否存在再处理

### Resolution
- **Resolved**: 2026-05-05T22:10:00+08:00
- **方法**: 添加 if name: 检查
- **Notes**: 共修复 3 处类似问题

---
