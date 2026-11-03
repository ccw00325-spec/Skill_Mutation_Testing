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

## 결과를 보고 테스트 보강하기

| 결과 | 다음 작업 |
| --- | --- |
| `NoCoverage` | 올바른 패키지에서 테스트를 발견하고 커버리지를 수집했는지 확인합니다. 실제로 테스트가 닿지 않는 경로라면 그 경로를 실행하고 기대 결과를 단언하는 기본 테스트부터 추가합니다. |
| `Survived` | 기존 테스트가 놓친 차이를 찾습니다. `<`와 `<=`가 갈리는 기한 당일처럼, 원본과 변이가 다른 결과를 내는 입력을 골라 단언을 보강합니다. |
| `Timeout` | 원본 테스트도 느린지 확인하고 변이 하나를 낮은 동시성으로 재현합니다. 테스트가 단언으로 변이를 잡은 결과와는 별도로 기록합니다. |

테스트를 보강한 뒤에는 원본에서 통과하는지 확인하고, 같은 변이를 캐시 없이 다시 실행합니다. [AI에 전달할 결과와 재실행 방법](mutation-testing/references/tools.md)

테스트 파일은 같은 패키지에서 비슷한 소스를 어떻게 검사하는지 확인한 뒤 정합니다. 기존 파일에 케이스를 추가할 수 있는지 먼저 보고, 새 파일이 필요하면 러너가 찾는 위치와 이름을 따릅니다. 대형 PR에서는 변이마다 관련 테스트를 기록할 수 있습니다. 실행 결과에서 새 케이스가 실제로 실행됐는지 확인합니다.

현재 시간이나 외부 응답에 따라 결과가 달라지는 로직은 테스트에서 그 입력을 고정합니다. 예를 들어 오퍼 API 응답과 마감 시각을 고정하고, 마감과 정확히 같은 순간의 **최종 결제 금액**을 검증합니다. [시계와 외부 응답을 고정하는 예제](mutation-testing/references/tools.md#시간과-외부-의존성이-있는-테스트)

## 도구와 CI

JS·TypeScript에는 **StrykerJS**, Java·Kotlin JVM에는 **PIT**를 사용합니다. JS·TS용 PR 템플릿과 Git 변경 범위 계산 스크립트가 들어 있습니다. PIT는 변경된 소스를 모듈별 클래스 이름에 매핑해 범위를 지정합니다. [도구 설정과 PR 템플릿](mutation-testing/references/tools.md)

참고 사례에서 451은 테스트 수입니다. 검출 결과는 변이 550개 중 273개 검출, 161개 생존, 116개 미실행이었습니다. 한 프로젝트의 결과입니다.

### 모노레포와 느린 PR 검사

바뀐 파일은 소유 패키지별로 나눕니다. 예를 들어 `packages/billing/src/domain/fee.ts`를 저장소 루트에서 실행하면 전체 경로를 사용하고, `packages/billing`에서 실행하면 `src/domain/fee.ts`를 사용합니다. 패키지별 실행 위치·설정·리포트와 캐시를 구분합니다. PIT는 JVM 모듈과 컴파일된 클래스 이름을 확인합니다.

다른 패키지의 빌드 결과나 생성 파일이 테스트에 필요하다면 기존 CI 명령으로 필요한 산출물만 준비합니다. TypeScript를 러너가 직접 변환하는 패키지는 그 실행 방식을 사용합니다. [테스트 위치와 선행 빌드](mutation-testing/references/tools.md)

타임아웃은 원본 실행 시간을 기준으로 조정합니다. StrykerJS는 `timeoutFactor`와 `timeoutMS`, PIT Maven은 `timeoutFactor`와 `timeoutConstant`를 사용합니다. 느린 스위트를 PR에서 분리할 때는 빠진 범위를 기록하고 별도 검사에서 실행합니다. [모노레포 예시와 타임아웃 설정](mutation-testing/references/tools.md)

### 확인한 범위

시계와 오퍼 API 응답을 고정한 할인 예제도 실제 StrykerJS에서 확인했습니다. 마감 직전·직후만 검사했을 때는 변이 6개 중 1개가 살아남았습니다. 기존 테스트 파일에 마감 시각의 가격을 검증하는 케이스를 추가하자 원본 테스트 3개가 모두 통과했고, 변이 6개를 모두 검출했습니다. 같은 `<` → `<=` 변이에서만 기대값 10,000원 대신 9,000원이 나와 새 단언이 실패한 것도 확인했습니다.

실제 StrykerJS 날짜 예제에서 기한 당일 테스트를 추가하자 `<` → `<=` 변이가 `Survived`에서 `Killed`로 바뀌었습니다. 명시적인 설정 파일, 변이 경로, 타임아웃 옵션을 지정한 재실행에서도 변이 5개를 모두 검출했습니다. 대규모 모노레포, PIT, `NoCoverage` 재현은 도구 가이드에 포함된 별도 검증 범위입니다.

## 라이선스

Apache License 2.0을 적용합니다. 저작권은 Chan Woo Cho ([@ccw00325-spec](https://github.com/ccw00325-spec))에게 있습니다. 재배포 시 제4조에 따라 관련 저작권과 출처 고지를 보존해야 합니다. [LICENSE](LICENSE) · [NOTICE](NOTICE)
