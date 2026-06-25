# 부록 G: 인증, 공유, 외부 서비스

## Provider 인증

Provider auth는 `packages/opencode/src/provider/auth.ts`에서 다룬다. OAuth, text prompt, select prompt 같은 인증 방식은 provider별로 다르며 실제 language model 객체를 만들기 전에 auth 정보가 필요하다.

## 내장 auth plugin

- Codex auth: `packages/opencode/src/plugin/codex.ts`
- GitHub Copilot auth: `packages/opencode/src/plugin/github-copilot/copilot.ts`
- Cloudflare auth: `packages/opencode/src/plugin/cloudflare.ts`
- GitLab/Poe auth plugin: npm package import를 통해 server plugin hook 배열에 합류한다.

## MCP OAuth

`packages/opencode/src/mcp/oauth-provider.ts`와 `packages/opencode/src/mcp/oauth-callback.ts`는 redirect uri, local callback server, pending state, token persistence를 다룬다. 외부 도구 연결은 tool schema만으로 끝나지 않는다.

## 공유 정책

공유는 config의 share 설정과 `packages/opencode/src/share/share-next.ts` 계층을 통해 통제된다. 공유 payload에는 세션 메시지뿐 아니라 summary/diff 같은 구조화 정보가 중요하다.
