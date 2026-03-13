from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from options_strategy_assistant.builder import build_catalog, write_catalog


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a public strategy catalog from a local workbook.")
    parser.add_argument("--source", required=True, help="Absolute or relative path to the local .xlsx workbook.")
    parser.add_argument(
        "--output",
        default=str(PROJECT_ROOT / "data" / "strategy_catalog.json"),
        help="Output path for the generated public JSON catalog.",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    records = build_catalog(source_path)
    write_catalog(records, output_path)
    print(f"Generated {len(records)} strategies -> {output_path}")


if __name__ == "__main__":
    main()
