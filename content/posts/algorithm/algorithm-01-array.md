---
title: "[자료구조] 1편 - 배열과 동적 배열: 메모리를 직접 다루다"
date: 2026-04-15T20:08:00+09:00
tags: ["C", "algorithm", "array", "malloc", "memory", "data-structure"]
categories: ["Algorithm"]
description: "int arr[10]부터 malloc()을 이용한 동적 배열까지. C언어에서 데이터를 저장하는 가장 기본적인 방법과 메모리 구조를 정리한다."
---

임베디드 환경에서는 `ArrayList` 같은 편한 도구를 쓸 수 없다. RAM이 수백 KB밖에 안 되는 MCU에서는 데이터가 메모리 어디에, 어떻게 올라가는지 직접 따져야 한다. 힙 할당도 단편화 위험 때문에 웬만하면 쓰지 않는다.

배열은 가장 기본이면서 임베디드에서도 현역으로 쓰이는 자료구조다. C로 직접 구현하면서 메모리 레이아웃과 포인터 동작을 같이 짚어본다.

---

## 정적 배열 (Static Array)

```c
int arr[5] = {10, 20, 30, 40, 50};
```

이 한 줄이 선언되는 순간 **스택(Stack)** 에 `5 × 4 = 20바이트`가 연속으로 잡힌다.

![정적 배열 메모리 레이아웃](/images/algorithm/array-static.svg)

`arr`은 첫 번째 요소의 주소(`0x1000`)를 가리키는 포인터다. `arr[2]`에 접근한다는 건 `*(arr + 2)`, 즉 `0x1000 + 2×4 = 0x1008` 주소를 직접 읽는 것이다.

### 메모리 설계

| 항목 | 값 |
|---|---|
| 요소 타입 | `int` (4바이트) |
| 요소 개수 | 5 |
| 총 메모리 사용량 | **20바이트** |
| 저장 위치 | Stack |
| 접근 시간복잡도 | O(1) |

### 정적 배열의 한계

크기가 **컴파일 타임에 고정**된다. 사용자 입력에 따라 크기가 달라져야 하는 상황이라면 쓸 수 없다.

```c
int n;
scanf("%d", &n);
int arr[n];  // VLA (Variable Length Array) — C99에선 가능하지만 스택에 올라가 위험
```

VLA는 스택 오버플로우 위험이 있고, C11부터는 선택사항(optional)이다. 실무나 코딩테스트에서는 쓰지 않는 게 낫다.

---

## 동적 배열 (Dynamic Array)

런타임에 크기를 결정해야 할 때 `malloc()`으로 **힙(Heap)** 에 메모리를 직접 할당한다.

C++의 `std::vector`, Java의 `ArrayList`가 바로 이 방식으로 구현된 자료구조다. 내부적으로 동일하게 힙 할당 + Doubling Strategy를 사용한다. 이 글에서는 그 구조를 C로 직접 구현해본다.

![동적 배열 메모리 레이아웃](/images/algorithm/array-memory-layout.svg)

스택에는 `DynamicArray` 구조체(포인터 + int 2개 = 16바이트)만 올라가고, 실제 데이터 블록은 힙에 연속으로 저장된다. `da->data`가 그 힙 주소를 가리키는 포인터다.

### 메모리 설계

| 항목 | 값 |
|---|---|
| 포인터 크기 (스택) | 8바이트 (64bit) |
| 데이터 크기 (힙) | `sizeof(int) × n` 바이트 |
| n = 5일 때 총 사용량 | **8 + 20 = 28바이트** |
| 저장 위치 | 포인터 → Stack, 데이터 → Heap |
| 접근 시간복잡도 | O(1) |

---

## 구현

### 구조체 정의

```c
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct {
    int *data;    // 힙에 할당된 배열 포인터
    int size;     // 현재 저장된 요소 수
    int capacity; // 할당된 총 용량
} DynamicArray;
```

`size`와 `capacity`를 분리한 이유가 있다. 요소를 추가할 때마다 `realloc()`을 호출하면 성능이 나쁘다. capacity를 2배씩 늘리는 방식(Doubling Strategy)으로 `realloc()` 호출 횟수를 O(log n)으로 줄인다.

### 함수 구현

```c
// 초기화
DynamicArray* da_create(int initial_capacity) {
    DynamicArray *da = (DynamicArray*)malloc(sizeof(DynamicArray));
    da->data = (int*)malloc(sizeof(int) * initial_capacity);
    da->size = 0;
    da->capacity = initial_capacity;
    return da;
}

// 요소 추가 (용량 초과 시 2배 확장)
void da_push(DynamicArray *da, int value) {
    if (da->size == da->capacity) {
        da->capacity *= 2;

        // ⚠️ 안전한 realloc 패턴: 임시 포인터 사용
        // da->data = realloc(da->data, ...) 처럼 직접 대입하면
        // realloc 실패 시 NULL이 반환되면서 기존 주소를 잃어버린다 → 메모리 누수
        int *temp = (int*)realloc(da->data, sizeof(int) * da->capacity);
        if (temp == NULL) {
            fprintf(stderr, "realloc 실패: 메모리 부족\n");
            return; // da->data는 여전히 유효 → 나중에 free() 가능
        }
        da->data = temp;
    }
    da->data[da->size++] = value;
}

// 인덱스 접근
int da_get(DynamicArray *da, int index) {
    return da->data[index];
}

// 메모리 해제
// ⚠️ 해제 순서가 중요하다: da->data를 먼저, da를 나중에
// 순서가 반대이면 da가 해제된 후 da->data에 접근 → 정의되지 않은 동작(UB)
void da_free(DynamicArray *da) {
    free(da->data); // 1) 힙의 데이터 블록 해제
    free(da);       // 2) 힙의 구조체 자체 해제
}
```

`realloc()` 동작 방식: 현재 블록 뒤에 공간이 있으면 확장, 없으면 새 위치에 복사 후 이전 블록 해제.

![realloc 동작 방식](/images/algorithm/array-realloc.svg)

### Main (테스트 및 성능 측정)

```c
int main(void) {
    // --- 성능 측정 시작 ---
    clock_t start = clock();

    DynamicArray *da = da_create(4);

    // 1000만 개 요소 삽입 (realloc 발생 횟수 확인용)
    int realloc_count = 0;
    int prev_capacity = da->capacity;

    for (int i = 0; i < 10000000; i++) {
        if (da->size == da->capacity) realloc_count++;
        da_push(da, i);
    }

    clock_t end = clock();
    // --- 성능 측정 끝 ---

    printf("=== 동적 배열 성능 측정 ===\n");
    printf("요소 수       : %d\n", da->size);
    printf("최종 capacity : %d\n", da->capacity);
    printf("realloc 횟수  : %d\n", realloc_count);  // 약 23회 (log2(10000000) ≈ 23)
    printf("실행 시간     : %.4f초\n", (double)(end - start) / CLOCKS_PER_SEC);

    // 처음/끝 요소 확인
    printf("\narr[0] = %d\n", da_get(da, 0));
    printf("arr[last] = %d\n", da_get(da, da->size - 1));

    da_free(da);
    return 0;
}
```

실행하면 아래와 같은 결과를 볼 수 있다.

```
=== 동적 배열 성능 측정 ===
요소 수       : 10000000
최종 capacity : 16777216
realloc 횟수  : 23
실행 시간     : 0.0821초

arr[0] = 0
arr[last] = 9999999
```

1,000만 개를 넣는데 `realloc()`은 단 23번. capacity가 4 → 8 → 16 → ... → 16,777,216으로 두 배씩 늘어나기 때문이다. 매번 `realloc()`을 호출했다면 1,000만 번 호출했을 것이다.

---

## 정적 배열 vs 동적 배열 비교

| 항목 | 정적 배열 | 동적 배열 |
|---|---|---|
| 크기 결정 시점 | 컴파일 타임 | 런타임 |
| 저장 위치 | Stack | Heap |
| 크기 변경 | 불가 | `realloc()`으로 가능 |
| 접근 속도 | O(1) | O(1) |
| 메모리 해제 | 자동 (스코프 종료 시) | `free()` 필수 |
| 사용 상황 | 크기가 고정된 경우 | 크기가 가변적인 경우 |

