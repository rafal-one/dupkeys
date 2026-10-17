"""dupkeys: find duplicate keys in JSON, .env and INI/properties files."""
import argparse
import json
import re
import sys

__version__ = "0.1.0"


def find_json(text):
    """Return [(path, first_value_hint)] for duplicate keys in JSON text."""
    found = []

    def hook(pairs):
        seen = set()
        for k, _ in pairs:
            if k in seen:
                found.append(k)
            seen.add(k)
        return dict(pairs)

    json.loads(text, object_pairs_hook=hook)
    return found


def _line_keys(text, kind):
    section = ""
    seen = {}
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line[0] in "#;!":
            continue
        if kind == "ini" and line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            continue
        if kind == "env":
            line = re.sub(r"^export\s+", "", line)
            m = re.match(r"([A-Za-z_][A-Za-z0-9_.]*)\s*=", line)
        else:
            m = re.match(r"([^=:\s][^=:]*?)\s*[=:]", line)
        if not m:
            continue
        key = (section, m.group(1))
        if key in seen:
            name = (f"[{section}] " if section else "") + m.group(1)
            out.append((n, name, seen[key]))
        else:
            seen[key] = n
    return out


def check(path, text, kind=None):
    """Return list of (line_or_None, message)."""
    if kind is None:
        low = path.lower()
        base = low.rsplit("/", 1)[-1]
        if low.endswith(".json"):
            kind = "json"
        elif base.startswith(".env") or low.endswith(".env"):
            kind = "env"
        else:
            kind = "ini"
    if kind == "json":
        return [(None, f"duplicate key {k!r} (last value wins)") for k in find_json(text)]
    return [(n, f"duplicate key {name!r} (first at line {first}; last value wins)")
            for n, name, first in _line_keys(text, kind)]


def main(argv=None):
    p = argparse.ArgumentParser(prog="dupkeys", description=__doc__)
    p.add_argument("files", nargs="+")
    p.add_argument("--type", choices=["json", "env", "ini"], help="force file type")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    bad = err = False
    for f in a.files:
        try:
            with open(f, encoding="utf-8") as fh:
                text = fh.read()
            res = check(f, text, a.type)
        except (OSError, UnicodeDecodeError) as e:
            print(f"{f}: error: {e}", file=sys.stderr)
            err = True
            continue
        except ValueError as e:
            print(f"{f}: error: invalid JSON: {e}", file=sys.stderr)
            err = True
            continue
        for n, msg in res:
            print(f"{f}:{n}: {msg}" if n else f"{f}: {msg}")
            bad = True
    return 2 if err else (1 if bad else 0)


if __name__ == "__main__":
    sys.exit(main())
