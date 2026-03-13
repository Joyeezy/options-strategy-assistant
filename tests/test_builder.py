from options_strategy_assistant.builder import (
    direction_tags,
    risk_level_from_label,
    starter_friendly,
    time_value_profile,
    volatility_tags,
)


def test_risk_level_from_label() -> None:
    assert risk_level_from_label("2 级（低风险）") == 2


def test_time_value_profile_prefers_theta_sign() -> None:
    assert time_value_profile("Delta>0，Theta<0，Vega>0", "") == "买时间"
    assert time_value_profile("Delta<0，Theta>0，Vega<0", "") == "卖时间"


def test_direction_and_volatility_tags_are_derived_from_text() -> None:
    directions = direction_tags("买入跨式", "方向不明，预期标的大幅波动，波动率上行", "", "波动率组合")
    assert "双向波动" in directions
    volatilities = volatility_tags("方向不明，预期标的大幅波动，波动率上行", "", "Gamma>0，Theta<0，Vega>0", "波动率组合")
    assert "波动率上行" in volatilities


def test_starter_friendly_filters_unlimited_loss() -> None:
    assert not starter_friendly(2, "无限（标的上涨无上限）", "无持仓要求", "单腿方向")
    assert starter_friendly(2, "有限（净权利金支出）", "无持仓要求", "方向价差")
