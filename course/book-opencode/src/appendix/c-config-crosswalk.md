# 부록 C: 구성과 권한 크로스워크

OpenCode는 설정 파일 문서와 런타임 구현이 비교적 잘 대응되는 편이지만, 완전히 같은 층은 아니다. 이 표는 사용자가 만지는 설정 항목이 런타임 어느 파일과 연결되는지 빠르게 찾기 위한 것이다.

| 설정/개념 | 사용자-facing 문서 | 주 구현 파일 | 읽을 때 볼 것 |
| --- | --- | --- | --- |
| `agent` | `packages/web/src/content/docs/agents.mdx` | `packages/opencode/src/agent/agent.ts` | built-in agent 정의, config merge, hidden agent |
| `permission` | `packages/web/src/content/docs/permissions.mdx` | `packages/opencode/src/permission/index.ts` | `Rule`, `Request`, `Reply`, `always` 누적 |
| `mcp` | `packages/web/src/content/docs/mcp-servers.mdx` | `packages/opencode/src/mcp/index.ts` | local/remote transport, OAuth, tool refresh |
| `plugin` | `packages/web/src/content/docs/plugins.mdx` | `packages/opencode/src/plugin/index.ts`, `plugin/install.ts` | 외부 플러그인 로드 순서, 설치/해석 경계 |
| `tui.json` | `packages/opencode/specs/tui-plugins.md` | `packages/opencode/src/cli/cmd/tui/plugin/runtime.ts` | TUI plugin id, route/command/slot 등록 |
| `skills.paths`, `skills.urls` | 내부 런타임 동작 | `packages/opencode/src/skill/index.ts` | 스킬 스캔 범위, 이름 중복 처리 |
| session 관련 설정 | TUI/commands 문서 전반 | `packages/opencode/src/session/*.ts` | title, summary, compaction, run-state |
| snapshot 관련 설정 | 문서보다 구현 중심 | `packages/opencode/src/snapshot/index.ts` | 추적 켜짐 여부, diff/revert 비용 |
| workspace / sync | 앱/TUI UI와 연결 | `packages/opencode/src/control-plane/workspace.ts` | 연결 상태, SSE, 복원/동기화 |
| provider / model | providers 문서 | `packages/opencode/src/provider/provider.ts`, `transform.ts` | 모델 선택, options, reasoning variants |

## 권한 키와 실제 도구층의 대응

권한 문서는 사용자에게 친절한 이름을 보여 주지만, 런타임은 이를 조금 더 압축된 키로 다룬다.

| 권한 키 | 런타임 의미 | 관련 도구/층 |
| --- | --- | --- |
| `read` | 파일 읽기 | `read`, 일부 LSP/파일 조회 흐름 |
| `edit` | 모든 파일 변경을 대표하는 상위 권한 | `edit`, `write`, `apply_patch` |
| `bash` | 쉘 실행 | `bash` 도구 |
| `glob` | 파일 패턴 탐색 | `glob` |
| `grep` | 내용 검색 | `grep` |
| `task` | subagent/작업 위임 | `task` 도구 |
| `skill` | 스킬 로드 | `skill` 도구와 스킬 서비스 |
| `lsp` | LSP 호출 | `lsp` 도구 |
| `webfetch`, `websearch`, `codesearch` | 외부/웹 조회 | 대응 도구들 |
| `external_directory` | 작업 루트 밖 접근 | 파일/쉘 계열에서 공통적으로 작동 |
| `doom_loop` | 반복 호출 안전 브레이크 | 도구 반복 감시 |

## 설정을 읽을 때 흔히 놓치는 점

- `permission`은 정적 정책 파일이면서 동시에 세션 중 `always` 응답으로 임시 규칙이 덧붙는 계층이다.
- `agent`는 단순 프롬프트 프리셋이 아니라 permission envelope와 model 선택을 함께 가진다.
- `plugin`과 `tui plugin`은 같은 말이 아니다. 서버 런타임과 TUI 런타임이 분리되어 있다.
- `mcp`는 단순 도구 목록이 아니라 transport, auth, timeout, tool refresh를 포함한다.

## 부록을 쓰는 법

새 기능을 읽다가 "이건 설정에서 어디 켜는 거지?" 혹은 "문서에선 이렇게 말하는데 코드는 어디지?"가 생기면, 이 부록에서 개념을 찾은 뒤 구현 파일로 바로 내려가면 된다. 책 본문을 다시 훑는 것보다 빠르다.
