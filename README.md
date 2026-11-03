<p align="center">
  <img src="assets/banner.png" alt="Useful AI Skills — Built for Real Work, Not Just Demos" width="100%">
</p>

# Skill Mutation Testing

테스트가 열한 개 있어도 딱 하루 차이에서 생기는 버그를 놓칠 수 있습니다. 예를 들어 기한이 지나기 전인지 판단하는 코드에서 `<`를 `<=`로 바꾸면, **기한과 정확히 같은 날**의 결과만 달라집니다. 테스트에 그 날짜가 없다면 변이를 넣어도 테스트는 통과합니다.

**뮤테이션 테스트**는 이런 작은 변경을 넣고 기존 테스트가 알아차리는지 확인합니다. `Killed`는 테스트가 변이를 잡았다는 뜻이고, `Survived`는 변경 후에도 테스트가 통과했다는 뜻입니다. 실행 경로 자체가 빠진 경우는 `NoCoverage`로 따로 봅니다.

## 첫 실행

검사하려는 프로젝트에 `mutation-testing/` 폴더와 사용할 플랫폼의 명령 파일을 복사하세요. 프로젝트의 기존 테스트 명령과 StrykerJS 또는 PIT 설정을 사용합니다.

| 환경 | 설치와 호출 |
| --- | --- |
| Claude Code | [.claude/commands/mut.md](.claude/commands/mut.md)를 같은 경로에 복사한 뒤 `/mut` |
| Cursor Agent | [.cursor/commands/mut.md](.cursor/commands/mut.md)를 같은 경로에 복사한 뒤 `/mut` |
| Gemini CLI | [.gemini/commands/mut.toml](.gemini/commands/mut.toml)을 같은 경로에 복사한 뒤 `/mut`. 세션이 열려 있으면 `/commands reload` |
| GPT · Codex | `mutation-testing/`을 프로젝트의 `.agents/skills/mut/`로 복사한 뒤 `$mut` 또는 `/skills`에서 **mut** 선택 |

```text
/mut 이 PR의 날짜·요금 계산을 검사하고, 살아남은 변이를 잡는 테스트를 추가해줘.
```

일반 ChatGPT에서 스킬 파일을 첨부하면 보고서를 검토하고 테스트 보강안을 작성할 수 있습니다. 실제 검사에는 프로젝트 소스와 테스트 도구에 접근할 수 있는 실행 환경이 필요합니다.

[Claude Code 스킬](https://code.claude.com/docs/en/skills) · [Cursor 명령](https://cursor.com/changelog/1-6) · [Gemini CLI 명령](https://geminicli.com/docs/cli/custom-commands/) · [Codex 스킬 호출](https://learn.chatgpt.com/docs/app-server#skills)

## 무엇을 검사하나요?

- **변경된 핵심 로직에 집중합니다.** PR의 기준 커밋과 비교해 변경된 도메인 파일을 선택합니다. UI, 테스트 파일, DB 스키마와 마이그레이션은 기본 변이 대상에서 제외합니다.
- **세 가지 방법으로 실행 시간을 줄입니다.** 먼저 변이를 만들 파일을 줄이고, 지원되는 러너에서는 해당 코드를 실행하는 테스트만 고릅니다. 반복 실행에서는 호환되는 이전 결과도 재사용합니다.
- **놓친 입력을 AI에 전달합니다.** 살아남은 변이의 위치와 변경 내용을 기록합니다. AI는 원본과 변이의 결과가 갈리는 입력을 찾아 테스트를 보강합니다. 새 테스트는 원본 코드에서 통과하고 변이 코드에서 실패해야 합니다.

문자열이 들어 있는지만 검색하거나 `expect(true).toBe(true)`를 실행하는 테스트는 날짜 판단이 맞는지 확인할 수 없습니다. 같은 예에서는 **기한 당일에 함수가 반환해야 할 값**을 단언하는 테스트를 추가합니다.

`NoCoverage`가 나오면 러너가 올바른 패키지의 테스트를 발견했는지 먼저 확인합니다. 실제로 테스트가 닿지 않는 경로라면, 그 경로를 실행하고 기대 결과를 단언하는 기본 테스트를 추가한 뒤 변이를 다시 돌립니다.

## 도구와 CI

JS·TypeScript에는 **StrykerJS**, Java·Kotlin JVM에는 **PIT**를 사용합니다. JS·TS용 PR 템플릿과 Git 변경 범위 계산 스크립트가 들어 있습니다. PIT는 변경된 소스를 모듈별 클래스 이름에 매핑해 범위를 지정합니다. [도구 설정과 PR 템플릿](mutation-testing/references/tools.md)

참고 사례에서 451은 테스트 수입니다. 검출 결과는 변이 550개 중 273개 검출, 161개 생존, 116개 미실행이었습니다. 한 프로젝트의 결과입니다.

모노레포에서는 바뀐 파일을 소유 패키지별로 나누고, 각 패키지에서 쓰는 설정과 경로를 확인한 뒤 실행합니다. 느린 검사에서는 원본 실행 시간과 멈추는 변이를 확인한 후 타임아웃을 조정합니다. PR에서 느린 스위트를 분리했다면 별도 검사에서 해당 범위를 실행합니다.

## 라이선스

Apache License 2.0을 적용합니다. 저작권은 Chan Woo Cho ([@ccw00325-spec](https://github.com/ccw00325-spec))에게 있습니다. 재배포 시 제4조에 따라 관련 저작권과 출처 고지를 보존해야 합니다. [LICENSE](LICENSE) · [NOTICE](NOTICE)
