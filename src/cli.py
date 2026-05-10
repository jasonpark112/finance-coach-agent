import os
import sys
from dotenv import load_dotenv
from agent_loop import run_agent

load_dotenv()


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        print(".env.example을 참고해 .env 파일을 만들어주세요.")
        sys.exit(1)

    # CLI 인수로 메시지를 받으면 단일 실행
    if len(sys.argv) > 1:
        run_agent(" ".join(sys.argv[1:]))
        return

    # 인수 없으면 대화형 모드
    print("개인 재무 코치 Agent (종료: quit 또는 Ctrl+C)\n")
    while True:
        try:
            user_input = input("사용자: ").strip()
        except KeyboardInterrupt:
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("종료합니다.")
            break

        run_agent(user_input)  # 출력은 agent_loop 내부에서 처리
        print()


if __name__ == "__main__":
    main()
