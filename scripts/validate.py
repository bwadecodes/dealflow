#!/usr/bin/env python3
"""Validate dealflow repository structure and file formats."""
import sys
import os
import json
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXPECTED_FILES = [
    "SKILL.md",
    "package.json",
    "LICENSE",
    "CHANGELOG.md",
    ".claude-plugin/plugin.json",
    "config/defaults/pe-lower-middle-market.yaml",
    "config/defaults/vc-seed-preseed.yaml",
    "config/defaults/growth-equity.yaml",
    "config/example-config.yaml",
    "dd-setup/SKILL.md",
    "dd-dataroom/SKILL.md",
    "dd-model/SKILL.md",
    "dd-questions/SKILL.md",
    "docs/cli-quickstart.md",
    "docs/it-compliance-guide.md",
    "docs/rubric-guide.md",
]


def check_files_exist():
    errors = []
    for f in EXPECTED_FILES:
        path = os.path.join(ROOT, f)
        if not os.path.isfile(path):
            errors.append(f"Missing: {f}")
    return errors


def check_yaml_files():
    try:
        import yaml
    except ImportError:
        return ["PyYAML not installed (run: pip install pyyaml) — skipping YAML checks"]
    errors = []
    yaml_files = [f for f in EXPECTED_FILES if f.endswith(".yaml")]
    for f in yaml_files:
        path = os.path.join(ROOT, f)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    yaml.safe_load(fh)
            except yaml.YAMLError as e:
                errors.append(f"Invalid YAML in {f}: {e}")
    return errors


def check_json_files():
    errors = []
    json_files = [f for f in EXPECTED_FILES if f.endswith(".json")]
    for f in json_files:
        path = os.path.join(ROOT, f)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    json.load(fh)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in {f}: {e}")
    return errors


def check_skill_frontmatter():
    errors = []
    skill_files = [f for f in EXPECTED_FILES if f.endswith("SKILL.md")]
    for f in skill_files:
        path = os.path.join(ROOT, f)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            if not content.startswith("---"):
                errors.append(f"Missing frontmatter in {f}")
            elif len(content.split("---", 2)) < 3:
                errors.append(f"Incomplete frontmatter in {f}")
    return errors


def main():
    all_errors = []
    all_errors.extend(check_files_exist())
    all_errors.extend(check_yaml_files())
    all_errors.extend(check_json_files())
    all_errors.extend(check_skill_frontmatter())

    if all_errors:
        print(f"FAIL — {len(all_errors)} issue(s):")
        for e in all_errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"PASS — all {len(EXPECTED_FILES)} files validated")
        sys.exit(0)


if __name__ == "__main__":
    main()
