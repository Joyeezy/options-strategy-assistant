from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "data" / "strategy_catalog.json"


def load_catalog(catalog_path: Path | None = None) -> pd.DataFrame:
    path = catalog_path or DEFAULT_CATALOG_PATH
    records = json.loads(path.read_text(encoding="utf-8"))
    dataframe = pd.DataFrame(records)
    if dataframe.empty:
        return dataframe
    dataframe["objective_tags"] = dataframe["objective_tags"].apply(list)
    dataframe["direction_tags"] = dataframe["direction_tags"].apply(list)
    dataframe["volatility_tags"] = dataframe["volatility_tags"].apply(list)
    dataframe["source_sheets"] = dataframe["source_sheets"].apply(list)
    return dataframe


def _contains_tag(value: str, tags: list[str]) -> bool:
    if value == "全部":
        return True
    return value in tags


def filter_catalog(
    dataframe: pd.DataFrame,
    *,
    direction: str = "全部",
    volatility: str = "全部",
    time_value: str = "全部",
    risk_bucket: str = "全部",
    holding_requirement: str = "全部",
    objective: str = "全部",
    keyword: str = "",
) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe
    filtered = dataframe.copy()
    filtered = filtered[filtered["direction_tags"].map(lambda tags: _contains_tag(direction, tags))]
    filtered = filtered[filtered["volatility_tags"].map(lambda tags: _contains_tag(volatility, tags))]
    if time_value != "全部":
        filtered = filtered[filtered["time_value_profile"] == time_value]
    if risk_bucket != "全部":
        filtered = filtered[filtered["risk_bucket"] == risk_bucket]
    if holding_requirement != "全部":
        filtered = filtered[filtered["holding_requirement"] == holding_requirement]
    if objective != "全部":
        filtered = filtered[filtered["objective_tags"].map(lambda tags: _contains_tag(objective, tags))]
    normalized = keyword.strip().lower()
    if normalized:
        filtered = filtered[
            filtered["name"].str.lower().str.contains(normalized)
            | filtered["name_en"].fillna("").str.lower().str.contains(normalized)
            | filtered["summary"].str.lower().str.contains(normalized)
            | filtered["strategy_family"].str.lower().str.contains(normalized)
        ]
    return filtered.sort_values(
        by=["starter_friendly", "risk_level", "strategy_family", "name"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)


def compare_table(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe
    view = dataframe.copy()
    view["方向"] = view["direction_tags"].map(lambda tags: " / ".join(tags))
    view["波动率判断"] = view["volatility_tags"].map(lambda tags: " / ".join(tags))
    view["策略目的"] = view["objective_tags"].map(lambda tags: " / ".join(tags))
    view["公开版推荐"] = view["starter_friendly"].map(lambda value: "适合先看" if value else "进阶再看")
    return view[
        [
            "name",
            "strategy_family",
            "方向",
            "波动率判断",
            "time_value_profile",
            "risk_bucket",
            "holding_requirement",
            "策略目的",
            "max_profit",
            "max_loss",
            "公开版推荐",
        ]
    ].rename(
        columns={
            "name": "策略",
            "strategy_family": "策略家族",
            "time_value_profile": "时间价值",
            "risk_bucket": "风险等级",
            "holding_requirement": "持仓基础",
            "max_profit": "最大盈利",
            "max_loss": "最大亏损",
        }
    )


def summary_metrics(dataframe: pd.DataFrame) -> dict[str, Any]:
    if dataframe.empty:
        return {
            "count": 0,
            "starter_count": 0,
            "high_risk_count": 0,
            "hedge_count": 0,
        }
    high_risk = int((dataframe["risk_bucket"] == "高风险").sum())
    hedge_count = int(dataframe["objective_tags"].map(lambda tags: "风险对冲" in tags).sum())
    starter_count = int(dataframe["starter_friendly"].sum())
    return {
        "count": int(len(dataframe)),
        "starter_count": starter_count,
        "high_risk_count": high_risk,
        "hedge_count": hedge_count,
    }
