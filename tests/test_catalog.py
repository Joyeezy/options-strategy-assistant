import pandas as pd

from options_strategy_assistant.catalog import compare_table, filter_catalog


def sample_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "买入看涨",
                "name_en": "Long Call",
                "strategy_family": "单腿方向",
                "objective_tags": ["方向表达"],
                "direction_tags": ["看涨"],
                "volatility_tags": ["波动率上行"],
                "time_value_profile": "买时间",
                "holding_requirement": "无持仓要求",
                "capital_profile": "权利金型",
                "risk_level": 3,
                "risk_label": "3 级（中风险）",
                "risk_bucket": "中风险",
                "max_profit": "无限",
                "max_loss": "有限",
                "breakeven": "行权价 + 权利金",
                "margin_summary": "以支付权利金为主，一般无追加保证金。",
                "greeks": "Delta>0，Theta<0，Vega>0",
                "summary": "适合偏看涨的市场判断。",
                "risk_note": "时间损耗需要重点关注。",
                "starter_friendly": True,
                "source_sheets": ["完整策略表"],
            },
            {
                "name": "盒式套利",
                "name_en": "Box Spread",
                "strategy_family": "套利",
                "objective_tags": ["套利"],
                "direction_tags": ["套利"],
                "volatility_tags": ["定价偏差"],
                "time_value_profile": "时间中性",
                "holding_requirement": "机构/套利账户",
                "capital_profile": "低杠杆套利型",
                "risk_level": 2,
                "risk_label": "2 级（低风险）",
                "risk_bucket": "低风险",
                "max_profit": "有限",
                "max_loss": "有限",
                "breakeven": "无传统盈亏平衡点",
                "margin_summary": "对成本、流动性和执行质量要求更高。",
                "greeks": "Delta≈0，Gamma≈0，Theta≈0，Vega≈0",
                "summary": "更适合关注定价偏差的专业账户。",
                "risk_note": "套利并不等于无风险。",
                "starter_friendly": False,
                "source_sheets": ["完整策略表", "Sheet2"],
            },
        ]
    )


def test_filter_catalog_by_direction() -> None:
    filtered = filter_catalog(sample_catalog(), direction="看涨")
    assert filtered["name"].tolist() == ["买入看涨"]


def test_compare_table_exposes_user_facing_columns() -> None:
    table = compare_table(sample_catalog())
    assert "策略" in table.columns
    assert "风险等级" in table.columns
