# 부록 H: 용어집

## Agent

prompt 이름이 아니라 mode, permission, model override, options, prompt를 포함하는 런타임 객체다. 구현은 `packages/opencode/src/agent/agent.ts`에 있다.

## Instance

directory, worktree, project를 묶은 실행 context다. 구현은 `packages/opencode/src/project/instance.ts`에 있다.

## Tool Def

모델에게 노출되는 도구의 실행 계약이다. id, description, zod parameters, execute, metadata가 들어간다. 구현은 `packages/opencode/src/tool/tool.ts`에 있다.

## MessageV2 Part

세션 메시지를 구성하는 typed 조각이다. text, file, tool, subtask, compaction, step-start/finish 등으로 나뉜다.

## Permission Ruleset

permission name, pattern, action으로 이루어진 규칙 배열이다. findLast 기반 override semantics가 중요하다.

## Hidden Agent

사용자가 직접 선택하지 않지만 title, summary, compaction 같은 유지 기능을 수행하는 agent다.

## Snapshot

사용자 repository와 분리된 internal gitdir 기반 파일 상태 기록이다.

## Provider Transform

OpenCode의 message/tool/options를 provider별 SDK가 받아들일 수 있는 형태로 바꾸는 계층이다. 구현은 `packages/opencode/src/provider/transform.ts`에 있다.
