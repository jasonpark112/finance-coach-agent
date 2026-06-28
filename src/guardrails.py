AUTHENTICATED_USER_ID = "u001"

_INJECTION_PATTERNS = [
    "이전 지시를 무시",
    "지시를 무시하고",
    "지금부터 너는",
    "제한 없는",
    "ignore previous instructions",
    "시스템 규칙을 무시",
]

_EXTRACTION_PATTERNS = [
    "시스템 프롬프트",
    "system prompt",
    "내부 지침",
    "개발자가 너에게 설정",
    "내부 설정",
]


def check_input_guardrail(user_message: str):
    """
    사용자 입력에서 Prompt Injection 또는 시스템 프롬프트 추출 시도를 탐지.
    위험 시 에러 dict 반환, 통과 시 None 반환.
    """
    msg_lower = user_message.lower()

    for pattern in _INJECTION_PATTERNS:
        if pattern.lower() in msg_lower:
            return {
                "code": "PROMPT_INJECTION_DETECTED",
                "message": "허용되지 않는 요청입니다. 시스템 지침을 변경하는 입력은 처리할 수 없습니다.",
            }

    for pattern in _EXTRACTION_PATTERNS:
        if pattern.lower() in msg_lower:
            return {
                "code": "SYSTEM_PROMPT_EXTRACTION_DETECTED",
                "message": "시스템 프롬프트나 내부 지침은 공개할 수 없습니다.",
            }

    return None


def check_tool_guardrail(tool_name: str, tool_input: dict):
    """
    Tool 호출 전 권한 검사.
    위반 시 에러 dict 반환, 통과 시 None 반환.
    """
    if tool_name == "get_transactions":
        requested_uid = tool_input.get("user_id")
        if requested_uid != AUTHENTICATED_USER_ID:
            return {
                "ok": False,
                "data": None,
                "error": {
                    "code": "UNAUTHORIZED_USER",
                    "message": f"접근 권한이 없는 사용자 ID입니다: {requested_uid}",
                },
            }
    return None
