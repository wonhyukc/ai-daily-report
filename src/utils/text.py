import re


def contains_word(text: str, keyword: str) -> bool:
    """단어 경계 기반 키워드 매칭 (대소문자 무시).

    부분 문자열 매칭의 오탐("ai" ⊂ "said", "ad" ⊂ "adapter")을 막기 위해
    키워드 앞뒤가 단어 문자가 아닐 때만 매칭한다. \\b 대신 lookaround를
    쓰는 이유는 "DALL-E"처럼 비단어 문자로 끝나는 키워드도 지원하기 위함.
    """
    # 단순 복수형(GPUs, LLMs)은 매칭 유지
    pattern = rf"(?<!\w){re.escape(keyword)}(?:s|es)?(?!\w)"
    return re.search(pattern, text, re.IGNORECASE) is not None
