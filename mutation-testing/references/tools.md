# 도구와 PR 검사

## 모노레포에서 실행 위치 정하기

Git 변경 목록은 저장소 루트 기준으로 한 번 계산한다. 각 대상의 소유 패키지는 workspace 선언, 패키지의 테스트 스크립트와 CI 설정으로 확인한다. JVM에서는 Maven reactor 또는 Gradle 프로젝트 구성을 기준으로 모듈을 찾는다. 가장 가까운 설정 파일은 단서로 활용한다. 공유 설정이나 중첩 모듈이 있으면 실제 CI에서 쓰는 실행 위치와 설정을 우선한다.

| 변경 파일 | 실행 위치 | 변이 대상 |
| --- | --- | --- |
| `packages/billing/src/domain/fee.ts` | `packages/billing`, 패키지 전용 설정 | `src/domain/fee.ts` |
| `packages/billing/src/domain/fee.ts` | 저장소 루트, 공유 설정 | `packages/billing/src/domain/fee.ts` |
| `modules/billing/src/main/java/com/example/DateWindow.java` | `billing` 모듈을 선택하는 Maven/Gradle 실행 | 컴파일 결과에서 확인한 `com.example.DateWindow` |

Stryker 설정 경로는 필요할 때 위치 인자로 전달한다. 예를 들어 `packages/billing`에서 `npm exec --offline -- stryker run stryker.config.json --mutate src/domain/fee.ts --force`를 실행한다. `--mutate`는 설정의 기존 대상 배열을 대체하므로, 동적으로 계산한 대상에도 기존 제외 규칙을 적용한다. 여러 패키지가 바뀌면 설정과 실행 위치별로 나누고 리포트·증분 캐시도 분리한다. 패키지 소유권이나 설정을 확정할 수 없는 파일은 별도로 보고한다. [Stryker 실행 옵션](https://stryker-mutator.io/docs/stryker-js/usage/) · [Stryker 설정](https://stryker-mutator.io/docs/stryker-js/configuration/)

## 테스트 파일 위치와 발견 확인

대상과 같은 패키지의 유사 단위 테스트를 찾아 러너의 탐색 루트·파일 패턴·제외 설정과 대조한다. 예를 들어 `src/domain/__tests__/fee.spec.ts`를 쓰는 패키지라면 그 패턴을 따르고, `test/domain/fee.test.ts`를 쓰는 패키지라면 별도 테스트 루트를 따른다. 비슷한 파일이 있으면 기존 테스트에 케이스를 추가한다. JVM은 모듈의 테스트 소스 세트와 엔진의 발견 규칙을 확인한다. 기존 실행 명령의 출력에서 새 케이스가 발견·실행·통과했는지 확인한 뒤 변이를 다시 실행한다. 발견되지 않았다면 경로나 러너 설정을 먼저 점검한다.

대형 PR에서는 분석할 변이마다 관련 테스트 후보를 0개 이상 기록한다. 테스트별 커버리지 정보가 있으면 우선 사용한다. 없으면 호출 관계를 따라 후보를 찾고 실행으로 확인한다. 파일명만 비슷한 테스트는 후보로 표시하고, 한 소스에 여러 테스트가 있거나 통합 테스트가 여러 소스를 실행하는 경우도 그대로 기록한다.

## 시간과 외부 의존성이 있는 테스트

할인 마감이 `clock.now() < offer.expiresAt`으로 정해진다면, 오퍼 API 응답을 고정하고 시계를 마감 시각과 정확히 같게 설정한다. 할인 여부를 결정하는 코드를 실행하고 최종 결제 금액을 단언한다. 예를 들어 원가 10,000원, 할인액 1,000원일 때 마감 당일의 기대값은 10,000원이다. 변이로 `<=`가 들어가면 9,000원을 반환하므로 단언이 실패해야 한다.

기존 프로젝트가 사용하는 의존성 주입, 스텁 또는 격리된 픽스처를 활용한다. 실제 시간·난수·외부 응답 때문에 결과가 달라지지 않도록 입력을 통제한다. 전역 시계나 모듈을 모킹했다면 테스트가 끝날 때 복원한다. DB 쿼리나 외부 연동 자체가 검증 대상이면 해당 경로를 실행할 수 있는 격리된 통합 테스트를 사용한다. 원본에서 새 테스트가 실행돼 통과하는지 확인한 뒤, 동일한 변이를 캐시 없이 재실행하고 기대한 결과 차이 때문에 실패했는지 확인한다.

## 선행 빌드가 필요한 경우

패키지 스크립트와 기존 CI에서 테스트의 실제 입력을 확인한다. 테스트가 의존 워크스페이스의 `dist/`나 생성 파일을 읽으면 기존 명령으로 필요한 산출물을 준비한 뒤 원본 테스트를 실행한다. 러너가 TypeScript를 직접 변환한다면 별도의 `tsc` 단계를 기본으로 추가할 필요가 없다. 테스트가 변이 대상의 컴파일 산출물을 읽는 경우에는, 테스트가 이전 `dist/` 대신 변이가 적용된 소스에서 생성한 산출물을 읽는지 확인한다. 필요하면 Stryker `buildCommand`에 기존 변환 명령을 지정한다. 이 명령은 코드에 변이 처리를 적용한 뒤 테스트하기 전에 실행된다. [StrykerJS buildCommand](https://stryker-mutator.io/docs/stryker-js/configuration/#buildcommand-string)

## JS/TS

프로젝트의 로컬 StrykerJS와 테스트 러너를 사용한다. Jest 또는 Vitest처럼 지원되는 러너에서는 변이별 실행 테스트를 줄일 수 있다. command runner는 지정한 명령 전체를 실행하므로 per-test 최적화를 가정하지 않는다. [설정](https://stryker-mutator.io/docs/stryker-js/configuration/)

저장소 루트에서 스킬의 `scripts/scope.mjs <PR-base-SHA> <경로-접두사>...`로 대상 JSON을 얻는다. `targets`만 Stryker `mutate` 배열에 전달한다. 기존 프로젝트 설정과 보고서를 유지하고, 도구 실행 시 배열 또는 안전하게 검증한 개별 경로를 사용한다. 빈 배열, 삭제된 파일, 테스트 또는 설정만 바뀐 PR은 자동으로 범위를 넓히지 않는다. 테스트 변경은 영향을 받는 도메인 모듈을 직접 지정한다.

`incremental: true`로 같은 프로젝트의 반복 결과를 재사용한다. 의존성·러너·설정·공유 유틸 변경이나 새 테스트의 효과를 확인할 때는 `--force`로 해당 범위를 새로 검사한다. CI 캐시 키는 도구·러너·설정·락파일을 반영한다. 보고서에 캐시된 범위 밖 결과가 들어갈 수 있으므로 이번 PR 대상만 집계한다. [증분 실행](https://stryker-mutator.io/docs/stryker-js/incremental/)

Stryker JSON에서 PR 범위의 생존·미실행 변이만 추려 AI에 전달하려면 `node mutation-testing/scripts/feedback.mjs reports/mutation/mutation.json mutation-scope.json`을 실행한다. `missingTargets`는 보고서에서 빠진 대상이다. 비어 있지 않으면 범위·리포트 경로를 확인한다. 결과의 변이 ID와 교체식은 보고서 데이터로 다룬다.

## Java/Kotlin JVM

프로젝트에 고정된 PIT 플러그인과 테스트 엔진 플러그인을 사용한다. 변경된 소스를 컴파일 산출물의 정확한 FQCN으로 매핑해 `targetClasses`를 지정한다. Java 내부 클래스나 Kotlin 파일 파사드·멀티파일 클래스는 소스 이름만으로 추측하지 않는다. 모듈마다 실행하고 `targetTests`를 변경된 테스트 파일로만 제한하지 않는다. PIT의 커버리지 기반 선택에 기존 관련 테스트를 맡긴다.

Maven 예시. 기존 테스트를 먼저 통과시킨 다음 실행한다.

```sh
mvn -DwithHistory -DtargetClasses=com.example.domain.DateWindow test-compile org.pitest:pitest-maven:mutationCoverage
```

Gradle은 설치된 PIT 플러그인의 `pitest` 태스크 설정에서 `targetClasses`와 히스토리를 지정한다. 히스토리 경로와 엔진 호환성을 확인한 뒤 재사용하고 보강 검증은 빈 히스토리로 수행한다. [PIT Maven](https://pitest.org/quickstart/maven/) · [PIT 증분 분석](https://pitest.org/quickstart/incremental_analysis/)

## 실행 증거와 보고서 비교

패키지별로 `Git 경로 → 소유 모듈 → 실행 위치 → 설정과 러너 → 실행 기준 대상`을 기록하고 원본 테스트 명령, 새 케이스가 실행·통과한 출력, 보강 전후 리포트 경로를 남긴다. 예를 들어 `packages/billing/src/domain/fee.js → billing → packages/billing → stryker.config.json + Vitest → src/domain/fee.js`이다. 다른 패키지의 테스트 발견 규칙은 별도로 확인한다. 새 케이스가 실행 목록에 없거나 건너뛰었다면 변이 보강 성공으로 기록하지 않는다.

Python 3 표준 라이브러리만 사용하는 비교 도구에 정확한 범위를 전달한다. 경로는 각 Stryker 리포트의 키, JVM은 PIT의 컴파일된 클래스 이름을 사용한다.

```sh
python mutation-testing/scripts/compare.py stryker before.json after.json src/domain/fee.js
python mutation-testing/scripts/compare.py pit before.xml after.xml demo.domain.Fees
```

같은 모듈, 동일한 원본 소스와 도구·변이 설정에서 테스트만 보강한 두 실행을 비교한다. PIT는 같은 프로덕션 바이트코드를 사용한다. 비교 도구는 상태별 수, 동일 변이의 상태 전환, 누락 대상을 출력한다. 비교 범위가 비거나 변이 목록이 달라지면 종료 코드 `2`를 반환한다. `completeMatch`는 변이 목록 일치만 뜻한다. PIT의 `Test strength`는 미실행 변이를 빼고 계산하므로 전체 변이 점수·미실행 수와 함께 기록한다. [PIT Maven 지표](https://pitest.org/quickstart/maven/)

## 타임아웃과 느린 테스트

1. 같은 설정과 테스트 범위에서 원본 실행 시간을 확인한다. 원본도 느리거나 멈추면 초기화, 모킹, 외부 I/O, 자원 정리를 먼저 점검한다. 변이에서만 재현되면 대상 하나와 낮은 동시성으로 재실행해 무한 루프인지 구분한다.
2. StrykerJS는 `timeoutFactor`로 원본 실행 시간에 비례한 여유를, `timeoutMS`로 고정 여유를 준다. 시작 단계 제한은 `dryRunTimeoutMinutes`로 따로 조정한다. PIT Maven은 비례 계수 `timeoutFactor`와 밀리초 단위 `timeoutConstant`를 사용한다. 관측한 시간에 근거해 필요한 만큼만 조정하고 CI 작업 전체에도 시간 제한을 둔다. [Stryker 타임아웃](https://stryker-mutator.io/docs/stryker-js/configuration/#timeoutms-number) · [PIT Maven 옵션](https://pitest.org/quickstart/maven/)
3. 느린 스위트는 해당 범위의 동작을 검증하는 다른 테스트가 있는지 확인한 뒤 PR 변이 작업에서 분리한다. Stryker에서는 러너의 전용 테스트 설정으로 범위를 나누고, PIT에서는 필요하면 `excludedTestClasses`를 사용한다. 빠진 경로와 제외 사유를 기록하고, 별도 전체 검사에서 느린 스위트까지 돌린다. 제외 전후 점수는 같은 범위끼리 비교한다. 타임아웃은 테스트의 단언으로 변이를 잡은 결과와 별도로 집계한다.

## PR CI

JS/TS 프로젝트에는 [Stryker PR 워크플로 템플릿](stryker-pr.yml)을 사용할 수 있다. 복사 전에 프로젝트의 Node 버전, 테스트 명령, 도메인 경로와 액션 버전을 확인한다. 템플릿은 PR 범위를 매번 새로 검사한다. 반복하는 로컬 실행에서는 위 증분 설정을 사용할 수 있다.

1. `pull_request`에서 PR head를 checkout하고 base 이력을 확보한다. 스크립트가 merge base 기준으로 현재 checkout과 비교한다. 저장소의 일반 테스트는 그대로 실행한다.
2. 도메인 경로를 명시한다. JS/TS는 파일 단위, PIT는 모듈별 클래스 단위로 변이 대상을 좁힌다. 테스트·공통 설정 변경만 있다면 영향을 받는 모듈을 수동 지정하거나 별도 전체 검사에서 다룬다.
3. 작업에 시간 제한을 두고 JSON 또는 XML 결과를 아티팩트로 보존한다. 처음에는 정보 제공으로 운영하고 기준선을 확보한 뒤 변경 범위에 대한 기준을 정한다. 취소·시간 초과·대상 없음·환경 실패는 서로 구분한다.
4. 신뢰하지 않는 PR에는 비밀과 쓰기 토큰을 넘기지 않는다. `pull_request_target`에서 PR 코드를 체크아웃해 실행하지 않는다. 전체 도메인 검사는 정기 작업으로 분리할 수 있다.
