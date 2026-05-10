import json

# ──────────────────────────────────────────────
# Mock 데이터
# ──────────────────────────────────────────────

MOCK_TRANSACTIONS = {
    "u001": {
        "2026-03": [
            {"date": "2026-03-02", "category": "식비",   "amount": 8500,   "merchant": "스타벅스 강남점"},
            {"date": "2026-03-03", "category": "식비",   "amount": 42000,  "merchant": "강남 한식당"},
            {"date": "2026-03-04", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-03-05", "category": "식비",   "amount": 9500,   "merchant": "GS25 편의점"},
            {"date": "2026-03-07", "category": "쇼핑",   "amount": 35000,  "merchant": "올리브영"},
            {"date": "2026-03-08", "category": "식비",   "amount": 28000,  "merchant": "본죽 강남점"},
            {"date": "2026-03-10", "category": "구독",   "amount": 13900,  "merchant": "넷플릭스"},
            {"date": "2026-03-11", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-03-12", "category": "식비",   "amount": 15000,  "merchant": "CU 편의점"},
            {"date": "2026-03-13", "category": "문화",   "amount": 15000,  "merchant": "CGV 강남"},
            {"date": "2026-03-14", "category": "식비",   "amount": 52000,  "merchant": "강남 스시집"},
            {"date": "2026-03-15", "category": "교통",   "amount": 38000,  "merchant": "KTX 예매"},
            {"date": "2026-03-17", "category": "쇼핑",   "amount": 128000, "merchant": "쿠팡"},
            {"date": "2026-03-18", "category": "월세",   "amount": 500000, "merchant": "부동산 이체"},
            {"date": "2026-03-19", "category": "식비",   "amount": 22000,  "merchant": "배달의민족"},
            {"date": "2026-03-20", "category": "통신비", "amount": 55000,  "merchant": "SKT"},
            {"date": "2026-03-21", "category": "식비",   "amount": 18500,  "merchant": "맥도날드 강남"},
            {"date": "2026-03-22", "category": "구독",   "amount": 17000,  "merchant": "유튜브 프리미엄"},
            {"date": "2026-03-23", "category": "의료",   "amount": 15000,  "merchant": "강남 내과"},
            {"date": "2026-03-24", "category": "식비",   "amount": 35000,  "merchant": "강남 이자카야"},
            {"date": "2026-03-25", "category": "쇼핑",   "amount": 55000,  "merchant": "무신사"},
            {"date": "2026-03-26", "category": "문화",   "amount": 22000,  "merchant": "교보문고"},
            {"date": "2026-03-27", "category": "식비",   "amount": 12000,  "merchant": "스타벅스 삼성점"},
            {"date": "2026-03-28", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-03-29", "category": "보험",   "amount": 45000,  "merchant": "삼성화재"},
            {"date": "2026-03-30", "category": "식비",   "amount": 31000,  "merchant": "홍대 파스타"},
            {"date": "2026-03-31", "category": "구독",   "amount": 9900,   "merchant": "멜론"},
        ],
        "2026-04": [
            {"date": "2026-04-01", "category": "식비",   "amount": 7500,   "merchant": "스타벅스 강남점"},
            {"date": "2026-04-02", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-04-03", "category": "식비",   "amount": 12500,  "merchant": "스타벅스 강남점"},
            {"date": "2026-04-05", "category": "식비",   "amount": 35000,  "merchant": "강남 한식당"},
            {"date": "2026-04-07", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-04-08", "category": "식비",   "amount": 9800,   "merchant": "GS25 편의점"},
            {"date": "2026-04-09", "category": "문화",   "amount": 18000,  "merchant": "CGV 강남"},
            {"date": "2026-04-10", "category": "구독",   "amount": 13900,  "merchant": "넷플릭스"},
            {"date": "2026-04-11", "category": "식비",   "amount": 24000,  "merchant": "배달의민족"},
            {"date": "2026-04-12", "category": "식비",   "amount": 28000,  "merchant": "CU 편의점"},
            {"date": "2026-04-14", "category": "쇼핑",   "amount": 67000,  "merchant": "쿠팡"},
            {"date": "2026-04-15", "category": "교통",   "amount": 1500,   "merchant": "서울시 교통공사"},
            {"date": "2026-04-16", "category": "식비",   "amount": 41000,  "merchant": "강남 스시집"},
            {"date": "2026-04-17", "category": "의료",   "amount": 12000,  "merchant": "강남 내과"},
            {"date": "2026-04-18", "category": "월세",   "amount": 500000, "merchant": "부동산 이체"},
            {"date": "2026-04-19", "category": "식비",   "amount": 16500,  "merchant": "맥도날드 강남"},
            {"date": "2026-04-20", "category": "식비",   "amount": 45000,  "merchant": "강남 이자카야"},
            {"date": "2026-04-21", "category": "쇼핑",   "amount": 43000,  "merchant": "올리브영"},
            {"date": "2026-04-22", "category": "통신비", "amount": 55000,  "merchant": "SKT"},
            {"date": "2026-04-23", "category": "식비",   "amount": 8200,   "merchant": "스타벅스 삼성점"},
            {"date": "2026-04-24", "category": "구독",   "amount": 17000,  "merchant": "유튜브 프리미엄"},
            {"date": "2026-04-25", "category": "쇼핑",   "amount": 89000,  "merchant": "무신사"},
            {"date": "2026-04-26", "category": "식비",   "amount": 32000,  "merchant": "배달의민족"},
            {"date": "2026-04-27", "category": "문화",   "amount": 13000,  "merchant": "교보문고"},
            {"date": "2026-04-28", "category": "교통",   "amount": 42000,  "merchant": "KTX 예매"},
            {"date": "2026-04-29", "category": "식비",   "amount": 27000,  "merchant": "홍대 파스타"},
            {"date": "2026-04-30", "category": "보험",   "amount": 45000,  "merchant": "삼성화재"},
        ],
    }
}

MOCK_STOCKS = {
    "005930": {
        "symbol": "005930", "name": "삼성전자",
        "price": 72400, "change_pct": -0.55,
        "updated_at": "2026-05-06T09:35:00Z",
    },
    "TIGER 미국S&P500": {
        "symbol": "TIGER 미국S&P500", "name": "TIGER 미국S&P500",
        "price": 12450, "change_pct": 0.8,
        "updated_at": "2026-05-06T09:35:00Z",
    },
    "KODEX 200": {
        "symbol": "KODEX 200", "name": "KODEX 200",
        "price": 35200, "change_pct": 0.3,
        "updated_at": "2026-05-06T09:35:00Z",
    },
    "TIGER 미국나스닥100": {
        "symbol": "TIGER 미국나스닥100", "name": "TIGER 미국나스닥100",
        "price": 21800, "change_pct": 1.2,
        "updated_at": "2026-05-06T09:35:00Z",
    },
}

MOCK_NEWS = {
    "S&P500": [
        {
            "title": "미 증시 강세, S&P500 사상 최고치 경신",
            "summary": "미 연준 금리 동결 기대감에 증시 반등",
            "source": "한국경제", "published_at": "2026-05-05",
        },
        {
            "title": "원달러 환율 1380원대, ETF 투자 시 환율 영향 유의",
            "summary": "환율 변동이 미국 ETF 수익률에 미치는 영향 분석",
            "source": "매일경제", "published_at": "2026-05-04",
        },
        {
            "title": "TIGER 미국S&P500, 올해 수익률 12% 돌파",
            "summary": "장기 투자 관점에서 꾸준한 성과 기록",
            "source": "이데일리", "published_at": "2026-05-03",
        },
    ],
    "삼성전자": [
        {
            "title": "삼성전자, 2분기 실적 회복 기대감",
            "summary": "반도체 업황 개선으로 영업이익 반등 전망",
            "source": "한국경제", "published_at": "2026-05-05",
        },
        {
            "title": "삼성전자 HBM 공급 확대로 AI 수혜 기대",
            "summary": "엔비디아향 HBM3E 공급 확대 계획 발표",
            "source": "조선비즈", "published_at": "2026-05-04",
        },
        {
            "title": "외국인 삼성전자 5거래일 연속 순매수",
            "summary": "외국인 투자자 귀환에 삼성전자 주가 반등 모색",
            "source": "파이낸셜뉴스", "published_at": "2026-05-03",
        },
    ],
    "나스닥": [
        {
            "title": "나스닥 기술주 랠리, AI 관련주 강세",
            "summary": "빅테크 실적 호조에 나스닥 2% 상승",
            "source": "뉴스1", "published_at": "2026-05-05",
        },
        {
            "title": "TIGER 미국나스닥100, 반도체 섹터 강세 수혜",
            "summary": "엔비디아·TSMC 상승으로 ETF 수익률 개선",
            "source": "연합뉴스", "published_at": "2026-05-04",
        },
    ],
}

# 고정비로 분류할 카테고리
FIXED_CATEGORIES = {"월세", "통신비", "보험", "구독"}

# 가정 월 소득 (3년차 IT 개발자)
MONTHLY_INCOME = 3_500_000


# ──────────────────────────────────────────────
# Tool 함수
# ──────────────────────────────────────────────

def get_transactions(user_id: str, period: str) -> dict:
    """지정 기간의 지출 내역 조회 (Mock)"""
    user_data = MOCK_TRANSACTIONS.get(user_id)
    if not user_data:
        return {
            "ok": False, "data": None,
            "error": {"code": "USER_NOT_FOUND", "message": f"사용자 {user_id}를 찾을 수 없습니다"},
        }

    transactions = user_data.get(period)
    if not transactions:
        return {
            "ok": False, "data": None,
            "error": {"code": "NO_DATA", "message": f"{period} 기간의 거래 내역이 없습니다"},
        }

    return {"ok": True, "data": transactions, "error": None}


def analyze_spending(transactions: list) -> dict:
    """지출 내역을 카테고리별로 분류하고 여유 자금 계산"""
    if not transactions:
        return {
            "ok": False, "data": None,
            "error": {"code": "PARSE_ERROR", "message": "거래 내역이 비어 있습니다"},
        }

    fixed = 0
    variable = 0
    breakdown: dict[str, int] = {}

    for tx in transactions:
        category = tx["category"]
        amount = tx["amount"]
        breakdown[category] = breakdown.get(category, 0) + amount
        if category in FIXED_CATEGORIES:
            fixed += amount
        else:
            variable += amount

    total = fixed + variable
    surplus = MONTHLY_INCOME - total

    return {
        "ok": True,
        "data": {
            "fixed": fixed,
            "variable": variable,
            "total": total,
            "surplus": surplus,
            "monthly_income": MONTHLY_INCOME,
            "breakdown": breakdown,
        },
        "error": None,
    }


def get_stock_price(symbol: str) -> dict:
    """종목·ETF 현재 시세 및 등락률 조회 (Mock)"""
    stock = MOCK_STOCKS.get(symbol)
    if not stock:
        # 부분 일치 허용
        for key, value in MOCK_STOCKS.items():
            if symbol in key or symbol in value.get("name", ""):
                stock = value
                break

    if not stock:
        return {
            "ok": False, "data": None,
            "error": {
                "code": "SYMBOL_NOT_FOUND",
                "message": f"종목 '{symbol}'을 찾을 수 없습니다. 지원 종목: {list(MOCK_STOCKS.keys())}",
            },
        }

    return {"ok": True, "data": stock, "error": None}


def get_news_summary(query: str, limit: int = 3) -> dict:
    """종목·키워드 관련 최신 뉴스 요약 (Mock)"""
    matched: list = []
    for keyword, news_list in MOCK_NEWS.items():
        if keyword in query or query in keyword:
            matched.extend(news_list)

    if not matched:
        # 키워드 미매칭 시 전체에서 하나씩 반환
        for news_list in MOCK_NEWS.values():
            matched.extend(news_list[:1])

    if not matched:
        return {
            "ok": False, "data": None,
            "error": {"code": "NEWS_UNAVAILABLE", "message": f"'{query}' 관련 뉴스를 찾을 수 없습니다"},
        }

    return {"ok": True, "data": matched[:limit], "error": None}


def generate_recommendation(surplus: int, risk: str, market_data: dict) -> dict:
    """여유 자금·리스크 성향·시장 데이터 기반 투자 추천 생성"""
    if surplus <= 0:
        return {
            "ok": False, "data": None,
            "error": {"code": "INSUFFICIENT_DATA", "message": "여유 자금이 없어 투자 추천이 불가합니다"},
        }

    profiles = {
        "low": {
            "label": "안정형",
            "picks": [
                {"symbol": "KODEX 200",        "reason": "국내 대형주 분산으로 안정적 수익",  "weight_pct": 60},
                {"symbol": "TIGER 미국S&P500",  "reason": "미국 시장 분산 투자",               "weight_pct": 40},
            ],
        },
        "mid": {
            "label": "중립형",
            "picks": [
                {"symbol": "TIGER 미국S&P500",   "reason": "장기 우상향 기대 S&P500 추종 ETF", "weight_pct": 50},
                {"symbol": "TIGER 미국나스닥100", "reason": "기술주 중심 성장 ETF",              "weight_pct": 30},
                {"symbol": "KODEX 200",           "reason": "국내 시장 분산",                   "weight_pct": 20},
            ],
        },
        "high": {
            "label": "공격형",
            "picks": [
                {"symbol": "TIGER 미국나스닥100", "reason": "AI·빅테크 성장 수혜, 고수익 가능", "weight_pct": 50},
                {"symbol": "005930",              "reason": "삼성전자 반도체 업황 회복 기대",    "weight_pct": 30},
                {"symbol": "TIGER 미국S&P500",   "reason": "분산 투자 기반",                    "weight_pct": 20},
            ],
        },
    }

    profile = profiles.get(risk, profiles["mid"])
    invest_amount = int(surplus * 0.5)  # 여유 자금의 50%만 투자 권장
    reserve = surplus - invest_amount

    recommendation = (
        f"여유 자금 {surplus:,}원 기준, {profile['label']} 포트폴리오를 추천합니다. "
        f"투자 권장 금액은 {invest_amount:,}원(여유 자금의 50%)이며, "
        f"나머지 {reserve:,}원은 비상금으로 유지하세요."
    )

    return {
        "ok": True,
        "data": {
            "recommendation": recommendation,
            "invest_amount": invest_amount,
            "surplus": surplus,
            "risk": risk,
            "picks": profile["picks"],
        },
        "error": None,
    }


# Tool 이름 → 함수 매핑 (agent_loop에서 사용)
TOOL_FUNCTIONS = {
    "get_transactions":       get_transactions,
    "analyze_spending":       analyze_spending,
    "get_stock_price":        get_stock_price,
    "get_news_summary":       get_news_summary,
    "generate_recommendation": generate_recommendation,
}
