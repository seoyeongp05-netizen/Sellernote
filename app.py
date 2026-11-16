import time
import datetime
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. 페이지 설정 및 SELLERNOTE 딥그린 테마 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="셀러노트 | 발주 프로그램",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .top-banner {
        background-color: #153D34;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.2rem;
    }
    .brand-title { font-size: 1.35rem; font-weight: 800; letter-spacing: 0.04em; }
    .demo-badge {
        font-size: 0.8rem;
        border: 1px solid #78958A;
        border-radius: 20px;
        padding: 4px 12px;
        color: #E1EFE8;
    }
    .exec-badge {
        display: inline-block;
        background-color: #E1EFE8;
        color: #096351;
        border: 1px solid #A9C4BA;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .step-header {
        background-color: #F0F6F3;
        border-left: 4px solid #096351;
        padding: 0.55rem 0.9rem;
        font-weight: 800;
        color: #153D34;
        border-radius: 0 8px 8px 0;
        margin: 0.8rem 0 0.6rem 0;
    }
    .date-preview {
        background-color: #E6F2ED;
        color: #096351;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        margin-top: 2px;
    }
    .alert-card {
        padding: 0.75rem 0.95rem;
        border-radius: 8px;
        margin-bottom: 0.55rem;
        font-size: 0.88rem;
        line-height: 1.45;
    }
    .alert-red { background-color: #FCE5E4; border-left: 5px solid #D93025; color: #7F1D1D; }
    .alert-orange { background-color: #FFEAD8; border-left: 5px solid #F59E0B; color: #78350F; }
    .alert-yellow { background-color: #FFF3CA; border-left: 5px solid #EAB308; color: #713F12; }
    .alert-blue { background-color: #E2ECFF; border-left: 5px solid #2563EB; color: #1E3A8A; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #D9E5DF;
        padding: 0.9rem 1.1rem;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

BASE_DATE = datetime.date(2026, 11, 16)

def fmt_md(days: int) -> str:
    target = BASE_DATE + datetime.timedelta(days=int(days))
    return target.strftime("%m.%d")

# ---------------------------------------------------------
# 2. 초기 예시 데이터 구성
# ---------------------------------------------------------
def get_initial_data():
    return [
        {
            "id": "SN-101", "name": "쯔유 500 mL",
            "forecast": [[75, 112, 315], [80, 118, 330], [78, 116, 320], [81, 120, 310]],
            "ship": [105, 118],
            "lots": [
                {"id": "YY-01", "qty": 110, "expiry": 22, "deadline": 22},
                {"id": "YY-02", "qty": 290, "expiry": 122, "deadline": 122}
            ],
            "inbound": [{"mode": "해상", "day": 34, "qty": 420, "expiry": 170, "deadline": 170}],
            "b2b": [{"day": 6, "qty": 80}],
            "planned": 300,
            "terms": {"air": 6, "sea": 42, "window": 100, "review": 14, "leadSD": 5, "cycle": 30},
            "costs": {"air": [0, 140000], "sea": [310000, 320000]},
            "records": [{
                "request": -30, "accepted": -29, "depart": -20, "eta": 34,
                "status": "운송 중", "mode": "해상", "route": "일본 · 오사카항 → 한국 · 부산항",
                "container": "20ft LCL", "load": "1.2 CBM", "cost": 320000, "vat": 32000
            }]
        },
        {
            "id": "SN-202", "name": "롤드 오트밀 500 g",
            "forecast": [[42, 64, 83], [46, 69, 91], [44, 66, 90], [42, 65, 86]],
            "ship": [75, 62],
            "lots": [
                {"id": "OT-01", "qty": 310, "expiry": 11, "deadline": 11},
                {"id": "OT-02", "qty": 250, "expiry": 130, "deadline": 130}
            ],
            "inbound": [{"mode": "해상", "day": 30, "qty": 280, "expiry": 120, "deadline": 120}],
            "b2b": [],
            "planned": 480,
            "terms": {"air": 8, "sea": 52, "window": 55, "review": 14, "leadSD": 8, "cycle": 30},
            "costs": {"air": [0, 0], "sea": [400000, 0]},
            "records": [{
                "request": -35, "accepted": -34, "depart": -25, "eta": 30,
                "status": "운송 중", "mode": "해상", "route": "폴란드 · 그단스크항 → 한국 · 부산항",
                "container": "20ft LCL", "load": "1.8 CBM", "cost": 410000, "vat": 41000
            }]
        },
        {
            "id": "SN-303", "name": "트러플 오일 250 mL",
            "forecast": [[25, 44, 62], [29, 46, 65], [27, 45, 63], [30, 48, 67]],
            "ship": [41, 45],
            "lots": [{"id": "TR-01", "qty": 300, "expiry": 150, "deadline": 150}],
            "inbound": [
                {"mode": "항공", "day": 12, "qty": 160, "expiry": 130, "deadline": 130},
                {"mode": "해상", "day": 49, "qty": 40, "expiry": 180, "deadline": 180}
            ],
            "b2b": [],
            "planned": 60,
            "terms": {"air": 7, "sea": 56, "window": 70, "review": 14, "leadSD": 6, "cycle": 30},
            "costs": {"air": [220000, 155000], "sea": [0, 290000]},
            "records": [
                {
                    "request": -10, "accepted": -9, "depart": -4, "eta": 12,
                    "status": "운송 중", "mode": "항공", "route": "이탈리아 · 밀라노 공항 → 한국 · 인천공항",
                    "container": "항공 혼재", "load": "64 kg", "cost": 155000, "vat": 15500
                },
                {
                    "request": -28, "accepted": -27, "depart": -18, "eta": 49,
                    "status": "운송 중", "mode": "해상", "route": "이탈리아 · 제노바항 → 한국 · 부산항",
                    "container": "20ft LCL", "load": "0.9 CBM", "cost": 290000, "vat": 29000
                }
            ]
        }
    ]

if "sku_data" not in st.session_state:
    st.session_state.sku_data = get_initial_data()
if "events" not in st.session_state:
    st.session_state.events = []
if "sent_alerts" not in st.session_state:
    st.session_state.sent_alerts = set()
if "read_alerts" not in st.session_state:
    st.session_state.read_alerts = set()

# ---------------------------------------------------------
# 3. 핵심 시뮬레이션 및 발주 권고 연산 엔진
# ---------------------------------------------------------
def cutoff(lot):
    return min(lot["deadline"], lot.get("expiry", lot["deadline"]))

def daily_demand(sku, day, col):
    weeks = sku["forecast"]
    wk = day // 7
    if weeks:
        row = weeks[wk] if wk < len(weeks) else weeks[-1]
        return row[col] / 7.0
    prev_s, cur_s = sku["ship"]
    return [min(prev_s, cur_s), (prev_s + cur_s) / 2.0, max(prev_s, cur_s)][col] / 7.0

def simulate(sku, col, extra=None, horizon=180):
    extra = extra or []
    cur_lots = [{**l, "deadline": cutoff(l), "day": 0, "current": True} for l in sku["lots"]]
    fut_lots = [{**l, "deadline": cutoff(l), "id": f"입고 {i+1}", "current": False} for i, l in enumerate(sku["inbound"])]
    ext_lots = [{**l, "current": False} for l in extra]
    lots = [{**l, "left": float(l["qty"]), "sold": 0.0, "lost": 0.0, "first": None, "last": None} for l in (cur_lots + fut_lots + ext_lots)]

    arrivals = {}
    for l in lots:
        arrivals.setdefault(l["day"], []).append(l)

    booked = {}
    for o in sku["b2b"]:
        booked[o["day"]] = booked.get(o["day"], 0.0) + float(o["qty"])

    active = []
    total_demand = 0.0
    total_supply = 0.0
    first_gap = None
    lines = []
    miss = []

    for day in range(horizon):
        next_active = []
        for l in active:
            if l["deadline"] > day and l["left"] > 1e-7:
                next_active.append(l)
            elif l["deadline"] <= day:
                l["lost"] = l["left"]
                total_supply -= l["left"]
                l["left"] = 0.0
        active = next_active

        for l in arrivals.get(day, []):
            if l["deadline"] <= day:
                l["lost"] = l["left"]
                l["left"] = 0.0
                continue
            active.append(l)
            total_supply += l["left"]

        active.sort(key=lambda x: (x["deadline"], x["day"]))
        need = daily_demand(sku, day, col) + booked.get(day, 0.0)
        total_demand += need

        for l in active:
            if need <= 1e-7:
                break
            take = min(need, l["left"])
            if take <= 1e-7:
                continue
            if l["first"] is None:
                l["first"] = day
            l["last"] = day
            l["sold"] += take
            l["left"] -= take
            need -= take

        if need > 1e-7 and first_gap is None:
            first_gap = day
        miss.append(max(0.0, need))
        lines.append((total_demand, total_supply))

    return {"lots": lots, "lines": lines, "miss": miss, "firstGap": first_gap}

def evaluate_all(data_list):
    t0 = time.perf_counter()
    results = []
    for sku in data_list:
        t = sku["terms"]
        air = t["air"]
        sea_days = [l["day"] for l in sku["inbound"] if l["mode"] == "해상"]
        sea_day = min(sea_days) if sea_days else t["sea"]

        max_d = max(
            [1]
            + [l["deadline"] for l in sku["lots"]]
            + [l["deadline"] for l in sku["inbound"]]
            + [t["sea"] + t["window"], sea_day + 1, air + 1]
        ) + 1

        p20 = simulate(sku, 0, horizon=max_d)
        mean = simulate(sku, 1, horizon=max_d)
        p95 = simulate(sku, 2, horizon=max_d)

        cand = {"id": "신규 해상 발주", "qty": 1e12, "day": t["sea"], "deadline": t["sea"] + t["window"]}
        cap_sim = simulate(sku, 0, extra=[cand], horizon=max_d)
        cap = max(0, int(np.floor(cap_sim["lots"][-1]["sold"] + 1e-7)))

        waste_lots = [l for l in p20["lots"] if l["current"]]
        waste = int(np.ceil(sum(l["lost"] for l in waste_lots) - 1e-7))

        first = p95["firstGap"] if (p95["firstGap"] is not None and p95["firstGap"] < sea_day) else None
        air_qty = 0 if (first is None or air >= sea_day) else int(np.ceil(sum(p95["miss"][air:sea_day]) - 1e-7))

        day_mean = sum(daily_demand(sku, d, 1) for d in range(7)) / 7.0
        booked_lt = sum(o["qty"] for o in sku["b2b"] if o["day"] < t["sea"] + t["review"])
        pos = sum(l["qty"] for l in sku["lots"] if cutoff(l) > 0) + sum(
            l["qty"] for l in sku["inbound"] if l["day"] < t["sea"] + t["review"] and cutoff(l) > l["day"]
        )
        sd_part = max(0.0, daily_demand(sku, 0, 2) - day_mean) / 1.65 * np.sqrt(t["sea"] + t["review"])
        safety = 1.65 * np.hypot(sd_part, day_mean * t["leadSD"])
        reorder = day_mean * (t["sea"] + t["review"]) + safety + booked_lt
        raw = max(0, int(np.floor(reorder + t["cycle"] * day_mean - pos))) if pos <= reorder else 0

        results.append({
            "sku": sku, "air": air, "seaDay": sea_day,
            "p20": p20, "mean": mean, "p95": p95,
            "cap": cap, "waste": waste, "wasteLots": waste_lots,
            "first": first, "airQty": air_qty, "recommend": min(raw, cap)
        })
    elapsed = time.perf_counter() - t0
    return results, elapsed

results, elapsed_sec = evaluate_all(st.session_state.sku_data)

# ---------------------------------------------------------
# 4. 상단 배너 및 SKU 선택
# ---------------------------------------------------------
st.markdown(f"""
<div class="top-banner">
    <div>
        <div class="brand-title">SELLERNOTE · 지능형 발주 프로그램</div>
        <div style="font-size:0.85rem; color:#CBE0D7; margin-top:2px;">기준일 {BASE_DATE.strftime('%Y-%m-%d')} · 관리 대상 SKU {len(st.session_state.sku_data)}개</div>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="exec-badge"> {len(results)}개 SKU 계산 완료 · {elapsed_sec:.4f}초 ({elapsed_sec*1000:.1f}ms)</span>
        <span class="demo-badge">발주 검토 대시보드</span>
    </div>
</div>
""", unsafe_allow_html=True)

sku_options = [s["id"] for s in st.session_state.sku_data]
selected_sku_id = st.selectbox(
    "검토할 품목 (SKU) 선택",
    options=sku_options,
    format_func=lambda x: f"{x} · {next(s['name'] for s in st.session_state.sku_data if s['id'] == x)}"
)
active_res = next(r for r in results if r["sku"]["id"] == selected_sku_id)
active_sku = active_res["sku"]

# ---------------------------------------------------------
# 5. 사이드바: 담당자 4단계 예외 기반 알림 센터
# ---------------------------------------------------------
with st.sidebar:
    st.header("담당자 알림 시스템")
    st.caption("긴급(빨강)·주의(주황)·검토(노랑)·변동(파랑) 발생 시 자동 감지합니다.")

    alerts = []
    for r in results:
        sid, sname = r["sku"]["id"], r["sku"]["name"]
        if r["airQty"] > 0:
            alerts.append((0, "긴급", sid, sname, "긴급 항공 투입 검토", f"항공 추가 {r['airQty']:,}개 · 최초 부족 {fmt_md(r['first'])}"))
        if r["waste"] > 0:
            alerts.append((1, "주의", sid, sname, "판매 마감 시 잔량 예상", f"현재 로트 P20 기준 {r['waste']:,}개 만료 예상"))
        if r["first"] is not None:
            alerts.append((1, "주의", sid, sname, "해상 입고 전 품절 예상", f"{fmt_md(r['first'])} ({r['first']//7 + 1}주차) 품절 예상"))
        if r["sku"]["planned"] > r["cap"]:
            alerts.append((2, "검토", sid, sname, "입력 발주량 상한 초과", f"{r['sku']['planned']:,}개 입력 / {r['cap']:,}개 상한"))

    for ev in st.session_state.events:
        alerts.append((3, "변동", ev["sku"], ev["name"], ev["title"], ev["detail"]))

    alerts.sort(key=lambda x: x[0])

    sc1, sc2 = st.columns(2)
    if sc1.button("일괄 모의 전송", use_container_width=True):
        for idx, _ in enumerate(alerts):
            st.session_state.sent_alerts.add(idx)
        st.success(f"{len(alerts)}건 전송 완료")
    if sc2.button("미확인 재알림", use_container_width=True):
        unread = [i for i in range(len(alerts)) if i in st.session_state.sent_alerts and i not in st.session_state.read_alerts]
        st.info(f"미확인 {len(unread)}건 재알림 발송")

    st.divider()
    for idx, (lvl, sev, sid, sname, title, detail) in enumerate(alerts):
        cls_map = {0: "alert-red", 1: "alert-orange", 2: "alert-yellow", 3: "alert-blue"}
        icon_map = {0: "🔴", 1: "🟠", 2: "🟡", 3: "🔵"}
        status_txt = "확인완료" if idx in st.session_state.read_alerts else ("발송됨" if idx in st.session_state.sent_alerts else "대기")
        st.markdown(f"""
        <div class="alert-card {cls_map[lvl]}">
            <strong>{icon_map[lvl]} [{sev}] {title}</strong> · <span style="font-size:0.8rem;">({status_txt})</span><br>
            <span style="font-weight:700;">{sid} ({sname})</span><br>
            {detail}
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. 메인 탭 구성
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "종합 대시보드",
    "소비기한",
    "운송 수단",
    "SKU별 발주 상태"
])

# =========================================================
# [탭 1] 종합 대시보드
# =========================================================
with tab1:
    st.subheader("금주 발주 및 물류 핵심 지표 (KPI)")

    urgent_air_cnt = sum(1 for r in results if r["airQty"] > 0)
    expiry_risk_cnt = sum(1 for r in results if r["waste"] > 0)
    total_sku_cnt = len(results)
    normal_cnt = sum(1 for r in results if r["first"] is None and r["waste"] == 0 and r["sku"]["planned"] <= r["cap"])

    sales_prev = sum(s["ship"][0] for s in st.session_state.sku_data)
    sales_curr = sum(s["ship"][1] for s in st.session_state.sku_data)
    sales_pct = ((sales_curr - sales_prev) / sales_prev * 100) if sales_prev else 0.0

    air_prev = sum(s["costs"]["air"][0] for s in st.session_state.sku_data)
    air_curr = sum(s["costs"]["air"][1] for s in st.session_state.sku_data)
    sea_prev = sum(s["costs"]["sea"][0] for s in st.session_state.sku_data)
    sea_curr = sum(s["costs"]["sea"][1] for s in st.session_state.sku_data)
    cost_prev = air_prev + sea_prev
    cost_curr = air_curr + sea_curr
    cost_pct = ((cost_curr - cost_prev) / cost_prev * 100) if cost_prev else 0.0

    # 첫째 줄: 1, 2, 3번째 박스 (3번째 박스를 '전체 관리 SKU 수'로 변경)
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    row1_c1.metric("① 긴급 항공 검토 필요", f"{urgent_air_cnt} SKU", delta="해상 입고 전 품절 방어 필요", delta_color="inverse" if urgent_air_cnt > 0 else "off")
    row1_c2.metric("② 소비기한 임박·폐기 위험", f"{expiry_risk_cnt} SKU", delta="보수적 판매(P20) 시 잔량 발생", delta_color="inverse" if expiry_risk_cnt > 0 else "off")
    row1_c3.metric("③ 전체 관리 SKU 수", f"{total_sku_cnt} SKU", delta=f"위험 경보 없는 정상 품목 {normal_cnt}개", delta_color="off")

    # 둘째 줄: 4, 5번째 박스
    row2_c1, row2_c2 = st.columns(2)
    row2_c1.metric("④ 금주 운송수단별 운송비", f"{cost_curr:,}원", delta=f"해상 {sea_curr:,}원 · 항공 {air_curr:,}원", delta_color="off")
    row2_c2.metric("⑤ 판매수량 및 운송비 주간 증감률", f"판매량 {sales_pct:+.1f}%", delta=f"금주 출고 {sales_curr:,}개 · 운송비 {cost_pct:+.1f}%", delta_color="off")

    st.divider()

    # 직관적인 발주 조건 및 변동 시뮬레이션 입력창
    col_in_head, col_reset = st.columns([4, 1])
    with col_in_head:
        st.subheader(f"발주 조건 및 변동 시뮬레이션 입력 — [{active_sku['id']} · {active_sku['name']}]")
        st.caption("기준일(2026.11.16)로부터 며칠 뒤인지(D+일)를 입력하면 실제 달력 날짜가 옆에 자동으로 표시됩니다.")
    with col_reset:
        if st.button("초기 예시값 복원", use_container_width=True):
            st.session_state.sku_data = get_initial_data()
            st.session_state.events = []
            st.session_state.sent_alerts = set()
            st.session_state.read_alerts = set()
            st.rerun()

    with st.form("intuitive_order_form"):
        st.markdown('<div class="step-header">1단계 · 현재 보유 재고(로트) 및 예정 입고 현황 수정</div>', unsafe_allow_html=True)

        lot_inputs = []
        for idx, lot in enumerate(active_sku["lots"]):
            lc1, lc2, lc3, lc4 = st.columns([1.2, 1.2, 1.3, 1.3])
            lc1.markdown(f"**현재 재고 · {lot['id']}**<br><span style='font-size:0.8rem; color:#096351;'>창고 보유중</span>", unsafe_allow_html=True)
            l_qty = lc2.number_input(f"{lot['id']} 가용 수량 (개)", min_value=0, max_value=1000000, value=int(lot["qty"]), key=f"lqty_{active_sku['id']}_{idx}")
            l_exp = lc3.number_input(f"{lot['id']} 소비기한 만료 (D+일)", min_value=0, max_value=730, value=int(lot.get("expiry", lot["deadline"])), key=f"lexp_{active_sku['id']}_{idx}")
            lc3.markdown(f'<span class="date-preview">만료일: {fmt_md(l_exp)}</span>', unsafe_allow_html=True)
            l_end = lc4.number_input(f"{lot['id']} 실제 판매 마감 (D+일)", min_value=0, max_value=730, value=int(lot["deadline"]), key=f"lend_{active_sku['id']}_{idx}")
            lc4.markdown(f'<span class="date-preview">마감일: {fmt_md(l_end)}</span>', unsafe_allow_html=True)
            lot_inputs.append((idx, l_qty, l_exp, l_end))

        inb_inputs = []
        for idx, inb in enumerate(active_sku["inbound"]):
            ic1, ic2, ic3, ic4 = st.columns([1.2, 1.2, 1.3, 1.3])
            ic1.markdown(f"**예정 입고 {idx+1} ({inb['mode']})**<br><span style='font-size:0.8rem; color:#506762;'>기존 예정: {fmt_md(inb['day'])}</span>", unsafe_allow_html=True)
            i_qty = ic2.number_input(f"입고 {idx+1} 수량 (개)", min_value=0, max_value=1000000, value=int(inb["qty"]), key=f"iqty_{active_sku['id']}_{idx}")
            i_day = ic3.number_input(f"입고 {idx+1} 도착 예정 (D+일)", min_value=0, max_value=730, value=int(inb["day"]), key=f"iday_{active_sku['id']}_{idx}")
            ic3.markdown(f'<span class="date-preview">도착일: {fmt_md(i_day)}</span>', unsafe_allow_html=True)
            i_end = ic4.number_input(f"입고 {idx+1} 판매 마감 (D+일)", min_value=0, max_value=1095, value=int(inb["deadline"]), key=f"iend_{active_sku['id']}_{idx}")
            ic4.markdown(f'<span class="date-preview">마감일: {fmt_md(i_end)}</span>', unsafe_allow_html=True)
            inb_inputs.append((idx, i_qty, i_day, i_end))

        b2b_str = ", ".join([f"{fmt_md(o['day'])} ({o['qty']:,}개)" for o in active_sku["b2b"]]) or "없음"
        st.info(f"현재 등록된 확정 B2B 주문: **{b2b_str}**")

        st.markdown('<div class="step-header">2단계 · 금주 신규 발주 희망량 및 돌발 변수(확정 B2B · 입고 지연) 입력</div>', unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        in_planned = s1.number_input("금주 신규 발주 희망 수량 (개)", min_value=0, max_value=1000000, value=int(active_sku["planned"]), help="문제 2의 최대 발주 상한 초과 여부를 자동 검증합니다.")
        in_b2b_qty = s2.number_input("추가 확정 B2B 주문량 (개)", min_value=0, max_value=1000000, value=0, help="기존 주간 예측에 포함되지 않은 신규 확정 대량 주문만 입력하세요.")
        in_b2b_day = s3.number_input("확정 B2B 출고 예정일 (D+일)", min_value=0, max_value=365, value=4)
        s3.markdown(f'<span class="date-preview">출고일: {fmt_md(in_b2b_day)}</span>', unsafe_allow_html=True)
        in_delay = s4.number_input("가장 빠른 예정 입고 지연 (+일)", min_value=0, max_value=365, value=0, help="선적·통관 지연 시 가장 빠른 예정 입고일이 뒤로 밀립니다.")

        submitted = st.form_submit_button("입력값 반영 및 발주 권고 재계산", use_container_width=True, type="primary")
        if submitted:
            active_sku["planned"] = int(in_planned)
            for idx, l_qty, l_exp, l_end in lot_inputs:
                active_sku["lots"][idx]["qty"] = int(l_qty)
                active_sku["lots"][idx]["expiry"] = int(l_exp)
                active_sku["lots"][idx]["deadline"] = int(l_end)

            for idx, i_qty, i_day, i_end in inb_inputs:
                old_day = active_sku["inbound"][idx]["day"]
                active_sku["inbound"][idx]["qty"] = int(i_qty)
                active_sku["inbound"][idx]["day"] = int(i_day)
                active_sku["inbound"][idx]["deadline"] = int(i_end)
                if i_day > old_day:
                    st.session_state.events.append({
                        "sku": active_sku["id"], "name": active_sku["name"],
                        "title": f"{active_sku['inbound'][idx]['mode']} ETA 지연",
                        "detail": f"{fmt_md(old_day)} → {fmt_md(i_day)} ({i_day - old_day}일 지연)"
                    })

            if in_delay > 0 and active_sku["inbound"]:
                earliest = min(active_sku["inbound"], key=lambda x: x["day"])
                old_d = earliest["day"]
                earliest["day"] += int(in_delay)
                st.session_state.events.append({
                    "sku": active_sku["id"], "name": active_sku["name"],
                    "title": f"{earliest['mode']} 입항 지연 반영",
                    "detail": f"{fmt_md(old_d)} → {fmt_md(earliest['day'])} (+{in_delay}일 지연)"
                })

            if in_b2b_qty > 0:
                active_sku["b2b"].append({"day": int(in_b2b_day), "qty": int(in_b2b_qty)})
                st.session_state.events.append({
                    "sku": active_sku["id"], "name": active_sku["name"],
                    "title": "확정 B2B 대량 주문 등록",
                    "detail": f"{fmt_md(in_b2b_day)} 출고 · {int(in_b2b_qty):,}개 추가"
                })

            st.rerun()

    st.divider()

    # SKU별 발주 권고 결과표
    st.subheader("SKU별 발주 권고 결과표 (긴급 순위순)")
    def get_rank(x):
        if x["airQty"] > 0:
            return 0
        if x["waste"] > 0 or x["first"] is not None:
            return 1
        if x["sku"]["planned"] > x["cap"]:
            return 2
        return 3

    rank_labels = {0: "🔴 긴급", 1: "🟠 주의", 2: "🟡 검토", 3: "🟢 정상"}
    sorted_res = sorted(results, key=get_rank)

    table_rows = []
    for r in sorted_res:
        rk = get_rank(r)
        table_rows.append({
            "긴급 순위": rank_labels[rk],
            "SKU ID": r["sku"]["id"],
            "품목명": r["sku"]["name"],
            "권고 발주량": f"{r['recommend']:,}개",
            "만료 예상 폐기량": f"{r['waste']:,}개",
            "신규 발주 상한": f"{r['cap']:,}개",
            "최초 품절 예상": "품절 없음" if r["first"] is None else f"{r['first']//7 + 1}주차 ({fmt_md(r['first'])})",
            "항공 긴급 투입량": f"{r['airQty']:,}개"
        })

    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

# =========================================================
# [탭 2] 소비기한 (문제 2) — 상·하한 음영 밴드 + 주차별 직관 차트
# =========================================================
with tab2:
    st.subheader(f"로트별 소비기한(FEFO) 소진 및 신규 발주 상한 — [{active_sku['id']} {active_sku['name']}]")
    t = active_sku["terms"]

    e1, e2, e3 = st.columns(3)
    e1.metric("현재 로트 예상 폐기 잔량 (P20)", f"{active_res['waste']:,}개", delta="판매 둔화 시 만료 예상", delta_color="inverse" if active_res["waste"] > 0 else "off")
    e2.metric("신규 해상 발주 최대 상한 (P95)", f"{active_res['cap']:,}개", delta=f"신규 입고 {fmt_md(t['sea'])} ~ 마감 {fmt_md(t['sea']+t['window'])}", delta_color="off")
    e3.metric("담당자 희망 발주량 검증", f"{active_sku['planned']:,}개", delta="상한 초과! 조정 필요" if active_sku["planned"] > active_res["cap"] else "상한 이내 정상", delta_color="inverse" if active_sku["planned"] > active_res["cap"] else "normal")

    lot_df = pd.DataFrame([
        {
            "로트 ID": l["id"],
            "가용 재고": f"{int(l['qty']):,}개",
            "P20 소진 기간": "미소진" if l["first"] is None else f"{fmt_md(l['first'])} ~ {fmt_md(l['last'])}",
            "판매 마감일": fmt_md(l["deadline"]),
            "판매 마감 시 만료 잔량": f"{int(np.ceil(l['lost'] - 1e-7)):,}개"
        }
        for l in active_res["wasteLots"]
    ])
    st.dataframe(lot_df, use_container_width=True, hide_index=True)

    # 실제 날짜 객체(datetime) 사용으로 연도 변경 시 선 꺾임 현상 완전 해결
    end_d = max(7, t["sea"] + t["window"])
    step = 7  # 주 단위(1주 후, 2주 후...)로 깔끔하게 표시
    sample_days = list(range(0, end_d + 1, step))
    if sample_days[-1] != end_d:
        sample_days.append(end_d)

    dates_x = [BASE_DATE + datetime.timedelta(days=d) for d in sample_days]
    tick_labels = [f"{d//7}주 후<br>({fmt_md(d)})" if d > 0 else f"기준일<br>({fmt_md(0)})" for d in sample_days]

    p20_y = [round(active_res["p20"]["lines"][d][0], 1) for d in sample_days]
    mean_y = [round(active_res["mean"]["lines"][d][0], 1) for d in sample_days]
    p95_y = [round(active_res["p95"]["lines"][d][0], 1) for d in sample_days]

    fig_exp = go.Figure()
    # 상한선(P95) 투명 경계
    fig_exp.add_trace(go.Scatter(
        x=dates_x, y=p95_y, mode="lines", line=dict(width=0),
        showlegend=False, hoverinfo="skip"
    ))
    # 하한선(P20) ~ 상한선(P95) 사이 반투명 민트 음영 밴드
    fig_exp.add_trace(go.Scatter(
        x=dates_x, y=p20_y, mode="lines",
        line=dict(color="rgba(9, 99, 81, 0.35)", width=1.5, dash="dot"),
        fill="tonexty", fillcolor="rgba(9, 99, 81, 0.14)",
        name="수요 예측 상·하한 범위 (P20 ~ P95)"
    ))
    # 중심 평균선
    fig_exp.add_trace(go.Scatter(
        x=dates_x, y=mean_y, mode="lines+markers",
        line=dict(color="#096351", width=3.5),
        marker=dict(size=7, color="#096351"),
        name="주간 누적 예측 평균값"
    ))

    # 주요 일정 수직선 (datetime 좌표 사용)
    sea_dt = BASE_DATE + datetime.timedelta(days=t["sea"])
    end_dt = BASE_DATE + datetime.timedelta(days=t["sea"] + t["window"])
    fig_exp.add_vline(x=sea_dt, line_dash="dot", line_color="#2563EB", line_width=2)
    fig_exp.add_annotation(x=sea_dt, y=1.06, yref="paper", text=f"신규 해상 입고 ({fmt_md(t['sea'])})", showarrow=False, font=dict(color="#2563EB", size=12))

    fig_exp.add_vline(x=end_dt, line_dash="dash", line_color="#D93025", line_width=2)
    fig_exp.add_annotation(x=end_dt, y=1.06, yref="paper", text=f"판매 마감일 ({fmt_md(t['sea']+t['window'])})", showarrow=False, font=dict(color="#D93025", size=12))

    fig_exp.update_layout(
        title="주차별 누적 수요 예측(평균 및 상·하한 밴드)과 판매 마감 시점",
        xaxis=dict(tickmode="array", tickvals=dates_x[::2], ticktext=tick_labels[::2], showgrid=False),
        yaxis=dict(title="누적 수량 (개)", gridcolor="#E6ECE9", zeroline=True, zerolinecolor="#D9E5DF"),
        plot_bgcolor="white",
        height=420,
        margin=dict(t=65, b=40, l=50, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.12, xanchor="left", x=0)
    )
    st.plotly_chart(fig_exp, use_container_width=True)
    st.caption("연한 초록색 음영은 보수적 하한(P20)부터 상한(P95)까지의 누적 수요 예측 구간입니다. 하한선(점선)이 기존 로트 재고량보다 낮으면 판매 마감일까지 미소진 폐기 물량이 발생합니다.")

# =========================================================
# [탭 3] 운송 수단 (문제 3) — 상·하한 음영 밴드 + 가용 공급 계단선 비교
# =========================================================
with tab3:
    st.subheader(f"항공 및 해상 입고 전 품절 위험 분석 — [{active_sku['id']} {active_sku['name']}]")

    tr1, tr2, tr3 = st.columns(3)
    tr1.metric("항공 검토 입고일 / 해상 입고일", f"{fmt_md(active_res['air'])} / {fmt_md(active_res['seaDay'])}", delta="리드타임 비교 기준", delta_color="off")
    tr2.metric("최초 품절 예상 시점 (P95)", "해상 입고 전 없음" if active_res["first"] is None else f"{fmt_md(active_res['first'])} ({active_res['first']//7 + 1}주차)", delta="안전 상한 돌파 시점", delta_color="inverse" if active_res["first"] is not None else "normal")
    tr3.metric("긴급 항공 추가 투입 권고량", f"{active_res['airQty']:,}개", delta="해상 도착 전 품절 방어분", delta_color="inverse" if active_res["airQty"] > 0 else "off")

    end_tr = max(7, active_res["air"], active_res["seaDay"])
    tr_days = list(range(0, end_tr + 1))
    tr_dates = [BASE_DATE + datetime.timedelta(days=d) for d in tr_days]

    # x축 눈금은 1주(7일) 간격으로 깔끔하게 표시
    tick_days_tr = list(range(0, end_tr + 1, 7))
    if tick_days_tr[-1] != end_tr:
        tick_days_tr.append(end_tr)
    tick_dates_tr = [BASE_DATE + datetime.timedelta(days=d) for d in tick_days_tr]
    tick_labels_tr = [f"{d//7}주 후<br>({fmt_md(d)})" if d > 0 else f"기준일<br>({fmt_md(0)})" for d in tick_days_tr]

    p20_tr = [round(active_res["p20"]["lines"][d][0], 1) for d in tr_days]
    mean_tr = [round(active_res["mean"]["lines"][d][0], 1) for d in tr_days]
    p95_dem = [round(active_res["p95"]["lines"][d][0], 1) for d in tr_days]
    p95_sup = [round(active_res["p95"]["lines"][d][1], 1) for d in tr_days]

    fig_tr = go.Figure()
    # 상한(P95) 경계선
    fig_tr.add_trace(go.Scatter(
        x=tr_dates, y=p95_dem, mode="lines",
        line=dict(color="rgba(9, 99, 81, 0.45)", width=1.5, dash="dot"),
        name="수요 상한 (P95 · 스파이크 기준)"
    ))
    # 하한(P20) ~ 상한(P95) 음영 밴드
    fig_tr.add_trace(go.Scatter(
        x=tr_dates, y=p20_tr, mode="lines", line=dict(width=0),
        fill="tonexty", fillcolor="rgba(9, 99, 81, 0.14)",
        name="수요 예측 상·하한 구간"
    ))
    # 평균 누적 수요
    fig_tr.add_trace(go.Scatter(
        x=tr_dates, y=mean_tr, mode="lines",
        line=dict(color="#096351", width=3.5),
        name="평균 누적 수요"
    ))
    # 누적 가용 공급 (계단형)
    fig_tr.add_trace(go.Scatter(
        x=tr_dates, y=p95_sup, mode="lines",
        line=dict(color="#2563EB", width=3, shape="hv"),
        name="누적 가용 공급 (현재재고 + 예정입고)"
    ))

    air_dt = BASE_DATE + datetime.timedelta(days=active_res["air"])
    sea_tr_dt = BASE_DATE + datetime.timedelta(days=active_res["seaDay"])

    fig_tr.add_vline(x=air_dt, line_dash="dot", line_color="#0284C7", line_width=2)
    fig_tr.add_annotation(x=air_dt, y=1.06, yref="paper", text=f"항공 입고 가능일 ({fmt_md(active_res['air'])})", showarrow=False, font=dict(color="#0284C7", size=12))

    fig_tr.add_vline(x=sea_tr_dt, line_dash="dash", line_color="#7C3AED", line_width=2)
    fig_tr.add_annotation(x=sea_tr_dt, y=1.06, yref="paper", text=f"해상 입고일 ({fmt_md(active_res['seaDay'])})", showarrow=False, font=dict(color="#7C3AED", size=12))

    if active_res["first"] is not None:
        first_dt = BASE_DATE + datetime.timedelta(days=active_res["first"])
        fig_tr.add_vline(x=first_dt, line_dash="solid", line_color="#D93025", line_width=2)
        fig_tr.add_annotation(x=first_dt, y=0.92, yref="paper", text=f"최초 품절 ({fmt_md(active_res['first'])})", showarrow=False, bgcolor="#FCE5E4", font=dict(color="#D93025", size=12))

    fig_tr.update_layout(
        title="리드타임 구간 내 수요 예측(평균 및 상·하한) vs 누적 가용 공급 비교",
        xaxis=dict(tickmode="array", tickvals=tick_dates_tr, ticktext=tick_labels_tr, showgrid=False),
        yaxis=dict(title="누적 수량 (개)", gridcolor="#E6ECE9", zeroline=True, zerolinecolor="#D9E5DF"),
        plot_bgcolor="white",
        height=430,
        margin=dict(t=65, b=40, l=50, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.12, xanchor="left", x=0)
    )
    st.plotly_chart(fig_tr, use_container_width=True)
    st.caption("파란색 계단선(누적 가용 공급)이 초록색 점선(수요 상한 P95) 아래로 내려가는 지점이 최초 품절 예상 시점이며, 항공 입고일부터 해상 입고 전날까지의 부족분이 항공 긴급 투입 권고량입니다.")
# =========================================================
# [탭 4] SKU 발주 상태
# =========================================================
with tab4:
    st.subheader(f"세부 SKU별 발주·국제 물류 상태 — [{active_sku['id']} {active_sku['name']}]")
    rec_rows = []
    for o in active_sku["records"]:
        rec_rows.append({
            "의뢰일": fmt_md(o["request"]),
            "수락일": fmt_md(o["accepted"]),
            "운송 시작": fmt_md(o["depart"]),
            "도착 예정": fmt_md(o["eta"]),
            "상태 / 방식": f"{o['status']} / {o['mode']}",
            "출발지 → 도착지": o["route"],
            "컨테이너 / 적재량": f"{o['container']} / {o['load']}",
            "운송비": f"{o['cost']:,}원",
            "VAT": f"{o['vat']:,}원",
            "의뢰→도착 리드타임": f"{o['eta'] - o['request']}일"
        })
    st.dataframe(pd.DataFrame(rec_rows), use_container_width=True, hide_index=True)
