import html
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from options_strategy_assistant.catalog import compare_table, filter_catalog, load_catalog, summary_metrics

st.set_page_config(page_title="期权策略助手", layout="wide", initial_sidebar_state="collapsed")

RISK_COLORS = {
    "低风险": "#6f9b6d",
    "中风险": "#d89a3d",
    "高风险": "#cf6a4c",
}

FILTER_OPTIONS = {
    "direction": ["全部", "看涨", "看跌", "震荡", "双向波动", "对冲", "套利"],
    "volatility": ["全部", "波动率上行", "波动率下行", "波动率中性", "高波动", "定价偏差"],
    "time_value": ["全部", "买时间", "卖时间", "时间中性"],
    "risk_bucket": ["全部", "低风险", "中风险", "高风险"],
    "holding_requirement": ["全部", "无持仓要求", "需持有现货", "需卖空现货", "机构/套利账户"],
    "objective": ["全部", "方向表达", "收益增强", "风险对冲", "波动率交易", "套利", "仓位替代", "结构表达"],
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --bg: #f5ede2;
          --bg-soft: #fbf5ed;
          --panel: rgba(255, 249, 240, 0.88);
          --panel-strong: rgba(255, 251, 246, 0.96);
          --panel-muted: rgba(247, 238, 226, 0.9);
          --border: rgba(131, 99, 67, 0.16);
          --border-strong: rgba(184, 115, 51, 0.24);
          --text: #2d231d;
          --muted: #7b6858;
          --accent: #b87333;
          --accent-blue: #6b8c8e;
          --accent-amber: #c98b35;
          --accent-red: #c86b53;
          --mono: "JetBrains Mono", "SFMono-Regular", "Menlo", monospace;
          --sans: "IBM Plex Sans", "SF Pro Display", "Avenir Next", "Helvetica Neue", sans-serif;
        }

        html, body, [class*="css"] {
          font-family: var(--sans);
        }

        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(circle at top left, rgba(201, 139, 53, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(107, 140, 142, 0.12), transparent 26%),
            linear-gradient(180deg, #f6eee4 0%, #f3eadf 36%, #efe3d6 100%);
          color: var(--text);
        }

        [data-testid="stHeader"] {
          background: rgba(245, 237, 226, 0.76);
          border-bottom: 1px solid rgba(131, 99, 67, 0.08);
          backdrop-filter: blur(10px);
        }

        section.main > div {
          max-width: 1460px;
          padding-top: 2.25rem;
          padding-bottom: 4rem;
        }

        .block-container {
          padding-top: 0;
        }

        h1, h2, h3, h4 {
          color: var(--text);
          letter-spacing: -0.03em;
        }

        p, li, label, .stMarkdown, .stCaption {
          color: var(--muted);
        }

        [data-testid="stMetric"] {
          background: linear-gradient(180deg, rgba(255, 251, 246, 0.98), rgba(250, 244, 236, 0.96));
          border: 1px solid var(--border);
          border-radius: 24px;
          padding: 1rem 1.2rem;
          box-shadow: 0 18px 40px rgba(92, 67, 44, 0.08);
        }

        [data-testid="stMetricLabel"] {
          color: var(--muted);
          font-family: var(--mono);
          font-size: 0.76rem;
          letter-spacing: 0.14em;
          text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
          color: var(--text);
          letter-spacing: -0.04em;
        }

        div[data-baseweb="select"] > div,
        .stTextInput input {
          background: rgba(255, 250, 244, 0.96) !important;
          color: var(--text) !important;
          border: 1px solid var(--border) !important;
          border-radius: 18px !important;
          min-height: 54px;
          box-shadow: inset 0 0 0 1px rgba(184, 115, 51, 0.04);
        }

        div[data-baseweb="select"] svg,
        .stTextInput input::placeholder {
          color: var(--muted) !important;
        }

        label[data-testid="stWidgetLabel"] p {
          color: var(--muted);
          font-family: var(--mono);
          font-size: 0.75rem;
          letter-spacing: 0.12em;
          text-transform: uppercase;
        }

        div[data-testid="stExpander"] {
          background: linear-gradient(180deg, rgba(255, 250, 244, 0.98), rgba(249, 241, 231, 0.96));
          border: 1px solid var(--border);
          border-radius: 22px;
          overflow: hidden;
        }

        div[data-testid="stExpander"] details summary p {
          color: var(--text);
          font-weight: 600;
        }

        div[data-testid="stAlertContainer"] > div {
          border-radius: 20px;
          border: 1px solid rgba(201, 139, 53, 0.22);
          background: linear-gradient(90deg, rgba(250, 236, 210, 0.95), rgba(247, 229, 202, 0.9));
          color: #7a5426;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
          background: transparent;
        }

        .hero-shell,
        .desk-shell,
        .guide-shell,
        .section-shell,
        .table-shell {
          background: linear-gradient(180deg, rgba(255, 251, 246, 0.94), rgba(249, 241, 231, 0.9));
          border: 1px solid var(--border);
          border-radius: 28px;
          box-shadow: 0 24px 60px rgba(92, 67, 44, 0.1);
        }

        .hero-shell {
          padding: 1.8rem 2rem 2rem 2rem;
          min-height: 280px;
          position: relative;
          overflow: hidden;
        }

        .hero-shell:before {
          content: "";
          position: absolute;
          inset: 0;
          background:
            linear-gradient(115deg, rgba(184, 115, 51, 0.09), transparent 35%),
            radial-gradient(circle at right top, rgba(201, 139, 53, 0.14), transparent 24%);
          pointer-events: none;
        }

        .desk-shell {
          padding: 1.4rem 1.5rem;
          min-height: 280px;
        }

        .hero-kicker,
        .section-kicker,
        .guide-kicker,
        .desk-kicker {
          font-family: var(--mono);
          color: var(--accent);
          font-size: 0.76rem;
          letter-spacing: 0.16em;
          text-transform: uppercase;
          margin-bottom: 0.85rem;
        }

        .hero-title {
          font-size: clamp(3.2rem, 6vw, 5.8rem);
          line-height: 0.96;
          margin: 0;
          color: var(--text);
          position: relative;
        }

        .hero-subtitle {
          margin-top: 1rem;
          max-width: 780px;
          font-size: 1.08rem;
          line-height: 1.7;
          color: var(--muted);
          position: relative;
        }

        .chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.55rem;
          margin-top: 1.1rem;
          position: relative;
        }

        .hero-chip,
        .strategy-chip {
          display: inline-flex;
          align-items: center;
          gap: 0.35rem;
          padding: 0.4rem 0.72rem;
          border-radius: 999px;
          border: 1px solid rgba(184, 115, 51, 0.16);
          background: rgba(255, 246, 235, 0.88);
          color: var(--text);
          font-size: 0.84rem;
        }

        .hero-chip strong,
        .strategy-chip strong {
          color: var(--accent);
          font-weight: 600;
        }

        .desk-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 0.85rem;
          margin-top: 1.15rem;
        }

        .desk-stat {
          padding: 0.95rem 1rem;
          border-radius: 18px;
          background: rgba(255, 246, 235, 0.92);
          border: 1px solid rgba(131, 99, 67, 0.12);
        }

        .desk-stat-label {
          font-family: var(--mono);
          color: var(--muted);
          text-transform: uppercase;
          letter-spacing: 0.14em;
          font-size: 0.72rem;
        }

        .desk-stat-value {
          color: var(--text);
          font-size: 1.5rem;
          letter-spacing: -0.04em;
          font-weight: 600;
          margin-top: 0.3rem;
        }

        .desk-note {
          margin-top: 1.1rem;
          color: var(--muted);
          line-height: 1.7;
        }

        .guide-shell,
        .section-shell,
        .table-shell {
          padding: 1.3rem 1.4rem 1.4rem 1.4rem;
        }

        .guide-grid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.95rem;
          margin-top: 0.8rem;
        }

        .guide-card {
          padding: 1.1rem 1.05rem;
          border-radius: 18px;
          border: 1px solid rgba(131, 99, 67, 0.1);
          background: rgba(255, 247, 237, 0.92);
          min-height: 160px;
        }

        .guide-card-title {
          color: var(--text);
          font-size: 1.02rem;
          font-weight: 600;
          margin-bottom: 0.55rem;
        }

        .guide-card p {
          margin: 0;
          line-height: 1.72;
          color: var(--muted);
        }

        .section-title {
          color: var(--text);
          font-size: 1.28rem;
          font-weight: 600;
          margin-bottom: 0.3rem;
        }

        .section-copy {
          color: var(--muted);
          line-height: 1.65;
        }

        .strategy-card {
          padding: 1.2rem 1.2rem 1.05rem 1.2rem;
          border-radius: 24px;
          border: 1px solid var(--border);
          background: linear-gradient(180deg, rgba(255, 251, 246, 0.98), rgba(251, 244, 235, 0.96));
          box-shadow: 0 18px 42px rgba(92, 67, 44, 0.08);
          margin-bottom: 1rem;
        }

        .strategy-card-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
        }

        .strategy-family {
          font-family: var(--mono);
          font-size: 0.72rem;
          letter-spacing: 0.14em;
          text-transform: uppercase;
          color: var(--accent);
          margin-bottom: 0.45rem;
        }

        .strategy-name {
          color: var(--text);
          font-size: 1.34rem;
          font-weight: 650;
          line-height: 1.18;
        }

        .strategy-name-en {
          color: var(--muted);
          font-family: var(--mono);
          font-size: 0.82rem;
          margin-top: 0.3rem;
        }

        .risk-pill {
          display: inline-flex;
          align-items: center;
          padding: 0.38rem 0.68rem;
          border-radius: 999px;
          font-family: var(--mono);
          font-size: 0.78rem;
          font-weight: 600;
          color: #041019;
        }

        .strategy-summary {
          margin-top: 0.85rem;
          color: var(--text);
          line-height: 1.72;
          font-size: 0.98rem;
        }

        .strategy-chip-row {
          display: flex;
          flex-wrap: wrap;
          gap: 0.48rem;
          margin-top: 0.9rem;
          margin-bottom: 0.95rem;
        }

        .strategy-chip {
          font-size: 0.78rem;
          color: var(--muted);
          border-color: rgba(131, 99, 67, 0.12);
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 0.72rem;
          margin-top: 0.35rem;
        }

        .info-tile {
          padding: 0.88rem 0.95rem;
          border-radius: 16px;
          background: rgba(255, 247, 237, 0.94);
          border: 1px solid rgba(131, 99, 67, 0.1);
        }

        .info-label {
          font-family: var(--mono);
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: var(--muted);
          font-size: 0.68rem;
          margin-bottom: 0.45rem;
        }

        .info-value {
          color: var(--text);
          line-height: 1.62;
          font-size: 0.94rem;
        }

        .risk-note {
          margin-top: 0.9rem;
          padding-top: 0.9rem;
          border-top: 1px solid rgba(131, 99, 67, 0.1);
          color: #99611f;
          line-height: 1.7;
        }

        .table-shell .stDataFrame {
          border-radius: 18px;
          overflow: hidden;
          border: 1px solid rgba(131, 99, 67, 0.1);
        }

        @media (max-width: 1100px) {
          .guide-grid,
          .desk-grid,
          .info-grid {
            grid-template-columns: 1fr;
          }

          .hero-title {
            font-size: 3rem;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def risk_pill(label: str) -> str:
    color = RISK_COLORS.get(label, "#7b8ba0")
    return f"<span class='risk-pill' style='background:{color};'>{html.escape(label)}</span>"


def escape(value: object) -> str:
    return html.escape("" if value is None else str(value))


def accent_label(direction_tags: list[str], objective_tags: list[str]) -> str:
    if "套利" in objective_tags or "套利" in direction_tags:
        return "Pricing Edge"
    if "风险对冲" in objective_tags or "对冲" in direction_tags:
        return "Risk Overlay"
    if "双向波动" in direction_tags:
        return "Volatility Breakout"
    if "看涨" in direction_tags and "看跌" not in direction_tags:
        return "Bullish Structure"
    if "看跌" in direction_tags and "看涨" not in direction_tags:
        return "Bearish Structure"
    if "震荡" in direction_tags:
        return "Range Income"
    return "Structure View"


def hero_chip(label: str, value: str) -> str:
    return f"<span class='hero-chip'>{escape(label)} <strong>{escape(value)}</strong></span>"


def render_hero(catalog_count: int, filters: dict[str, str]) -> None:
    active_filters = [value for value in filters.values() if value and value != "全部"]
    filter_label = " / ".join(active_filters[:4]) if active_filters else "全市场结构视图"
    buy_time = escape(filters["time_value"] if filters["time_value"] != "全部" else "未限制")
    st.markdown(
        f"""
        <div class="hero-shell">
          <div class="hero-kicker">Trader Desk / Options Structure Screener</div>
          <h1 class="hero-title">期权策略助手</h1>
          <div class="hero-subtitle">
            用交易台的视角去筛结构，而不是从一长串策略名里盲找。
            先锁定方向与波动率，再判断你是在买时间、卖时间，还是做风险对冲。
          </div>
          <div class="chip-row">
            {hero_chip("Coverage", f"{catalog_count} 策略")}
            {hero_chip("Desk Lens", filter_label)}
            {hero_chip("Time Value", buy_time)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_desk_panel(metrics: dict[str, int]) -> None:
    st.markdown(
        f"""
        <div class="desk-shell">
          <div class="desk-kicker">Desk Snapshot</div>
          <div class="desk-grid">
            <div class="desk-stat">
              <div class="desk-stat-label">Matched Structures</div>
              <div class="desk-stat-value">{metrics['count']}</div>
            </div>
            <div class="desk-stat">
              <div class="desk-stat-label">Starter Friendly</div>
              <div class="desk-stat-value">{metrics['starter_count']}</div>
            </div>
            <div class="desk-stat">
              <div class="desk-stat-label">High Risk</div>
              <div class="desk-stat-value">{metrics['high_risk_count']}</div>
            </div>
            <div class="desk-stat">
              <div class="desk-stat-label">Hedge Overlay</div>
              <div class="desk-stat-value">{metrics['hedge_count']}</div>
            </div>
          </div>
          <div class="desk-note">
            优先筛掉你不愿承担的风险，再比较相邻结构的 Theta、Vega 和保证金占用。
            这比直接在“跨式 / 铁鹰 / 对角价差”之间跳来跳去更像真实交易流程。
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_playbook() -> None:
    st.markdown(
        """
        <div class="guide-shell">
          <div class="guide-kicker">Trade Framework</div>
          <div class="section-title">先选市场判断，再选结构表达</div>
          <div class="guide-grid">
            <div class="guide-card">
              <div class="guide-card-title">方向 Bias</div>
              <p>先确认你是偏看涨、偏看跌，还是认为标的会横盘或放量突破。方向判断会直接缩小候选策略池。</p>
            </div>
            <div class="guide-card">
              <div class="guide-card-title">波动率 Vol</div>
              <p>再判断你是在买波动还是卖波动。很多结构看起来方向相似，但对隐含波动率的敏感度完全不同。</p>
            </div>
            <div class="guide-card">
              <div class="guide-card-title">时间 Theta</div>
              <p>最后看时间价值。买时间通常更怕拖，卖时间通常更怕尾部行情。这一步决定你的持仓节奏和心态压力。</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-shell">
          <div class="section-kicker">{escape(kicker)}</div>
          <div class="section-title">{escape(title)}</div>
          <div class="section-copy">{escape(copy)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_strategy_card(record: dict[str, object]) -> None:
    tags = [
        *[str(tag) for tag in record["direction_tags"]],
        *[str(tag) for tag in record["volatility_tags"]],
        str(record["time_value_profile"]),
        str(record["holding_requirement"]),
    ]
    chips = "".join(f"<span class='strategy-chip'>{escape(tag)}</span>" for tag in tags)
    info_tiles = [
        ("Structure Lens", accent_label(record["direction_tags"], record["objective_tags"])),
        ("Strategy Goal", " / ".join(str(tag) for tag in record["objective_tags"])),
        ("Max Profit", str(record["max_profit"])),
        ("Max Loss", str(record["max_loss"])),
        ("Breakeven", str(record["breakeven"])),
        ("Margin / Capital", str(record["margin_summary"])),
    ]
    tiles_html = "".join(
        f"""
        <div class="info-tile">
          <div class="info-label">{escape(label)}</div>
          <div class="info-value">{escape(value)}</div>
        </div>
        """
        for label, value in info_tiles
    )

    with st.container():
        st.markdown(
            f"""
            <div class="strategy-card">
              <div class="strategy-card-header">
                <div>
                  <div class="strategy-family">{escape(record['strategy_family'])}</div>
                  <div class="strategy-name">{escape(record['name'])}</div>
                  <div class="strategy-name-en">{escape(record['name_en'])}</div>
                </div>
                <div>{risk_pill(str(record['risk_bucket']))}</div>
              </div>
              <div class="strategy-summary">{escape(record['summary'])}</div>
              <div class="strategy-chip-row">{chips}</div>
              <div class="info-grid">{tiles_html}</div>
              <div class="risk-note">Risk note: {escape(record['risk_note'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander("查看 Greeks / 数据来源 / 原始标签"):
            st.markdown(f"**Greek 特征**：{record['greeks']}")
            st.markdown(f"**风险等级**：{record['risk_label']}")
            st.markdown(f"**数据页签**：{' / '.join(record['source_sheets'])}")


def render_card_grid(records: list[dict[str, object]]) -> None:
    columns = st.columns(2)
    for index, record in enumerate(records):
        with columns[index % 2]:
            render_strategy_card(record)


def main() -> None:
    inject_styles()
    catalog = load_catalog()

    current_filters = {
        "direction": st.session_state.get("filter_direction", "全部"),
        "volatility": st.session_state.get("filter_volatility", "全部"),
        "time_value": st.session_state.get("filter_time_value", "全部"),
        "risk_bucket": st.session_state.get("filter_risk_bucket", "全部"),
        "holding_requirement": st.session_state.get("filter_holding_requirement", "全部"),
        "objective": st.session_state.get("filter_objective", "全部"),
        "keyword": st.session_state.get("filter_keyword", ""),
    }
    hero_filtered = filter_catalog(
        catalog,
        direction=current_filters["direction"],
        volatility=current_filters["volatility"],
        time_value=current_filters["time_value"],
        risk_bucket=current_filters["risk_bucket"],
        holding_requirement=current_filters["holding_requirement"],
        objective=current_filters["objective"],
        keyword=current_filters["keyword"],
    )
    hero_metrics = summary_metrics(hero_filtered)

    hero_col, desk_col = st.columns([1.85, 1], gap="large")
    with hero_col:
        render_hero(len(catalog), current_filters)
    with desk_col:
        render_desk_panel(hero_metrics)

    st.warning("教育和研究用途，不构成投资建议。卖方、保证金和杠杆策略在极端行情下可能出现超预期亏损。")

    render_playbook()

    render_section_header(
        "Screener",
        "按交易假设筛结构",
        "方向、波动率、时间价值和持仓基础放在同一层，是为了让筛选更贴近真实下单前的结构比较。",
    )

    filter_row_1 = st.columns(4)
    direction = filter_row_1[0].selectbox("方向", FILTER_OPTIONS["direction"], key="filter_direction")
    volatility = filter_row_1[1].selectbox("波动率判断", FILTER_OPTIONS["volatility"], key="filter_volatility")
    time_value = filter_row_1[2].selectbox("时间价值", FILTER_OPTIONS["time_value"], key="filter_time_value")
    risk_bucket = filter_row_1[3].selectbox("风险等级", FILTER_OPTIONS["risk_bucket"], key="filter_risk_bucket")

    filter_row_2 = st.columns(3)
    holding_requirement = filter_row_2[0].selectbox(
        "持仓基础",
        FILTER_OPTIONS["holding_requirement"],
        key="filter_holding_requirement",
    )
    objective = filter_row_2[1].selectbox("策略目的", FILTER_OPTIONS["objective"], key="filter_objective")
    keyword = filter_row_2[2].text_input("关键词", placeholder="如：备兑、套利、跨式、保护", key="filter_keyword")

    filtered = filter_catalog(
        catalog,
        direction=direction,
        volatility=volatility,
        time_value=time_value,
        risk_bucket=risk_bucket,
        holding_requirement=holding_requirement,
        objective=objective,
        keyword=keyword,
    )
    metrics = summary_metrics(filtered)

    metric_cols = st.columns(4)
    metric_cols[0].metric("当前命中策略", metrics["count"])
    metric_cols[1].metric("适合先看的策略", metrics["starter_count"])
    metric_cols[2].metric("高风险策略", metrics["high_risk_count"])
    metric_cols[3].metric("对冲类策略", metrics["hedge_count"])

    if filtered.empty:
        st.info("当前筛选条件下没有命中策略，可以先放宽方向或风险等级。")
        return

    starter_block = filtered[filtered["starter_friendly"]].head(4)
    if not starter_block.empty:
        render_section_header(
            "Starter Setups",
            "先看这些更容易理解的结构",
            "这里优先展示有限亏损、保证金压力相对清晰、适合作为开源 demo 入口的策略。",
        )
        render_card_grid(starter_block.to_dict("records"))

    remaining = filtered[~filtered["strategy_id"].isin(starter_block["strategy_id"] if not starter_block.empty else [])]
    if not remaining.empty:
        render_section_header(
            "Matched Structures",
            "继续比较全部命中策略",
            "这一层更适合拿来横向比较相邻结构的收益上限、亏损轮廓、保证金和 Greeks 暴露。",
        )
        render_card_grid(remaining.to_dict("records"))

    render_section_header(
        "Comparison Matrix",
        "最后再看矩阵，而不是一开始就看表格",
        "表格适合横向比对，但真实筛选通常应该先从市场观点与风险承受能力出发。",
    )
    with st.expander("打开对比矩阵", expanded=False):
        st.markdown("<div class='table-shell'>", unsafe_allow_html=True)
        st.dataframe(compare_table(filtered), width="stretch", hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
