# 부록 F: 엔드투엔드 사례 추적

## 사례 1: 사용자가 파일 수정을 요청한다

```mermaid
flowchart TD
  N1["TUI/App/CLI가 user message 생성"]
  N2["SessionPrompt가 message parts 저장"]
  N1 --> N2
  N3["LLM.stream이 provider 호출"]
  N2 --> N3
  N4["모델이 edit/write/apply_patch 호출"]
  N3 --> N4
  N5["Permission.ask가 diff를 사용자에게 제시"]
  N4 --> N5
  N6["도구가 파일 쓰기와 format/watcher/LSP 갱신"]
  N5 --> N6
  N7["Snapshot/Summary가 diff와 revert 정보를 갱신"]
  N6 --> N7
```

읽을 파일:

- `packages/opencode/src/session/prompt.ts`
- `packages/opencode/src/session/llm.ts`
- `packages/opencode/src/tool/edit.ts`
- `packages/opencode/src/permission/index.ts`
- `packages/opencode/src/snapshot/index.ts`

## 사례 2: 컨텍스트가 넘친다

```mermaid
flowchart TD
  N1["assistant token usage 확인"]
  N2["usable budget 계산"]
  N1 --> N2
  N3["old tool output prune"]
  N2 --> N3
  N4["tail turn 보존"]
  N3 --> N4
  N5["compaction hidden agent 실행"]
  N4 --> N5
  N6["compaction part 기록"]
  N5 --> N6
  N7["overflow replay 필요 여부 판단"]
  N6 --> N7
```

읽을 파일:

- `packages/opencode/src/session/overflow.ts`
- `packages/opencode/src/session/compaction.ts`
- `packages/opencode/src/session/prompt/compaction.txt`

## 사례 3: 외부 MCP tool을 호출한다

```mermaid
flowchart TD
  N1["config.mcp server 선언"]
  N2["MCP client 연결"]
  N1 --> N2
  N3["tool list 수집"]
  N2 --> N3
  N4["SessionPrompt에서 AI SDK tool로 wrapping"]
  N3 --> N4
  N5["permission ask"]
  N4 --> N5
  N6["MCP result를 text/attachment로 정규화"]
  N5 --> N6
```

- `packages/opencode/src/mcp/index.ts`
- `packages/opencode/src/session/prompt.ts`
- `packages/opencode/src/plugin/index.ts`
