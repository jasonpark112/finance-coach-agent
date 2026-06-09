import json

# ──────────────────────────────────────────────
# Mock 데이터
# MOCK_TRANSACTIONS: CODEF API 응답 구조 기반 (https://codef.io/)
#   엔드포인트: POST /v1/kr/bank/p/fast-account/transaction-list
# ──────────────────────────────────────────────

MOCK_TRANSACTIONS = {
    "u001": {
        "2026-03": {
            "resAccountBalance": "1880600",
            "resWithdrawalAmt":  "1119400",
            "commStartDate":     "20260301",
            "commEndDate":       "20260331",
            "resTrHistoryList": [
                # 3/2
                {"resAccountTrDate": "20260302", "resAccountTrTime": "080512", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2991500"},
                {"resAccountTrDate": "20260302", "resAccountTrTime": "090034", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2990000"},
                {"resAccountTrDate": "20260302", "resAccountTrTime": "124530", "resAccountOut": "35000",  "resAccountIn": "0", "resAccountDesc1": "강남한식당",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2955000"},
                # 3/5
                {"resAccountTrDate": "20260305", "resAccountTrTime": "081500", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2946500"},
                {"resAccountTrDate": "20260305", "resAccountTrTime": "090000", "resAccountOut": "42000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "이체",     "resAccountDesc3": "KTX예매",           "resAccountDesc4": "",        "resAfterTranBalance": "2904500"},
                {"resAccountTrDate": "20260305", "resAccountTrTime": "200000", "resAccountOut": "18000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2886500"},
                # 3/8
                {"resAccountTrDate": "20260308", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2885000"},
                {"resAccountTrDate": "20260308", "resAccountTrTime": "183000", "resAccountOut": "43000",  "resAccountIn": "0", "resAccountDesc1": "올리브영",      "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2842000"},
                {"resAccountTrDate": "20260308", "resAccountTrTime": "200000", "resAccountOut": "22000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2820000"},
                # 3/10 - 넷플릭스 자동이체
                {"resAccountTrDate": "20260310", "resAccountTrTime": "000000", "resAccountOut": "13900",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "넷플릭스",          "resAccountDesc4": "",        "resAfterTranBalance": "2806100"},
                {"resAccountTrDate": "20260310", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2797600"},
                {"resAccountTrDate": "20260310", "resAccountTrTime": "131500", "resAccountOut": "4500",   "resAccountIn": "0", "resAccountDesc1": "GS25편의점",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남역점","resAfterTranBalance": "2793100"},
                # 3/12
                {"resAccountTrDate": "20260312", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2791600"},
                {"resAccountTrDate": "20260312", "resAccountTrTime": "190000", "resAccountOut": "67000",  "resAccountIn": "0", "resAccountDesc1": "쿠팡",          "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2724600"},
                {"resAccountTrDate": "20260312", "resAccountTrTime": "141000", "resAccountOut": "5500",   "resAccountIn": "0", "resAccountDesc1": "GS25편의점",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남역점","resAfterTranBalance": "2719100"},
                # 3/15
                {"resAccountTrDate": "20260315", "resAccountTrTime": "124000", "resAccountOut": "12500",  "resAccountIn": "0", "resAccountDesc1": "맥도날드강남",  "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2706600"},
                {"resAccountTrDate": "20260315", "resAccountTrTime": "183000", "resAccountOut": "55000",  "resAccountIn": "0", "resAccountDesc1": "무신사",        "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2651600"},
                {"resAccountTrDate": "20260315", "resAccountTrTime": "180000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2650100"},
                # 3/18 - 월세
                {"resAccountTrDate": "20260318", "resAccountTrTime": "100000", "resAccountOut": "500000", "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "이체",     "resAccountDesc3": "부동산이체 3월월세","resAccountDesc4": "",        "resAfterTranBalance": "2150100"},
                {"resAccountTrDate": "20260318", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2141600"},
                {"resAccountTrDate": "20260318", "resAccountTrTime": "193000", "resAccountOut": "24000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2117600"},
                # 3/22 - SKT 자동이체
                {"resAccountTrDate": "20260322", "resAccountTrTime": "000000", "resAccountOut": "55000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "SKT",               "resAccountDesc4": "",        "resAfterTranBalance": "2062600"},
                {"resAccountTrDate": "20260322", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2061100"},
                {"resAccountTrDate": "20260322", "resAccountTrTime": "200000", "resAccountOut": "45000",  "resAccountIn": "0", "resAccountDesc1": "강남이자카야",  "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2016100"},
                # 3/26 - 유튜브 자동이체
                {"resAccountTrDate": "20260326", "resAccountTrTime": "000000", "resAccountOut": "17000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "유튜브프리미엄",    "resAccountDesc4": "",        "resAfterTranBalance": "1999100"},
                {"resAccountTrDate": "20260326", "resAccountTrTime": "124000", "resAccountOut": "28000",  "resAccountIn": "0", "resAccountDesc1": "강남한식당",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1971100"},
                {"resAccountTrDate": "20260326", "resAccountTrTime": "200000", "resAccountOut": "22000",  "resAccountIn": "0", "resAccountDesc1": "교보문고",      "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "1949100"},
                # 3/31 - 삼성화재 자동이체
                {"resAccountTrDate": "20260331", "resAccountTrTime": "000000", "resAccountOut": "45000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "삼성화재보험",      "resAccountDesc4": "",        "resAfterTranBalance": "1904100"},
                {"resAccountTrDate": "20260331", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "1895600"},
                {"resAccountTrDate": "20260331", "resAccountTrTime": "193000", "resAccountOut": "15000",  "resAccountIn": "0", "resAccountDesc1": "CGV강남",       "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1880600"},
            ],
        },
        "2026-04": {
            "resAccountBalance": "1780600",
            "resWithdrawalAmt":  "1219400",
            "commStartDate":     "20260401",
            "commEndDate":       "20260430",
            "resTrHistoryList": [
                # 4/1
                {"resAccountTrDate": "20260401", "resAccountTrTime": "080512", "resAccountOut": "7500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2992500"},
                {"resAccountTrDate": "20260401", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2991000"},
                {"resAccountTrDate": "20260401", "resAccountTrTime": "200000", "resAccountOut": "21000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2970000"},
                # 4/4
                {"resAccountTrDate": "20260404", "resAccountTrTime": "081500", "resAccountOut": "9000",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2961000"},
                {"resAccountTrDate": "20260404", "resAccountTrTime": "130000", "resAccountOut": "41000",  "resAccountIn": "0", "resAccountDesc1": "강남스시집",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2920000"},
                {"resAccountTrDate": "20260404", "resAccountTrTime": "180000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2918500"},
                # 4/7
                {"resAccountTrDate": "20260407", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2917000"},
                {"resAccountTrDate": "20260407", "resAccountTrTime": "090000", "resAccountOut": "42000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "이체",     "resAccountDesc3": "KTX예매",           "resAccountDesc4": "",        "resAfterTranBalance": "2875000"},
                {"resAccountTrDate": "20260407", "resAccountTrTime": "200000", "resAccountOut": "24000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2851000"},
                # 4/10 - 넷플릭스 자동이체
                {"resAccountTrDate": "20260410", "resAccountTrTime": "000000", "resAccountOut": "13900",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "넷플릭스",          "resAccountDesc4": "",        "resAfterTranBalance": "2837100"},
                {"resAccountTrDate": "20260410", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2828600"},
                {"resAccountTrDate": "20260410", "resAccountTrTime": "183000", "resAccountOut": "43000",  "resAccountIn": "0", "resAccountDesc1": "올리브영",      "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2785600"},
                # 4/14
                {"resAccountTrDate": "20260414", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2777100"},
                {"resAccountTrDate": "20260414", "resAccountTrTime": "124000", "resAccountOut": "32000",  "resAccountIn": "0", "resAccountDesc1": "강남한식당",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2745100"},
                {"resAccountTrDate": "20260414", "resAccountTrTime": "190000", "resAccountOut": "67000",  "resAccountIn": "0", "resAccountDesc1": "쿠팡",          "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2678100"},
                # 4/17
                {"resAccountTrDate": "20260417", "resAccountTrTime": "140000", "resAccountOut": "12000",  "resAccountIn": "0", "resAccountDesc1": "강남내과",      "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2666100"},
                {"resAccountTrDate": "20260417", "resAccountTrTime": "180000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2664600"},
                {"resAccountTrDate": "20260417", "resAccountTrTime": "183000", "resAccountOut": "55000",  "resAccountIn": "0", "resAccountDesc1": "무신사",        "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2609600"},
                # 4/18 - 월세
                {"resAccountTrDate": "20260418", "resAccountTrTime": "100000", "resAccountOut": "500000", "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "이체",     "resAccountDesc3": "부동산이체 4월월세","resAccountDesc4": "",        "resAfterTranBalance": "2109600"},
                {"resAccountTrDate": "20260418", "resAccountTrTime": "082000", "resAccountOut": "8500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "2101100"},
                {"resAccountTrDate": "20260418", "resAccountTrTime": "193000", "resAccountOut": "19000",  "resAccountIn": "0", "resAccountDesc1": "배달의민족",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2082100"},
                # 4/22 - SKT 자동이체
                {"resAccountTrDate": "20260422", "resAccountTrTime": "000000", "resAccountOut": "55000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "SKT",               "resAccountDesc4": "",        "resAfterTranBalance": "2027100"},
                {"resAccountTrDate": "20260422", "resAccountTrTime": "091000", "resAccountOut": "1500",   "resAccountIn": "0", "resAccountDesc1": "서울시교통공사", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "2025600"},
                {"resAccountTrDate": "20260422", "resAccountTrTime": "200000", "resAccountOut": "45000",  "resAccountIn": "0", "resAccountDesc1": "강남이자카야",  "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1980600"},
                # 4/26 - 유튜브 자동이체
                {"resAccountTrDate": "20260426", "resAccountTrTime": "000000", "resAccountOut": "17000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "유튜브프리미엄",    "resAccountDesc4": "",        "resAfterTranBalance": "1963600"},
                {"resAccountTrDate": "20260426", "resAccountTrTime": "183000", "resAccountOut": "89000",  "resAccountIn": "0", "resAccountDesc1": "쿠팡",          "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1874600"},
                {"resAccountTrDate": "20260426", "resAccountTrTime": "215000", "resAccountOut": "27000",  "resAccountIn": "0", "resAccountDesc1": "홍대파스타",    "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1847600"},
                # 4/30 - 삼성화재 자동이체
                {"resAccountTrDate": "20260430", "resAccountTrTime": "000000", "resAccountOut": "45000",  "resAccountIn": "0", "resAccountDesc1": "",              "resAccountDesc2": "자동이체", "resAccountDesc3": "삼성화재보험",      "resAccountDesc4": "",        "resAfterTranBalance": "1802600"},
                {"resAccountTrDate": "20260430", "resAccountTrTime": "082000", "resAccountOut": "7500",   "resAccountIn": "0", "resAccountDesc1": "스타벅스강남점", "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "강남점",  "resAfterTranBalance": "1795100"},
                {"resAccountTrDate": "20260430", "resAccountTrTime": "215000", "resAccountOut": "14500",  "resAccountIn": "0", "resAccountDesc1": "맥도날드강남",  "resAccountDesc2": "카드",     "resAccountDesc3": "",                  "resAccountDesc4": "",        "resAfterTranBalance": "1780600"},
            ],
        },
    }
}

# MOCK_STOCKS: Finnhub API 응답 구조 기반 (https://finnhub.io/)
#   엔드포인트: GET /api/v1/quote?symbol=&token=
#  name 부분은 일단 임의로 작성 해둠 나중에는 지우던가 파싱을 해야 함
MOCK_STOCKS = {
    "005930": {
        "symbol": "005930", "name": "삼성전자",
        "c":  72400,   "d":  -400,  "dp": -0.55,
        "h":  73200,   "l":  71800, "o":  72800,
        "pc": 72800,   "t":  1746504900,
    },
    "TIGER 미국S&P500": {
        "symbol": "TIGER 미국S&P500", "name": "TIGER 미국S&P500",
        "c":  12450,   "d":   99,   "dp":  0.80,
        "h":  12510,   "l":  12380, "o":  12351,
        "pc": 12351,   "t":  1746504900,
    },
    "KODEX 200": {
        "symbol": "KODEX 200", "name": "KODEX 200",
        "c":  35200,   "d":  105,   "dp":  0.30,
        "h":  35350,   "l":  35050, "o":  35095,
        "pc": 35095,   "t":  1746504900,
    },
    "TIGER 미국나스닥100": {
        "symbol": "TIGER 미국나스닥100", "name": "TIGER 미국나스닥100",
        "c":  21800,   "d":  258,   "dp":  1.20,
        "h":  21950,   "l":  21600, "o":  21542,
        "pc": 21542,   "t":  1746504900,
    },
}

# MOCK_NEWS: Finnhub API 응답 구조 기반 (https://finnhub.io/)
# 실제 연동 시 GET /api/v1/company-news?symbol=&from=&to=&token= 응답으로 대체
MOCK_NEWS = {
    "S&P500": [
        {
            "category": "finance",
            "datetime":  1746435600,
            "headline":  "미 증시 강세, S&P500 사상 최고치 경신",
            "id":        7001001,
            "image":     "",
            "related":   "SPY",
            "source":    "한국경제",
            "summary":   "미 연준 금리 동결 기대감에 증시 반등하며 S&P500이 사상 최고치를 경신했다.",
            "url":       "",
        },
        {
            "category": "forex",
            "datetime":  1746349200,
            "headline":  "원달러 환율 1380원대, ETF 투자 시 환율 영향 유의",
            "id":        7001002,
            "image":     "",
            "related":   "SPY",
            "source":    "매일경제",
            "summary":   "환율 변동이 미국 ETF 수익률에 미치는 영향을 분석했다. 원화 약세 시 환차손 주의가 필요하다.",
            "url":       "",
        },
        {
            "category": "finance",
            "datetime":  1746262800,
            "headline":  "TIGER 미국S&P500, 올해 수익률 12% 돌파",
            "id":        7001003,
            "image":     "",
            "related":   "SPY",
            "source":    "이데일리",
            "summary":   "장기 투자 관점에서 꾸준한 성과를 기록하며 연초 대비 수익률 12%를 넘어섰다.",
            "url":       "",
        },
    ],
    "삼성전자": [
        {
            "category": "technology",
            "datetime":  1746435600,
            "headline":  "삼성전자, 2분기 실적 회복 기대감",
            "id":        7002001,
            "image":     "",
            "related":   "005930",
            "source":    "한국경제",
            "summary":   "반도체 업황 개선으로 2분기 영업이익 반등 전망이 높아지고 있다.",
            "url":       "",
        },
        {
            "category": "technology",
            "datetime":  1746349200,
            "headline":  "삼성전자 HBM 공급 확대로 AI 수혜 기대",
            "id":        7002002,
            "image":     "",
            "related":   "005930",
            "source":    "조선비즈",
            "summary":   "엔비디아향 HBM3E 공급 확대 계획을 발표하며 AI 반도체 수혜 기대감이 커지고 있다.",
            "url":       "",
        },
        {
            "category": "finance",
            "datetime":  1746262800,
            "headline":  "외국인 삼성전자 5거래일 연속 순매수",
            "id":        7002003,
            "image":     "",
            "related":   "005930",
            "source":    "파이낸셜뉴스",
            "summary":   "외국인 투자자 귀환에 삼성전자 주가 반등 모색. 5거래일 연속 순매수세가 이어지고 있다.",
            "url":       "",
        },
    ],
    "나스닥": [
        {
            "category": "technology",
            "datetime":  1746435600,
            "headline":  "나스닥 기술주 랠리, AI 관련주 강세",
            "id":        7003001,
            "image":     "",
            "related":   "QQQ",
            "source":    "뉴스1",
            "summary":   "빅테크 실적 호조에 나스닥이 2% 상승하며 AI 관련주 중심의 랠리가 이어졌다.",
            "url":       "",
        },
        {
            "category": "technology",
            "datetime":  1746349200,
            "headline":  "TIGER 미국나스닥100, 반도체 섹터 강세 수혜",
            "id":        7003002,
            "image":     "",
            "related":   "QQQ",
            "source":    "연합뉴스",
            "summary":   "엔비디아·TSMC 상승으로 ETF 수익률이 개선되며 나스닥100 추종 ETF에 자금 유입이 증가했다.",
            "url":       "",
        },
    ],
}

#  매달 반드시 나가는 고정비 카테고리이다. analyze_spending()에서 고정비/변동비를 구분할 때 사용
FIXED_CATEGORIES = {"월세", "통신비", "보험", "구독"}

MONTHLY_INCOME = 3_500_000

# 거래 내역 설명 텍스트에 이 키워드가 포함되면 해당 카테고리로 분류
CATEGORY_KEYWORDS = {
    "식비":   ["스타벅스", "맥도날드", "배달의민족", "GS25", "CU", "한식당", "스시집", "이자카야", "본죽", "파스타"],
    "교통":   ["교통공사", "KTX"],
    "쇼핑":   ["쿠팡", "올리브영", "무신사"],
    "구독":   ["넷플릭스", "유튜브"],
    "문화":   ["CGV", "교보문고"],
    "의료":   ["내과", "약국", "병원"],
    "통신비": ["SKT", "KT", "LGU"],
    "월세":   ["부동산", "월세"],
    "보험":   ["삼성화재", "보험"],
}


# ──────────────────────────────────────────────
# Tool 함수
# ──────────────────────────────────────────────

# 거래 1건을 받아서 카테고리를 반환하는 함수이다. _로 시작하는 건 외부에서 직접 쓰지 않는 내부 함수라는 관례
def _categorize(tx: dict) -> str:
    text = " ".join(filter(None, [
        tx.get("resAccountDesc1", ""),
        tx.get("resAccountDesc2", ""),
        tx.get("resAccountDesc3", ""),
        tx.get("resAccountDesc4", ""),
    ]))
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "기타"


# 2단계로 데이터를 찾는다. 사용자가 없으면 USER_NOT_FOUND, 해당 월 데이터가 없으면 NO_DATA 에러를 반환한다. 성공하면 해당 월의 전체 거래 데이터를 반환한다.
def get_transactions(user_id: str, period: str) -> dict:
    """지정 기간의 지출 내역 조회 (CODEF Mock)"""
    user_data = MOCK_TRANSACTIONS.get(user_id)
    if not user_data:
        return {
            "ok": False, "data": None,
            "error": {"code": "USER_NOT_FOUND", "message": f"사용자 {user_id}를 찾을 수 없습니다"},
        }

    period_data = user_data.get(period)
    if not period_data:
        return {
            "ok": False, "data": None,
            "error": {"code": "NO_DATA", "message": f"{period} 기간의 거래 내역이 없습니다"},
        }

    return {"ok": True, "data": period_data, "error": None}


# 거래 내역을 순회하면서 카테고리별 합계를 낸다. out == 0 인 경우는 입금 거래이므로 건너뛴다. 최종적으로 고정비, 변동비, 총지출, 여유자금을 계산해서 반환한다.
def analyze_spending(transactions: list) -> dict:
    """지출 내역(resTrHistoryList)을 카테고리별로 분류하고 여유 자금 계산"""
    if not transactions:
        return {
            "ok": False, "data": None,
            "error": {"code": "PARSE_ERROR", "message": "거래 내역이 비어 있습니다"},
        }

    fixed = 0
    variable = 0
    breakdown: dict[str, int] = {}

    for tx in transactions:
        out = int(tx.get("resAccountOut", "0"))
        if out == 0:
            continue 
        category = _categorize(tx)
        breakdown[category] = breakdown.get(category, 0) + out
        if category in FIXED_CATEGORIES:
            fixed += out
        else:
            variable += out

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


# 두 단계로 검색한다. "005930" 처럼 정확한 코드로 먼저 찾고, 못 찾으면 "삼성" 같은 부분 문자열로 재검색한다.
def get_stock_price(symbol: str) -> dict:
    """종목·ETF 현재 시세 및 등락률 조회 (Mock)"""
    stock = MOCK_STOCKS.get(symbol)
    if not stock:
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

# keyword in query or query in keyword - 양방향 부분 매칭이다. S&P500"으로 검색해도 걸리고, "미국 S&P500 ETF 추천"으로 검색해도 걸립니다. 아무것도 안 걸리면 모든 카테고리에서 1건씩 가져오는 fallback이 있습니다.
def get_news_summary(query: str, limit: int = 3) -> dict:
    """종목·키워드 관련 최신 뉴스 요약 (Mock)"""
    matched: list = []
    for keyword, news_list in MOCK_NEWS.items():
        if keyword in query or query in keyword:
            matched.extend(news_list)

    # 하나도 안 걸리면 각 키워드에서 1건씩 fallback
    if not matched:
        for news_list in MOCK_NEWS.values():
            matched.extend(news_list[:1])

    if not matched:
        return {
            "ok": False, "data": None,
            "error": {"code": "NEWS_UNAVAILABLE", "message": f"'{query}' 관련 뉴스를 찾을 수 없습니다"},
        }

    return {"ok": True, "data": matched[:limit], "error": None}


# 리스크 성향별로 미리 정해둔 포트폴리오를 선택한다. 여유 자금의 50%만 투자하고 나머지는 비상금으로 유지하는 보수적인 전략을 쓴다.
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
    invest_amount = int(surplus * 0.5)
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


# agent_loop.py에서 Tool 이름(문자열)으로 실제 함수를 찾을 때 쓰는 딕셔너리이다.
TOOL_FUNCTIONS = {
    "get_transactions":        get_transactions,
    "analyze_spending":        analyze_spending,
    "get_stock_price":         get_stock_price,
    "get_news_summary":        get_news_summary,
    "generate_recommendation": generate_recommendation,
}
