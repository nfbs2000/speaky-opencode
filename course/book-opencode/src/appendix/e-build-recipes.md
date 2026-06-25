# 부록 E: 빌드와 검색 명령 모음

이 책은 별도 `mdBook` 프로젝트다. 기존 `packages/web` 문서 사이트와는 별개로 빌드하고 배포해야 한다.

## 기본 빌드

```bash
mdbook build docs/book-ko
```

설명:
정적 HTML 산출물을 `docs/book-ko/book`에 생성한다.

## 로컬 미리보기

```bash
mdbook serve docs/book-ko --open
```

설명:
로컬 개발 서버를 띄우고 브라우저에서 책을 바로 연다.

## 검색 인덱스 생성

```bash
bunx pagefind --site docs/book-ko/book
```

설명:
`pagefind-search.js`가 기대하는 검색 인덱스를 생성한다. 이 단계를 거쳐야 책 상단 검색 토글이 실제 검색 UI를 띄운다.

## 구조 검증

```bash
find docs/book-ko/src -type f | sort
```

설명:
챕터와 부록 파일이 모두 존재하는지, `SUMMARY.md` 구성과 실제 파일 구성이 어긋나지 않는지 빠르게 본다.

## 챕터 길이 점검

```bash
python3 - <<'PY'
from pathlib import Path
for p in sorted(Path('docs/book-ko/src').rglob('*.md')):
    if p.name == 'SUMMARY.md':
        continue
    print(f\"{p.relative_to('docs/book-ko/src')}\\t{sum(1 for _ in p.open(encoding='utf-8'))}\")
PY
```

설명:
어느 장이 지나치게 얇은지 수치로 확인한다. 기준서와 비교할 때 유용하다.

## 명시적 소스 앵커 검증

```bash
ruby -EUTF-8 -e 'require \"set\"; paths = Dir[\"docs/book-ko/src/**/*.md\"].flat_map { |f| File.read(f, encoding: \"UTF-8\").scan(/`((?:packages|infra)\\/[^`*?\\[\\]]+)`/).flatten }.to_set.to_a.sort; missing = paths.reject { |p| File.exist?(p) }; puts(missing.empty? ? \"OK\" : missing.join(\"\\n\"))'
```

설명:
책 안에 적은 명시적 파일 경로가 실제 저장소에 존재하는지 빠르게 확인한다.

## 현재 초안에서 권장하는 검증 순서

1. `mdbook build docs/book-ko`
2. `bunx pagefind --site docs/book-ko/book`
3. `find docs/book-ko/book -maxdepth 2 -type f | sort | sed -n '1,160p'`

이 세 단계만 돌려도 본문, 정적 산출물, 검색 자산이 함께 살아 있는지 확인할 수 있다.
