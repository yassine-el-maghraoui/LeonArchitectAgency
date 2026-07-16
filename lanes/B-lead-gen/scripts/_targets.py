"""Minimal parser for config/targets.yaml — stdlib only (no PyYAML,
consistent with the project's "no install required" constraint).

Only supports the fixed structure of targets.yaml (market/segments/cities/goals).
If the file's shape changes, update this parser accordingly.
"""

from pathlib import Path

from _common import REPO_ROOT

TARGETS_FILE = REPO_ROOT / "config" / "targets.yaml"


def _strip_comment(line: str) -> str:
    # split on " #" so we don't break on a '#' inside a value like Greek "π" etc.
    idx = line.find(" #")
    return line if idx == -1 else line[:idx]


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'")


def load_targets(path: Path = TARGETS_FILE) -> dict:
    data: dict = {"market": {}, "segments": [], "cities": [], "goals": {}}
    section = None
    current: dict | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            current = None
            continue

        if section == "market":
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                v = _clean(v)
                if k.strip() == "language_hints":
                    v = [x.strip() for x in v.strip("[]").split(",") if x.strip()]
                data["market"][k.strip()] = v

        elif section == "goals":
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                v = _clean(v)
                data["goals"][k.strip()] = int(v) if v.isdigit() else v

        elif section in ("segments", "cities"):
            if indent == 6 and stripped.startswith("- "):
                # nested list (query_terms)
                if current is not None:
                    current.setdefault("query_terms", []).append(_clean(stripped[2:]))
            elif indent == 2 and stripped.startswith("- "):
                current = {"query_terms": []} if section == "segments" else {}
                data[section].append(current)
                rest = stripped[2:]
                if ":" in rest:
                    k, _, v = rest.partition(":")
                    current[k.strip()] = _clean(v)
            elif current is not None and ":" in stripped and not stripped.endswith(":"):
                k, _, v = stripped.partition(":")
                v = _clean(v)
                if k.strip() == "priority" and v.isdigit():
                    v = int(v)
                current[k.strip()] = v

    return data


if __name__ == "__main__":
    import json

    print(json.dumps(load_targets(), ensure_ascii=False, indent=2))
