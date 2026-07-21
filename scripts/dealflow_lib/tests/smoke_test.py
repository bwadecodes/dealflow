#!/usr/bin/env python3
"""Smoke test for dealflow_lib foundational infra.

Builds a fake deal folder, exercises state + index + excel author
end-to-end, prints PASS/FAIL. Run from anywhere:

    python3 scripts/dealflow_lib/tests/smoke_test.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Make scripts/ importable
_SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_SCRIPTS))

from dealflow_lib import excel, firmstyle, index, pdf, state  # noqa: E402


def _check(label: str, cond: bool, detail: str = "") -> None:
    mark = "✓" if cond else "✗"
    line = f"  {mark} {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    if not cond:
        raise AssertionError(label)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="dealflow-smoke-"))
    deal = tmp / "Acme-Corp"
    deal.mkdir()
    # plant a fake source file
    src = deal / "financials" / "Q3-PnL.csv"
    src.parent.mkdir(parents=True)
    src.write_text("month,revenue,gm\n2024-07,200000,0.58\n", encoding="utf-8")

    print(f"Smoke test in {tmp}")
    failures: list[str] = []
    try:
        # --- state ---
        print("\n[state]")
        s = state.init_state(deal, deal_name="Acme Corp")
        _check("init_state created file", (deal / ".dealflow" / "deal-state.yaml").exists())
        _check("default stage is prescreen", s["stage"] == "prescreen", s["stage"])
        state.add_skill_run(deal, "dealflow-prescreen", "reports/x.md")
        state.set_stage(deal, "diligence")
        state.add_decision(deal, "Pursue at $40M pre")
        s = state.read_state(deal)
        _check("skill_run appended", len(s["skills_run"]) == 1)
        _check("stage updated", s["stage"] == "diligence", s["stage"])
        _check("decision added", len(s["key_decisions"]) == 1)

        # --- index ---
        print("\n[index]")
        index.init_index(deal)
        _check("init_index created file", (deal / ".dealflow" / "index.jsonl").exists())
        rec = index.add_or_update_record(
            deal,
            path="financials/Q3-PnL.csv",
            category="financials",
            type_="csv",
            size_bytes=src.stat().st_size,
            hash_=index.hash_file(src),
            indexed_by="smoke-test",
            summary="Q3 2024 monthly P&L",
            tags=["gross_margin", "revenue"],
        )
        _check("record added", rec["path"] == "financials/Q3-PnL.csv")
        index.add_fact(
            deal,
            path="financials/Q3-PnL.csv",
            fact="Jul 2024 revenue: $200K",
            source_ref="row 2",
            added_by="smoke-test",
        )
        rec = index.get_record(deal, "financials/Q3-PnL.csv")
        _check("fact appended", rec is not None and len(rec["key_facts"]) == 1)
        hits = index.query(deal, substring="Jul 2024")
        _check("substring query returns hit", len(hits) == 1)
        hits = index.query(deal, tags=["gross_margin"])
        _check("tag query returns hit", len(hits) == 1)
        _check("is_stale false for unchanged", not index.is_stale(deal, "financials/Q3-PnL.csv"))
        # mutate the file
        src.write_text("month,revenue,gm\n2024-07,200000,0.58\n2024-08,220000,0.60\n", encoding="utf-8")
        _check("is_stale true after mutation", index.is_stale(deal, "financials/Q3-PnL.csv"))

        # --- firmstyle ---
        print("\n[firmstyle]")
        profile = firmstyle.load_profile(Path("/nonexistent"))
        _check("defaults loaded when no profile", profile["version"] == 1)
        _check(
            "default tone is IC-ready baseline",
            profile["voice"]["tone"].startswith("IC-ready:")
            and "no coined jargon" in profile["voice"]["tone"],
        )
        _check("brand defaults present", "primary_color" in firmstyle.get_brand(profile))

        # --- excel ---
        print("\n[excel]")
        author = excel.ExcelAuthor(firm_style=profile)
        wb = author.new_workbook(title="Smoke Test Analysis")
        author.add_source_tab(
            wb,
            "Source",
            rows=[["month", "revenue"], ["2024-07", 200000], ["2024-08", 220000]],
        )
        author.add_calc_tab(
            wb,
            "Calcs",
            header=["month", "revenue", "growth_mom"],
            rows=[
                ["2024-07", "=Source!B2", ""],
                ["2024-08", "=Source!B3", "=B3/B2-1"],
            ],
            input_columns=[1],
            output_columns=[3],
        )
        author.add_method_tab(wb, "Pulled revenue from Source!B2:B3.\nGrowth_mom = B/A - 1.")
        author.add_summary_tab(wb, "Summary", ["Revenue grew 10% MoM", "Sample size: 2 months"], title="Findings")
        xlsx_path = tmp / "smoke.xlsx"
        author.save(wb, xlsx_path)
        _check("xlsx written", xlsx_path.exists())
        _check("xlsx non-empty", xlsx_path.stat().st_size > 1000)

        # --- pdf ---
        print("\n[pdf]")
        renderer = pdf.renderer_available()
        _check("renderer detection runs", True, f"renderer={renderer or 'none'}")
        if renderer:
            md = tmp / "doc.md"
            md.write_text("# Hello\n\nThis is a **smoke test** PDF.\n", encoding="utf-8")
            pdf_path = tmp / "doc.pdf"
            try:
                pdf.md_to_pdf(md, pdf_path, firm_style=profile, title="Smoke")
                _check("pdf rendered", pdf_path.exists() and pdf_path.stat().st_size > 500)
            except pdf.PdfRendererNotAvailable as exc:
                print(f"  (skipped pdf render — {exc})")
        else:
            print("  (skipped pdf render — no renderer installed; this is OK)")

    except AssertionError as exc:
        failures.append(str(exc))
    finally:
        # leave tmp around if there were failures, for inspection
        if not failures:
            shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print(f"FAIL — {len(failures)} check(s) failed. Tmp dir kept: {tmp}")
        return 1
    print("PASS — all foundational utilities working")
    return 0


if __name__ == "__main__":
    sys.exit(main())
