# 부록 B: 프롬프트 파일 인덱스

OpenCode는 시스템 프롬프트를 한 파일에 몰아넣지 않는다. 목적별 프롬프트 파일이 따로 있고, `session/prompt.ts`가 현재 모드와 모델에 따라 이를 조립한다. 이 부록은 그 파일들을 역할별로 정리한다.

## 세션 기본 프롬프트

| 파일 | 역할 |
| --- | --- |
| `packages/opencode/src/session/prompt/default.txt` | 기본 작업 프롬프트의 중심이다. |
| `packages/opencode/src/session/prompt/plan.txt` | 쓰기/실행을 제한한 계획 모드 전용 프롬프트다. |
| `packages/opencode/src/session/prompt/build-switch.txt` | build 계열 전환 시 추가되는 리마인더다. |
| `packages/opencode/src/session/prompt/max-steps.txt` | step 수 제한 관련 정책 문구다. |

## 모델 또는 공급자별 프롬프트

| 파일 | 역할 |
| --- | --- |
| `packages/opencode/src/session/prompt/anthropic.txt` | Anthropic 계열 모델에 맞춘 보조 지침이다. |
| `packages/opencode/src/session/prompt/gpt.txt` | GPT 계열 모델용 차등 지침이다. |
| `packages/opencode/src/session/prompt/copilot-gpt-5.txt` | Copilot GPT-5 계열에 맞춘 별도 레이어다. |
| `packages/opencode/src/session/prompt/gemini.txt` | Gemini 계열의 도구 사용/검증 문구를 담는다. |
| `packages/opencode/src/session/prompt/kimi.txt` | Kimi 계열 모델을 위한 조정 레이어다. |
| `packages/opencode/src/session/prompt/trinity.txt` | 특정 제공자군에 맞춘 전용 보조 지침이다. |
| `packages/opencode/src/session/prompt/beast.txt` | 모델 특화 프롬프트 계층의 또 다른 예다. |

## 보조 시스템 에이전트 프롬프트

| 파일 | 역할 |
| --- | --- |
| `packages/opencode/src/agent/prompt/title.txt` | 세션 제목 생성 전용 프롬프트다. |
| `packages/opencode/src/agent/prompt/summary.txt` | 요약 에이전트가 사용하는 프롬프트다. |
| `packages/opencode/src/agent/prompt/compaction.txt` | 긴 세션을 압축하는 compaction 에이전트 프롬프트다. |
| `packages/opencode/src/agent/prompt/explore.txt` | `explore` subagent의 임무를 규정한다. |
| `packages/opencode/src/agent/generate.txt` | 새 agent 구성을 생성할 때 사용하는 텍스트 자산이다. |

## 명령 템플릿과 규칙 자산

| 파일 | 역할 |
| --- | --- |
| `packages/opencode/src/command/template/*.txt` | slash command나 명령 시스템이 삽입하는 템플릿 자산이다. |
| `packages/opencode/src/tool/apply_patch.txt` | patch 계열 도구 사용법을 모델에 설명하는 자산이다. |
| `packages/opencode/src/tool/todowrite.txt` | todo 도구 사용 방식을 지시하는 텍스트 자산이다. |

## 이 파일들을 읽을 때 볼 것

프롬프트 파일을 읽을 때는 문장 자체보다 아래 네 가지를 보길 권한다.

1. 어떤 파일이 항상 포함되고 어떤 파일이 조건부로 들어가는가
2. 어떤 제약이 코드가 아니라 프롬프트 레이어에 실려 있는가
3. 모델 차이를 코드 분기보다 텍스트 분리로 해결한 부분이 어디인가
4. 숨은 시스템 에이전트가 메인 assistant와 얼마나 다른 목적 함수를 가지는가

## 가장 먼저 대조해 볼 조합

- `default.txt` vs `plan.txt`
- `anthropic.txt` vs `gpt.txt`
- `summary.txt` vs `compaction.txt`
- `apply_patch.txt` vs `todowrite.txt`

이 대조만 해도 OpenCode가 프롬프트를 "성격"이 아니라 "운영 제어층"으로 다룬다는 점이 보인다.
