"""
Emit commit trailers or a CI run summary from the newest journal entry.
Works with PyYAML if present; falls back to a simple parser if not.
"""

import sys
import os
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, ".squirrelfocus", "config.yaml")

try:
    import yaml  # type: ignore

    HAVE_YAML = True
except Exception:
    yaml = None
    HAVE_YAML = False

DEF_CFG = {
    "journals_dir": "journal_logs",
    "trailer_keys": ["fix", "why", "change", "proof", "ref"],
    "summary_format": (
        "### CI Triage\n"
        "- **Fix:** {{fix}}\n"
        "- **Why:** {{why}}\n"
        "- **Change:** {{change}}\n"
        "- **Proof:** {{proof}}\n"
    ),
}


def newest_md(jdir: str) -> str | None:
    pat = os.path.join(ROOT, jdir, "**", "*.md")
    files = [f for f in glob.glob(pat, recursive=True)]
    return max(files, key=os.path.getmtime) if files else None


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_text = parts[1]
    body = parts[2]
    if HAVE_YAML:
        try:
            return yaml.safe_load(fm_text) or {}, body  # type: ignore
        except Exception:
            return {}, body
    fm = {}
    trailers = {}
    lines = fm_text.splitlines()
    in_tr = False
    for ln in lines:
        if ln.strip() == "trailers:":
            in_tr = True
            continue
        if in_tr:
            if ln.startswith(" ") or ln.startswith("\t"):
                s = ln.strip()
                if ":" in s:
                    k, v = s.split(":", 1)
                    trailers[k.strip()] = v.strip().strip('"').strip("'")
            else:
                in_tr = False
    if trailers:
        fm["trailers"] = trailers
    return fm, body


def load_cfg() -> dict:
    if HAVE_YAML and os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            out = dict(DEF_CFG)
            out.update({k: v for k, v in data.items() if v is not None})
            return out
        except Exception:
            pass
    return dict(DEF_CFG)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "trailers"
    cfg = load_cfg()
    jdir = cfg.get("journals_dir", "journal_logs")
    keys = cfg.get("trailer_keys", [])
    tmpl = cfg.get("summary_format", "")
    path = newest_md(jdir)
    if not path:
        print("", end="")
        return
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    fm, _ = split_frontmatter(text)
    trailers = (fm or {}).get("trailers", {}) or {}
    if mode == "trailers":
        lines = []
        for k in keys:
            val = str(trailers.get(k, "")).strip()
            if val:
                lines.append(f"{k}: {val}")
        print("\n".join(lines))
        return
    if mode == "summary":
        msg = tmpl
        for k in keys:
            msg = msg.replace("{{" + k + "}}", str(trailers.get(k, "")))
        print(msg)
        return
    print("", end="")


if __name__ == "__main__":
    main()
