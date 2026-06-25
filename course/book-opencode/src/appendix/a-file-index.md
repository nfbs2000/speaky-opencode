# 부록 A: 주요 파일 인덱스

이 부록은 책 전체를 따라가며 반복해서 열어 보게 될 파일들을 역할별로 묶은 색인이다. 단순 경로 목록이 아니라 "왜 이 파일을 봐야 하는가"를 함께 적었다.

## 코어 런타임의 시작점

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/index.ts` | CLI 명령군과 전체 엔트리포인트 구성을 보여 준다. |
| `packages/opencode/src/project/bootstrap.ts` | 실행 디렉터리를 인스턴스 문맥으로 바꾸는 초기화 경계다. |
| `packages/opencode/src/project/instance.ts` | 프로젝트와 현재 실행 인스턴스의 차이를 읽게 해 준다. |
| `packages/opencode/src/agent/agent.ts` | built-in agent, hidden agent, permission merge가 모두 여기에 있다. |
| `packages/opencode/src/tool/tool.ts` | 모든 도구 실행 계약의 핵심 추상화다. |

## 세션과 프롬프트

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/session/message-v2.ts` | OpenCode의 메시지 모델이 왜 문자열 로그를 넘었는지 보여 준다. |
| `packages/opencode/src/session/session.ts` | 세션 생성, 목록, 부모-자식 관계, 메시지 조회가 모이는 허브다. |
| `packages/opencode/src/session/prompt.ts` | 프롬프트 조립, 도구 해결, 보조 시스템 에이전트 호출이 몰려 있다. |
| `packages/opencode/src/session/compaction.ts` | 긴 세션을 압축하는 실제 정책 상수와 흐름이 있다. |
| `packages/opencode/src/session/summary.ts` | 메시지 요약과 diff 요약이 어떤 데이터로 남는지 보여 준다. |
| `packages/opencode/src/session/overflow.ts` | overflow를 예외가 아니라 운영 경로로 다루는 기준점이다. |

## 권한, 도구, 운영성

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/permission/index.ts` | allow/ask/deny, request/reply, always 규칙이 모두 여기에 있다. |
| `packages/opencode/src/permission/evaluate.ts` | 권한 규칙의 핵심 결정 로직이 매우 압축되어 있다. |
| `packages/opencode/src/session/run-state.ts` | 세션이 busy 상태인지, 중단 가능한지 같은 운영 상태를 맡는다. |
| `packages/opencode/src/session/revert.ts` | 되돌리기와 snapshot 기반 복구 흐름을 따라갈 때 중요하다. |
| `packages/opencode/src/bus/index.ts` | 이벤트 발행과 구독의 공통 채널을 제공한다. |

## 확장 계층

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/plugin/index.ts` | 서버 플러그인 로더, 내부 플러그인, 훅 실행 순서를 본다. |
| `packages/opencode/src/plugin/loader.ts` | 플러그인 엔트리 해석과 설치 흐름을 따라갈 수 있다. |
| `packages/opencode/src/plugin/install.ts` | npm/file 플러그인 설치와 설정 패치가 여기 있다. |
| `packages/opencode/src/skill/index.ts` | 스킬이 지식 자산으로 수집되고 필터링되는 과정을 보여 준다. |
| `packages/opencode/src/mcp/index.ts` | local/remote/OAuth MCP를 한 서비스로 묶는 중심 파일이다. |
| `packages/opencode/src/control-plane/workspace.ts` | 워크스페이스 연결, 복원, 동기화 루프를 읽는 핵심 파일이다. |

## 제품 표면

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/cli/cmd/tui/app.tsx` | TUI가 단순 REPL이 아니라 앱 구조라는 점이 드러난다. |
| `packages/opencode/src/cli/cmd/tui/routes/session/index.tsx` | 가장 두꺼운 통합 화면이다. 세션, 포크, 권한, todo가 다 만난다. |
| `packages/opencode/src/server/routes/instance/session.ts` | 로컬 제어면의 중심이며, 세션 API 표면이 여기 모여 있다. |
| `packages/sdk/js/src/client.ts` | SDK가 디렉터리 문맥과 클라이언트 계약을 어떻게 안정화하는지 보여 준다. |
| `packages/sdk/js/src/index.ts` | 로컬 서버와 클라이언트를 함께 감싸는 진입점이다. |

## 고급 서브시스템

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/opencode/src/lsp/server.ts` | 언어별 LSP 서버 정의와 부트 전략이 한 파일에 모여 있다. |
| `packages/opencode/src/patch/index.ts` | apply_patch 문법을 실제 파일 변경으로 바꾸는 핵심 구현이다. |
| `packages/opencode/src/worktree/index.ts` | git worktree 생성, 이름 충돌 회피, 리셋/삭제 경로가 들어 있다. |
| `packages/opencode/src/snapshot/index.ts` | 재현 가능한 상태와 revert/diff의 기반이다. |
| `packages/opencode/src/provider/transform.ts` | provider 차이를 내부 메시지/옵션 모델로 정규화하는 핵심 변환층이다. |

## 제품과 문서

| 파일 | 왜 중요한가 |
| --- | --- |
| `packages/web/src/content/docs/agents.mdx` | agent 개념의 사용자-facing 설명이다. 코드와 비교해 읽기 좋다. |
| `packages/web/src/content/docs/permissions.mdx` | 권한 모델의 사용자 개념과 실제 구현 차이를 비교할 수 있다. |
| `packages/web/src/content/docs/plugins.mdx` | 플러그인 시스템의 공식 개념 모델이다. |
| `packages/web/src/content/docs/mcp-servers.mdx` | MCP 연결 방식과 실제 구현을 대조할 수 있다. |
| `packages/opencode/specs/tui-plugins.md` | 현재 TUI 플러그인 시스템의 가장 밀도 높은 내부 참고서다. |
| `packages/opencode/specs/effect/tools.md` | 도구 계층의 현재 migration 상태와 설계 방향을 보여 준다. |
| `packages/opencode/specs/effect/routes.md` | 라우트 핸들러의 서비스화 방향을 읽을 수 있다. |

## 처음 다시 열어 볼 순서

책을 다 읽고 다시 코드를 탐험할 때는 아래 순서를 권한다.

1. `agent/agent.ts`
2. `tool/tool.ts`
3. `session/message-v2.ts`
4. `session/prompt.ts`
5. `permission/index.ts`
6. `plugin/index.ts`
7. `mcp/index.ts`
8. `server/routes/instance/session.ts`
9. `patch/index.ts`
10. `provider/transform.ts`

이 열 개만 다시 읽어도 OpenCode의 코어 설계 습관 대부분이 다시 보인다.
