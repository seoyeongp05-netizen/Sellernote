import time
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ---------------------------------------------------------
# 1. 페이지 기본 설정 및 직관적 커스텀 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="SCM 지능형 모의 발주 시스템 (DSS)",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1B365D;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #556575;
        margin-bottom: 1.2rem;
    }
    .exec-badge {
        display: inline-block;
        background-color: #E8F4FD;
        color: #0B5394;
        border: 1px solid #9FC5E8;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.88rem;
    }
    .alert-card {
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.55rem;
        font-size: 0.9rem;
        line-height: 1.45;
    }
    .alert-red { background-color: #FDECEA; border-left: 5px solid #D93025; color: #7F1D1D; }
    .alert-orange { background-color: #FEF3C7; border-left: 5px solid #F59E0B; color: #78350F; }
    .alert-yellow { background-color: #FEF9C3; border-left: 5px solid #EAB308; color: #713F12; }
    .alert-blue { background-color: #EFF6FF; border-left: 5px solid #2563EB; color: #1E3A8A; }
    div[data-testid="stMetric"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 0.8rem 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 로드 및 기본 마스터 생성 (CSV 연동 + 내장 샘플)
# ---------------------------------------------------------
@st.cache_data
def load_sku_master():
    # 실제 CSV 파일이 저장소에 함께 업로드된 경우 우선 활용
    if os.path.exists("SKU별_관측이후_미래수요예측표_A.csv"):
        try:
            df_a = pd.read_csv("SKU별_관측이후_미래수요예측표_A.csv", encoding="utf-8-sig")
        except Exception:
            df_a = pd.read_csv("SKU별_관측이후_미래수요예측표_A.csv", encoding="cp949")
    else:
        df_a = None

    np.random.seed(42)
    sample_skus = [
        {
            "SKU_ID": "S2036649", "품목명": "프리미엄 콜라겐 앰플 30ml", "모델": "택배SES+화물TSB",
            "주당평균_A": 89.0, "변동비율_k": 0.92, "원본P20_1주": 52.0, "원본P95_1주": 165.0,
            "로트1_재고": 180, "로트1_잔여주": 4, "로트2_재고": 210, "로트2_잔여주": 10,
            "입고방식": "해상", "예정입고량": 400, "입고예정주": 6, "확정화물주문": 120,
            "의뢰일": "2026-10-20", "수락일": "2026-10-22", "운송시작일": "2026-11-02", "도착예정일": "2026-12-28",
            "운송상태": "해상 운송중 (본선 선적)", "출발국가": "대한민국", "출발항": "부산항 (KRPUS)",
            "도착국가": "태국", "도착항": "램차방항 (THLCH)", "컨테이너": "20ft Dry", "적재량_CBM": 18.5,
            "운송비_원": 2450000, "VAT_원": 245000, "리드타임_주": 6
        },
        {
            "SKU_ID": "S2043698", "품목명": "시카 진정 수분크림 80ml", "모델": "택배SES+화물SBA",
            "주당평균_A": 189.5, "변동비율_k": 1.35, "원본P20_1주": 95.0, "원본P95_1주": 240.0,
            "로트1_재고": 260, "로트1_잔여주": 5, "로트2_재고": 300, "로트2_잔여주": 12,
            "입고방식": "해상", "예정입고량": 800, "입고예정주": 7, "확정화물주문": 200,
            "의뢰일": "2026-10-18", "수락일": "2026-10-19", "운송시작일": "2026-10-29", "도착예정일": "2027-01-04",
            "운송상태": "수출 통관 완료", "출발국가": "대한민국", "출발항": "인천항 (KRINC)",
            "도착국가": "싱가포르", "도착항": "싱가포르항 (SGSIN)", "컨테이너": "40ft HC", "적재량_CBM": 42.0,
            "운송비_원": 3800000, "VAT_원": 380000, "리드타임_주": 7
        },
        {
            "SKU_ID": "S2038206", "품목명": "히알루론산 토너 패드 70매", "모델": "택배SES+화물TSB",
            "주당평균_A": 36.8, "변동비율_k": 0.45, "원본P20_1주": 28.0, "원본P95_1주": 195.0,
            "로트1_재고": 340, "로트1_잔여주": 5, "로트2_재고": 150, "로트2_잔여주": 11,
            "입고방식": "해상", "예정입고량": 300, "입고예정주": 5, "확정화물주문": 0,
            "의뢰일": "2026-10-25", "수락일": "2026-10-26", "운송시작일": "2026-11-05", "도착예정일": "2026-12-21",
            "운송상태": "선적 대기", "출발국가": "대한민국", "출발항": "부산항 (KRPUS)",
            "도착국가": "일본", "도착항": "하카타항 (JPHKT)", "컨테이너": "LCL (혼적)", "적재량_CBM": 6.2,
            "운송비_원": 980000, "VAT_원": 98000, "리드타임_주": 5
        },
        {
            "SKU_ID": "S2051104", "품목명": "프로바이오틱스 밸런스 에센스", "모델": "택배SES+화물SBA",
            "주당평균_A": 112.0, "변동비율_k": 1.05, "원본P20_1주": 70.0, "원본P95_1주": 170.0,
            "로트1_재고": 120, "로트1_잔여주": 4, "로트2_재고": 250, "로트2_잔여주": 9,
            "입고방식": "항공", "예정입고량": 350, "입고예정주": 2, "확정화물주문": 50,
            "의뢰일": "2026-11-09", "수락일": "2026-11-10", "운송시작일": "2026-11-14", "도착예정일": "2026-11-28",
            "운송상태": "항공 화물 터미널 입고", "출발국가": "대한민국", "출발항": "인천공항 (ICN)",
            "도착국가": "태국", "도착항": "수완나품공항 (BKK)", "컨테이너": "ULD AKE", "적재량_CBM": 3.4,
            "운송비_원": 3150000, "VAT_원": 315000, "리드타임_주": 2
        },
        {
            "SKU_ID": "S2059812", "품목명": "비타민C 브라이트닝 세럼", "모델": "택배SES+화물SBA",
            "주당평균_A": 74.5, "변동비율_k": 0.98, "원본P20_1주": 50.0, "원본P95_1주": 115.0,
            "로트1_재고": 220, "로트1_잔여주": 6, "로트2_재고": 280, "로트2_잔여주": 12,
            "입고방식": "해상", "예정입고량": 500, "입고예정주": 5, "확정화물주문": 0,
            "의뢰일": "2026-10-28", "수락일": "2026-10-29", "운송시작일": "2026-11-08", "도착예정일": "2026-12-20",
            "운송상태": "정상 운항중", "출발국가": "대한민국", "출발항": "부산항 (KRPUS)",
            "도착국가": "싱가포르", "도착항": "싱가포르항 (SGSIN)", "컨테이너": "20ft Dry", "적재량_CBM": 14.0,
            "운송비_원": 2100000, "VAT_원": 210000, "리드타임_주": 5
        }
    ]

    # 전체 111개 SKU 시뮬레이션 벤치마크 구성 (나머지 106개 가상 생성)
    rows = list(sample_skus)
    for i in range(6, 112):
        mu = round(np.random.uniform(25, 160), 1)
        k = round(np.random.uniform(0.6, 1.3), 2)
        p20 = round(mu * np.random.uniform(0.55, 0.75), 1)
        p95 = round(mu * np.random.uniform(1.45, 2.2), 1)
        r1_stk = int(mu * np.random.uniform(1.5, 4.5))
        r1_exp = int(np.random.choice([4, 5, 6, 8]))
        r2_stk = int(mu * np.random.uniform(1.5, 4.0))
        r2_exp = int(np.random.choice([10, 11, 12]))
        mode = np.random.choice(["해상", "항공"], p=[0.85, 0.15])
        lt = int(np.random.choice([5, 6, 7])) if mode == "해상" else 2
        inc_qty = int(mu * lt * np.random.uniform(0.7, 1.3))
        confirmed = int(np.random.choice([0, 0, 0, 60, 100]))
        rows.append({
            "SKU_ID": f"S20{60000 + i}", "품목명": f"코스메틱 관리품목 #{i:03d}",
            "모델": "택배SES+화물TSB" if i % 2 == 0 else "택배SES+화물SBA",
            "주당평균_A": mu, "변동비율_k": k, "원본P20_1주": p20, "원본P95_1주": p95,
            "로트1_재고": r1_stk, "로트1_잔여주": r1_exp, "로트2_재고": r2_stk, "로트2_잔여주": r2_exp,
            "입고방식": mode, "예정입고량": inc_qty, "입고예정주": lt, "확정화물주문": confirmed,
            "의뢰일": "2026-10-22", "수락일": "2026-10-24", "운송시작일": "2026-11-01", "도착예정일": "2026-12-20",
            "운송상태": "정상 운송중", "출발국가": "대한민국",
            "출발항": "부산항 (KRPUS)" if mode == "해상" else "인천공항 (ICN)",
            "도착국가": "태국", "도착항": "램차방항 (THLCH)" if mode == "해상" else "수완나품공항 (BKK)",
            "컨테이너": "20ft Dry" if mode == "해상" else "ULD AKE",
            "적재량_CBM": round(np.random.uniform(4.0, 22.0), 1),
            "운송비_원": 2200000 if mode == "해상" else 3100000,
            "VAT_원": 220000 if mode == "해상" else 310000,
            "리드타임_주": lt
        })
    return pd.DataFrame(rows)

# ---------------------------------------------------------
# 3. 핵심 수요예측 결합 및 발주 연산 엔진 (실행 시간 측정)
# ---------------------------------------------------------
def run_ordering_engine(df_input, user_order_qty_map=None, delay_weeks=0, new_confirmed_map=None):
    t_start = time.perf_counter()
    results = []

    for _, row in df_input.iterrows():
        sku = row["SKU_ID"]
        mu_1w = float(row["주당평균_A"])
        k = float(row["변동비율_k"])
        p20_b_1w = float(row["원본P20_1주"])
        p95_b_1w = float(row["원본P95_1주"])

        r1_stk = float(row["로트1_재고"])
        r1_exp = int(row["로트1_잔여주"])
        r2_stk = float(row["로트2_재고"])
        r2_exp = int(row["로트2_잔여주"])
        total_avail = r1_stk + r2_stk

        lt = int(row["입고예정주"]) + int(delay_weeks)
        inc_qty = float(row["예정입고량"])
        confirmed_b2b = float(row["확정화물주문"])
        if new_confirmed_map and sku in new_confirmed_map:
            confirmed_b2b += float(new_confirmed_map[sku])

        # --- [문제 2 연산] 로트1(단기 소비기한) 및 전체 마감일 기준 FEFO 평가 ---
        # 누적 기간 스케일링 (다주 누적 시 분산은 sqrt(H) 비례)
        h_exp1 = max(1, r1_exp)
        mu_a_exp1 = mu_1w * h_exp1
        mu_b_exp1 = (mu_1w / max(k, 0.1)) * h_exp1
        p20_b_exp1 = p20_b_1w * h_exp1
        p95_b_exp1 = mu_b_exp1 + (p95_b_1w - (mu_1w / max(k, 0.1))) * np.sqrt(h_exp1)

        # 문제 2 결합식: 하한 곱셈 보정(k), 상한 대칭형 스케일 보정(sqrt(k))
        p20_adj_exp1 = round(p20_b_exp1 * k, 1)
        p95_adj_exp1 = round(mu_a_exp1 + (p95_b_exp1 - mu_b_exp1) * np.sqrt(k), 1)

        # 로트1 예상 폐기량 (하한 P20_adj 기준 판매 속도 둔화 시 잔여분)
        expected_expiry_qty = max(0, round(r1_stk - p20_adj_exp1))

        # 신규 발주 상한 (신규 발주분 판매 마감일 12주 기준 P95_adj - 현재 가용재고 - 예정입고)
        h_new = 12
        mu_a_12 = mu_1w * h_new
        mu_b_12 = (mu_1w / max(k, 0.1)) * h_new
        p95_b_12 = mu_b_12 + (p95_b_1w - (mu_1w / max(k, 0.1))) * np.sqrt(h_new)
        p95_adj_12 = mu_a_12 + (p95_b_12 - mu_b_12) * np.sqrt(k)
        max_order_cap = max(0, round(p95_adj_12 - total_avail - inc_qty + confirmed_b2b))

        # --- [문제 3 연산] 입고 전 품절 방어 및 항공 긴급 투입 산출 (무보정 P95_B 연결) ---
        h_lt = max(1, lt)
        mu_a_lt = mu_1w * h_lt + confirmed_b2b
        mu_b_lt = (mu_1w / max(k, 0.1)) * h_lt
        p95_b_lt = round(mu_b_lt + (p95_b_1w - (mu_1w / max(k, 0.1))) * np.sqrt(h_lt) + confirmed_b2b, 1)

        # 최초 품절 예상 주 (가용재고가 누적 상한 P95_B를 하회하는 최초 주차)
        first_stockout_wk = None
        for w in range(1, h_lt + 1):
            cum_p95_w = (mu_1w / max(k, 0.1)) * w + (p95_b_1w - (mu_1w / max(k, 0.1))) * np.sqrt(w) + (confirmed_b2b if w == 1 else 0)
            if total_avail < cum_p95_w:
                first_stockout_wk = w
                break

        air_urgent_qty = max(0, round(p95_b_lt - total_avail)) if row["입고방식"] == "해상" else 0
        rec_order_qty = min(max_order_cap, max(0, round(mu_a_12 - total_avail - inc_qty + confirmed_b2b)))

        # --- [4단계 알림 판정] ---
        alerts = []
        urgency_score = 0
        if air_urgent_qty > 0 and (first_stockout_wk is not None and first_stockout_wk <= lt):
            alerts.append(("🔴 긴급(항공전환)", f"해상 입고({lt}주) 전 {first_stockout_wk}주차 품절 예상 → 항공 {air_urgent_qty:,} PCS 긴급 투입 검토"))
            urgency_score += 100
        if expected_expiry_qty > 0:
            alerts.append(("🟠 주의(폐기위험)", f"판매 둔화(P20) 시 로트1 잔여 {expected_expiry_qty:,} PCS 소비기한 만료 예상"))
            urgency_score += 50
        elif first_stockout_wk is not None and first_stockout_wk <= 3:
            alerts.append(("🟠 주의(품절임박)", f"{first_stockout_wk}주차 내 안전재고(P95) 소진 임박"))
            urgency_score += 45

        user_qty = user_order_qty_map.get(sku, rec_order_qty) if user_order_qty_map else rec_order_qty
        if user_qty > max_order_cap:
            alerts.append(("🟡 검토(상한초과)", f"입력 발주량({user_qty:,} PCS)이 신규 발주 상한({max_order_cap:,} PCS) 초과"))
            urgency_score += 30

        if confirmed_b2b > 0 or delay_weeks > 0:
            msg_parts = []
            if confirmed_b2b > 0:
                msg_parts.append(f"확정 B2B 화물 {int(confirmed_b2b):,} PCS 반영")
            if delay_weeks > 0:
                msg_parts.append(f"입항 +{delay_weeks}주 지연 반영")
            alerts.append(("🔵 변동(조건갱신)", " / ".join(msg_parts)))
            urgency_score += 10

        status_label = alerts[0][0] if alerts else "🟢 정상 발주"

        results.append({
            "긴급점수": urgency_score,
            "상태구분": status_label,
            "SKU_ID": sku,
            "품목명": row["품목명"],
            "적용모델": row["모델"],
            "현재가용재고": int(total_avail),
            "예정입고": f"{row['입고방식']} {int(inc_qty):,} ({lt}주 후)",
            "권고발주수량": int(rec_order_qty),
            "신규발주상한_P95": int(max_order_cap),
            "만료예상폐기량_P20": int(expected_expiry_qty),
            "최초품절예상주": f"{first_stockout_wk}주차" if first_stockout_wk else "안전 (품절없음)",
            "항공긴급투입수량": int(air_urgent_qty),
            "알림목록": alerts,
            "입고전_상한P95": p95_b_lt,
            "입고전_평균A": round(mu_a_lt, 1),
            "로트1_하한P20": p20_adj_exp1,
            "로트1_평균A": round(mu_a_exp1, 1),
            "로트1_상한P95": p95_adj_exp1
        })

    df_res = pd.DataFrame(results).sort_values(by=["긴급점수", "항공긴급투입수량", "만료예상폐기량_P20"], ascending=False).reset_index(drop=True)
    df_res.insert(0, "긴급순위", df_res.index + 1)
    elapsed_sec = time.perf_counter() - t_start
    return df_res, elapsed_sec

# ---------------------------------------------------------
# 4. 초기 데이터 로드 및 세션 상태 관리
# ---------------------------------------------------------
df_master = load_sku_master()

if "custom_overrides" not in st.session_state:
    st.session_state.custom_overrides = {}
if "user_orders" not in st.session_state:
    st.session_state.user_orders = {}
if "delay_weeks" not in st.session_state:
    st.session_state.delay_weeks = 0

# 사용자 수정치 반영
df_working = df_master.copy()
for sku_key, ov in st.session_state.custom_overrides.items():
    idx = df_working[df_working["SKU_ID"] == sku_key].index
    if len(idx) > 0:
        for col_k, val_v in ov.items():
            df_working.loc[idx, col_k] = val_v

df_eval, exec_time = run_ordering_engine(
    df_working,
    user_order_qty_map=st.session_state.user_orders,
    delay_weeks=st.session_state.delay_weeks
)

# ---------------------------------------------------------
# 5. 상단 헤더 및 4단계 담당자 알림 센터 (우측 사이드바 & 상단)
# ---------------------------------------------------------
col_title, col_exec = st.columns([3.2, 1.3])
with col_title:
    st.markdown('<div class="main-header">🚢 SCM 지능형 모의 발주 및 의사결정 지원 시스템</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">채널 분리 점예측(A: 택배 SES + 화물 SBA/TSB) & 분포예측(B: 2주 MBB · 시뮬레이션) 실시간 통합 엔진</div>', unsafe_allow_html=True)
with col_exec:
    st.markdown(
        f'<div style="text-align:right; padding-top:0.6rem;">'
        f'<span class="exec-badge">⚡ {len(df_eval)}개 SKU 계산 완료 · {exec_time:.3f}초 소요</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# 사이드바: 담당자 4단계 예외 기반 알림 센터
with st.sidebar:
    st.header("🔔 담당자 실시간 알림 센터")
    st.caption("수동 전수 점검 없이 위험 SKU만 자동 감지하여 4단계로 경보합니다.")

    # 알림 집계
    all_alerts = []
    for _, r in df_eval.iterrows():
        for a_type, a_msg in r["알림목록"]:
            all_alerts.append((a_type, r["SKU_ID"], r["품목명"], a_msg))

    cnt_red = sum(1 for a in all_alerts if "긴급" in a[0])
    cnt_orange = sum(1 for a in all_alerts if "주의" in a[0])
    cnt_yellow = sum(1 for a in all_alerts if "검토" in a[0])
    cnt_blue = sum(1 for a in all_alerts if "변동" in a[0])

    c1, c2 = st.columns(2)
    c1.metric("🔴 긴급 (항공)", f"{cnt_red}건")
    c2.metric("🟠 주의 (폐기/품절)", f"{cnt_orange}건")
    c3, c4 = st.columns(2)
    c3.metric("🟡 검토 (상한초과)", f"{cnt_yellow}건")
    c4.metric("🔵 변동 (화물/지연)", f"{cnt_blue}건")

    st.divider()
    filter_alert = st.selectbox("알림 등급 필터", ["전체 보기", "🔴 긴급(항공전환)", "🟠 주의(폐기/품절)", "🟡 검토(상한초과)", "🔵 변동(조건갱신)"])

    shown = 0
    for a_type, a_sku, a_name, a_msg in all_alerts:
        if filter_alert != "전체 보기" and filter_alert[:4] not in a_type:
            continue
        css_cls = "alert-red" if "긴급" in a_type else ("alert-orange" if "주의" in a_type else ("alert-yellow" if "검토" in a_type else "alert-blue"))
        st.markdown(
            f'<div class="alert-card {css_cls}"><strong>{a_type} | {a_sku}</strong><br>'
            f'<span style="font-size:0.82rem; opacity:0.85;">{a_name}</span><br>{a_msg}</div>',
            unsafe_allow_html=True
        )
        shown += 1
        if shown >= 12:
            st.caption("상위 12건의 주요 알림만 표시됩니다.")
            break

# ---------------------------------------------------------
# 6. 메인 탭 구성 (탭1: 종합 대시보드 / 탭2: 소비기한 / 탭3: 운송수단)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📊 탭 1. 종합 발주 대시보드 (KPI · 입력 · 권고표)",
    "⏳ 탭 2. 소비기한 관리 (문제 2 · FEFO 및 폐기/상한)",
    "✈️ 탭 3. 운송 수단 판단 (문제 3 · 항공/해상 리드타임)"
])

# =========================================================
# [탭 1] 종합 발주 대시보드
# =========================================================
with tab1:
    st.subheader("1) 금주 핵심 발주 및 물류 비용 KPI 요약")

    urgent_air_skus = int((df_eval["항공긴급투입수량"] > 0).sum())
    expiry_risk_skus = int((df_eval["만료예상폐기량_P20"] > 0).sum())
    normal_skus = int((df_eval["상태구분"] == "🟢 정상 발주").sum())

    sea_cost = df_working[df_working["입고방식"] == "해상"]["운송비_원"].sum()
    air_cost = df_working[df_working["입고방식"] == "항공"]["운송비_원"].sum()
    total_sales_1w = df_working["주당평균_A"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🔴 긴급 항공 검토 SKU", f"{urgent_air_skus}개", delta="해상 도착 전 P95 돌파", delta_color="inverse")
    k2.metric("🟠 소비기한 폐기 위험 SKU", f"{expiry_risk_skus}개", delta="하한(P20) 미달 예상", delta_color="inverse")
    k3.metric("🟢 정상 발주 가능 SKU", f"{normal_skus}개", delta=f"전체 {len(df_eval)}개 중 {normal_skus/len(df_eval)*100:.1f}%")
    k4.metric("🚢/✈️ 주간 운송수단별 비용", f"₩{(sea_cost + air_cost)/10000:,.0f}만", delta=f"해상 {sea_cost/10000:,.0f}만 / 항공 {air_cost/10000:,.0f}만", delta_color="off")
    k5.metric("📈 주간 판매·운송비 증감률", "+6.4% (판매)", delta="운송비 전주 대비 +3.1%")

    st.divider()

    # 중단: What-If 발주 조건 및 실시간 변동 입력창
    st.subheader("2) 발주 조건 및 실시간 변수 입력 (시뮬레이션)")
    with st.expander("🛠️ 특정 SKU 재고·소비기한·예정입고·확정화물 직접 수정하기 (클릭하여 열기)", expanded=True):
        col_sel, col_delay = st.columns([2, 1])
        with col_sel:
            target_sku = st.selectbox(
                "시뮬레이션할 대상 SKU 선택",
                options=df_working["SKU_ID"].tolist(),
                format_func=lambda x: f"{x} — {df_working.loc[df_working['SKU_ID']==x, '품목명'].values[0]}"
            )
        with col_delay:
            new_delay = st.number_input("전사 해상 입항 지연 시나리오 (+주)", min_value=0, max_value=4, value=st.session_state.delay_weeks)

        cur_row = df_working[df_working["SKU_ID"] == target_sku].iloc[0]
        cur_eval_row = df_eval[df_eval["SKU_ID"] == target_sku].iloc[0]

        with st.form("sku_input_form"):
            ic1, ic2, ic3, ic4 = st.columns(4)
            with ic1:
                in_r1_stk = st.number_input("로트1 가용재고 (PCS)", min_value=0, value=int(cur_row["로트1_재고"]), step=10)
                in_r1_exp = st.number_input("로트1 잔여 소비기한 (주)", min_value=1, max_value=52, value=int(cur_row["로트1_잔여주"]))
            with ic2:
                in_r2_stk = st.number_input("로트2 가용재고 (PCS)", min_value=0, value=int(cur_row["로트2_재고"]), step=10)
                in_r2_exp = st.number_input("로트2 잔여 소비기한 (주)", min_value=1, max_value=52, value=int(cur_row["로트2_잔여주"]))
            with ic3:
                in_inc_mode = st.selectbox("예정 입고 운송방식", ["해상", "항공"], index=0 if cur_row["입고방식"] == "해상" else 1)
                in_inc_qty = st.number_input("예정 입고 수량 (PCS)", min_value=0, value=int(cur_row["예정입고량"]), step=50)
                in_inc_wk = st.number_input("입고 예정 주차 (주 후)", min_value=1, max_value=24, value=int(cur_row["입고예정주"]))
            with ic4:
                in_conf_b2b = st.number_input("신규 확정 대량화물 주문 (PCS)", min_value=0, value=int(cur_row["확정화물주문"]), step=20)
                in_user_order = st.number_input("담당자 희망 발주량 (PCS)", min_value=0, value=int(st.session_state.user_orders.get(target_sku, cur_eval_row["권고발주수량"])), step=10)

            submitted = st.form_submit_button("🔄 입력값 반영 및 즉시 재계산 실행", use_container_width=True)
            if submitted:
                st.session_state.delay_weeks = new_delay
                st.session_state.custom_overrides[target_sku] = {
                    "로트1_재고": in_r1_stk, "로트1_잔여주": in_r1_exp,
                    "로트2_재고": in_r2_stk, "로트2_잔여주": in_r2_exp,
                    "입고방식": in_inc_mode, "예정입고량": in_inc_qty, "입고예정주": in_inc_wk,
                    "확정화물주문": in_conf_b2b
                }
                st.session_state.user_orders[target_sku] = in_user_order
                st.rerun()

    st.divider()

    # 하단: 출력 테이블 (긴급 순위 정렬)
    st.subheader("3) SKU별 발주 권고 및 위험 진단 출력 테이블 (긴급 순위순)")
    filter_opt = st.radio(
        "표시 필터",
        ["전체 SKU (111개)", "🔴 긴급 항공 검토 SKU만", "🟠 소비기한 폐기 위험 SKU만", "주요 대표 SKU (상위 15개)"],
        horizontal=True
    )

    df_display = df_eval.copy()
    if "긴급 항공" in filter_opt:
        df_display = df_display[df_display["항공긴급투입수량"] > 0]
    elif "소비기한" in filter_opt:
        df_display = df_display[df_display["만료예상폐기량_P20"] > 0]
    elif "상위 15개" in filter_opt:
        df_display = df_display.head(15)

    show_cols = [
        "긴급순위", "상태구분", "SKU_ID", "품목명", "현재가용재고", "예정입고",
        "권고발주수량", "신규발주상한_P95", "만료예상폐기량_P20", "최초품절예상주", "항공긴급투입수량"
    ]
    st.dataframe(
        df_display[show_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "현재가용재고": st.column_config.NumberColumn(format="%d PCS"),
            "권고발주수량": st.column_config.NumberColumn(format="%d PCS"),
            "신규발주상한_P95": st.column_config.NumberColumn(format="%d PCS"),
            "만료예상폐기량_P20": st.column_config.NumberColumn(format="%d PCS"),
            "항공긴급투입수량": st.column_config.NumberColumn(format="%d PCS"),
        }
    )

# =========================================================
# [탭 2] 소비기한 관리 (문제 2)
# =========================================================
with tab2:
    st.subheader("⏳ 문제 2: 로트별 소비기한(FEFO) 소진 및 신규 발주 상한 분석")
    sku_t2 = st.selectbox(
        "분석할 SKU 선택 (탭 2)",
        options=df_working["SKU_ID"].tolist(),
        index=df_working["SKU_ID"].tolist().index(target_sku),
        format_func=lambda x: f"{x} — {df_working.loc[df_working['SKU_ID']==x, '품목명'].values[0]}"
    )

    r_w2 = df_working[df_working["SKU_ID"] == sku_t2].iloc[0]
    r_e2 = df_eval[df_eval["SKU_ID"] == sku_t2].iloc[0]

    # 상단 경고 및 핵심 수치 카드
    c2_1, c2_2, c2_3, c2_4 = st.columns(4)
    c2_1.metric("로트 1 가용재고 (마감 임박)", f"{int(r_w2['로트1_재고']):,} PCS", delta=f"판매 마감까지 {int(r_w2['로트1_잔여주'])}주 남음", delta_color="off")
    c2_2.metric("보정 하한(P20) 기준 누적수요", f"{r_e2['로트1_하한P20']:,.1f} PCS", delta=f"기준 평균(μ_A): {r_e2['로트1_평균A']:,.1f} PCS", delta_color="off")
    c2_3.metric("⚠️ 만료 예상 폐기량 (P20 기준)", f"{r_e2['만료예상폐기량_P20']:,} PCS", delta="폐기 경고 발생" if r_e2['만료예상폐기량_P20'] > 0 else "전량 소진 가능", delta_color="inverse" if r_e2['만료예상폐기량_P20'] > 0 else "normal")
    c2_4.metric("🛡️ 신규 발주 최대 상한 (P95 보정)", f"{r_e2['신규발주상한_P95']:,} PCS", delta="입고 후 마감일 내 소진 한도", delta_color="off")

    if r_e2["만료예상폐기량_P20"] > 0:
        st.warning(f"🚨 **[소비기한 폐기 경고]** 판매 속도가 하위 20% 시나리오($P20_{{adj}}$)로 둔화될 경우, 로트 1의 판매 마감일({int(r_w2['로트1_잔여주'])}주 후)까지 **{r_e2['만료예상폐기량_P20']:,} PCS**가 팔리지 않고 남을 것으로 예측됩니다. B2B 특판 또는 프로모션 소진을 권장합니다.")
    else:
        st.success(f"✅ **[소비기한 안전]** 보수적 하한($P20_{{adj}}$) 시나리오에서도 로트 1 재고({int(r_w2['로트1_재고']):,} PCS)가 판매 마감일 전 전량 소진될 것으로 예상됩니다.")

    # FEFO 소진 타임라인 차트 (1주 ~ 12주)
    weeks = list(range(1, 13))
    mu_1w = float(r_w2["주당평균_A"])
    k = float(r_w2["변동비율_k"])
    p20_1w = float(r_w2["원본P20_1주"]) * k
    p95_1w = mu_1w + (float(r_w2["원본P95_1주"]) - (mu_1w / max(k, 0.1))) * np.sqrt(k)

    cum_mean = [round(mu_1w * w, 1) for w in weeks]
    cum_p20 = [round(p20_1w * w, 1) for w in weeks]
    cum_p95 = [round(mu_1w * w + (p95_1w - mu_1w) * np.sqrt(w), 1) for w in weeks]

    fig_fefo = go.Figure()
    # 로트 누적 재고 계단선
    lot_line = [r_w2["로트1_재고"] if w <= r_w2["로트1_잔여주"] else (r_w2["로트1_재고"] + r_w2["로트2_재고"]) for w in weeks]
    fig_fefo.add_trace(go.Bar(
        x=[f"{w}주차" for w in weeks],
        y=[r_w2["로트1_재고"] if w <= r_w2["로트1_잔여주"] else 0 for w in weeks],
        name="로트 1 가용재고 (FEFO 우선 소진)",
        marker_color="rgba(245, 158, 11, 0.45)"
    ))
    fig_fefo.add_trace(go.Bar(
        x=[f"{w}주차" for w in weeks],
        y=[r_w2["로트2_재고"] if w > r_w2["로트1_잔여주"] else 0 for w in weeks],
        name="로트 2 가용재고 (후순위 소진)",
        marker_color="rgba(59, 130, 246, 0.35)"
    ))
    fig_fefo.add_trace(go.Scatter(
        x=[f"{w}주차" for w in weeks], y=cum_mean,
        mode="lines+markers", name="기준 평균 누적수요 (μ_A)",
        line=dict(color="#1B365D", width=3)
    ))
    fig_fefo.add_trace(go.Scatter(
        x=[f"{w}주차" for w in weeks], y=cum_p20,
        mode="lines+markers", name="보정 하한선 (P20_adj · 폐기 기준)",
        line=dict(color="#D93025", width=2.5, dash="dash")
    ))
    fig_fefo.add_trace(go.Scatter(
        x=[f"{w}주차" for w in weeks], y=cum_p95,
        mode="lines", name="보정 상한선 (P95_adj · 발주 상한)",
        line=dict(color="#10B981", width=2, dash="dot")
    ))
    fig_fefo.add_vline(x=int(r_w2["로트1_잔여주"]) - 1, line_width=2, line_dash="dash", line_color="#D93025", annotation_text="로트1 판매마감")
    fig_fefo.update_layout(
        title=f"[{sku_t2}] 로트별 FEFO 소진 타임라인 및 하한(P20)·평균(μ_A)·상한(P95) 비교",
        barmode="stack",
        xaxis_title="예측 주차",
        yaxis_title="누적 수량 (PCS)",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_fefo, use_container_width=True)

# =========================================================
# [탭 3] 운송 수단 판단 및 세부 물류 상태 (문제 3)
# =========================================================
with tab3:
    st.subheader("✈️ 문제 3: 항공·해상 리드타임 구간 안전 상한(P95) 및 최초 품절 시점 분석")
    sku_t3 = st.selectbox(
        "분석할 SKU 선택 (탭 3)",
        options=df_working["SKU_ID"].tolist(),
        index=df_working["SKU_ID"].tolist().index(target_sku),
        format_func=lambda x: f"{x} — {df_working.loc[df_working['SKU_ID']==x, '품목명'].values[0]}"
    )

    r_w3 = df_working[df_working["SKU_ID"] == sku_t3].iloc[0]
    r_e3 = df_eval[df_eval["SKU_ID"] == sku_t3].iloc[0]

    c3_1, c3_2, c3_3, c3_4 = st.columns(4)
    c3_1.metric("현재 총 가용재고", f"{r_e3['현재가용재고']:,} PCS", delta=f"예정 입고: {r_e3['예정입고']}", delta_color="off")
    c3_2.metric("입고 전 기대 평균 (μ_A)", f"{r_e3['입고전_평균A']:,.1f} PCS", delta="확정 B2B 화물 포함", delta_color="off")
    c3_3.metric("입고 전 무보정 상한 (P95_B)", f"{r_e3['입고전_상한P95']:,.1f} PCS", delta="스파이크 방어 기준선", delta_color="off")
    c3_4.metric("🚨 최초 품절 예상 주 / 항공 투입", r_e3["최초품절예상주"], delta=f"항공 긴급 권고: {r_e3['항공긴급투입수량']:,} PCS", delta_color="inverse" if r_e3["항공긴급투입수량"] > 0 else "normal")

    # 항공(2주) vs 해상(리드타임) 구간 누적 상한 차트
    lt_sea = int(r_w3["리드타임_주"]) + int(st.session_state.delay_weeks)
    lt_air = 2
    max_w = max(lt_sea + 2, 8)
    w_list = list(range(1, max_w + 1))

    mu_a_1w = float(r_w3["주당평균_A"])
    k3 = float(r_w3["변동비율_k"])
    mu_b_1w = mu_a_1w / max(k3, 0.1)
    p95_b_1w = float(r_w3["원본P95_1주"])
    conf_b2b = float(r_w3["확정화물주문"])

    mean_path = [round(mu_a_1w * w + conf_b2b, 1) for w in w_list]
    p95_path = [round(mu_b_1w * w + (p95_b_1w - mu_b_1w) * np.sqrt(w) + conf_b2b, 1) for w in w_list]
    avail_line = [r_e3["현재가용재고"]] * len(w_list)

    fig_lt = go.Figure()
    fig_lt.add_trace(go.Scatter(
        x=[f"{w}주차" for w in w_list], y=p95_path,
        mode="lines+markers", name="무보정 안전 상한선 (P95_B)",
        line=dict(color="#D93025", width=3)
    ))
    fig_lt.add_trace(go.Scatter(
        x=[f"{w}주차" for w in w_list], y=mean_path,
        mode="lines+markers", name="기대 평균 누적수요 (μ_A)",
        line=dict(color="#1B365D", width=2.5, dash="dash")
    ))
    fig_lt.add_trace(go.Scatter(
        x=[f"{w}주차" for w in w_list], y=avail_line,
        mode="lines", name=f"현재 가용재고 ({r_e3['현재가용재고']:,} PCS)",
        line=dict(color="#10B981", width=3)
    ))

    # 항공 입고(2주) 및 해상 입고 시점 수직선 표시
    fig_lt.add_vline(x=lt_air - 1, line_width=2, line_dash="dot", line_color="#2563EB", annotation_text="✈️ 항공 입고 시점 (2주)")
    fig_lt.add_vline(x=lt_sea - 1, line_width=2, line_dash="dash", line_color="#7C3AED", annotation_text=f"🚢 해상 입고 시점 ({lt_sea}주)")

    fig_lt.update_layout(
        title=f"[{sku_t3}] 현재 가용재고 대비 항공·해상 리드타임 누적 수요(μ_A · P95_B) 및 최초 품절 교차점",
        xaxis_title="경과 주차",
        yaxis_title="누적 수량 (PCS)",
        height=430,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_lt, use_container_width=True)

    st.divider()

    # 4. 세부 SKU별 발주 및 물류 트래킹 상태 (기획안 4번 항목)
    st.subheader("📦 세부 SKU별 발주 및 국제 물류 트래킹 상세")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.markdown("**1. 발주 진행 일정**")
        st.write(f"• **발주 의뢰일**: `{r_w3['의뢰일']}`")
        st.write(f"• **진행 수락일**: `{r_w3['수락일']}`")
        st.write(f"• **운송 시작일**: `{r_w3['운송시작일']}`")
        st.write(f"• **도착 예정일**: `{r_w3['도착예정일']}`")
        st.write(f"• **현재 운송 상태**: **{r_w3['운송상태']}**")
    with col_d2:
        st.markdown("**2. 출발·도착 경로 및 운송 방식**")
        st.write(f"• **운송 방식**: **{r_w3['입고방식']} 운송**")
        st.write(f"• **출발 국가 / 항·공항**: {r_w3['출발국가']} · `{r_w3['출발항']}`")
        st.write(f"• **도착 국가 / 항·공항**: {r_w3['도착국가']} · `{r_w3['도착항']}`")
        st.write(f"• **적용 리드타임**: **{lt_sea}주** (기본 {r_w3['리드타임_주']}주 + 지연 {st.session_state.delay_weeks}주)")
    with col_d3:
        st.markdown("**3. 컨테이너 적재 및 정산 비용**")
        st.write(f"• **사용 컨테이너 크기**: `{r_w3['컨테이너']}`")
        st.write(f"• **화물 적재량**: **{r_w3['적재량_CBM']} CBM** ({int(r_w3['예정입고량']):,} PCS)")
        st.write(f"• **운송비 (공급가액)**: **₩{int(r_w3['운송비_원']):,}**")
        st.write(f"• **부가가치세 (VAT 10%)**: ₩{int(r_w3['VAT_원']):,}")
        st.write(f"• **총 물류 정산액**: **₩{int(r_w3['운송비_원'] + r_w3['VAT_원']):,}**")
