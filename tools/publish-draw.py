#!/usr/bin/env python3
"""Turn a raw comment export into a published draw.

Reads a raw Instagram comment export, applies the giveaway's entry rules,
writes the redacted data files, rewrites the wheel's built-in dataset, and
optionally commits and pushes. The raw export itself is never copied into
the repo and is git-ignored.

    python3 tools/publish-draw.py my_export.csv --push

The entry rules match the ones the web page applies, so the wheel you
publish and the wheel you get by dropping the same file into the page in
your browser are the same wheel.
"""

import argparse
import collections
import csv
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

USER_NAMES = ["username", "user", "owner", "author", "handle", "commenter", "from"]
TYPE_NAMES = ["type", "kind"]
TAG_NAMES = ["tagged_accounts", "tagged", "mentions", "tags"]
TEXT_NAMES = ["comment", "text", "message", "body", "caption"]
TIME_NAMES = ["timestamp_pt", "timestamp_utc", "timestamp", "time", "date", "created"]

MENTION = re.compile(r"@([A-Za-z0-9._]+)")


def find_col(headers, names):
    lowered = [h.strip().lower() for h in headers]
    for want in names:
        if want in lowered:
            return lowered.index(want)
    for want in names:
        for i, h in enumerate(lowered):
            if want in h:
                return i
    return -1


def mentions(value):
    return [m.lower().rstrip(".") for m in MENTION.findall(value or "")]


def tally(rows, cols, opts):
    """Apply the entry rules. Returns (entrants, kept_rows, dropped_counts)."""
    counts = collections.Counter()
    seen_pair = set()
    kept = []
    drop = collections.Counter()
    host = opts.host.strip().lower().lstrip("@")

    for row in rows:
        def cell(i):
            return row[i] if 0 <= i < len(row) else ""

        user = cell(cols["user"]).strip().lstrip("@")
        if not user:
            drop["blank rows"] += 1
            continue
        lower = user.lower()

        if opts.top_level_only and cols["type"] != -1:
            kind = cell(cols["type"]).strip().lower()
            if kind and kind != "comment":
                drop["replies"] += 1
                continue

        source = cell(cols["tags"]) if cols["tags"] != -1 else cell(cols["text"])
        tags = mentions(source)

        if host and lower == host:
            drop["from the host"] += 1
            continue
        tags = [t for t in tags if t != host]
        self_tagged = lower in tags
        tags = [t for t in tags if t != lower]

        can_check_tags = cols["tags"] != -1 or cols["text"] != -1
        if opts.require_tag and can_check_tags and not tags:
            drop["self-tags" if self_tagged else "with no tag"] += 1
            continue

        if opts.unique_tags and tags:
            fresh = False
            for t in tags:
                key = (lower, t)
                if key not in seen_pair:
                    seen_pair.add(key)
                    fresh = True
            if not fresh:
                drop["repeat tags"] += 1
                continue

        counts[user] += 1
        kept.append({
            "type": cell(cols["type"]) if cols["type"] != -1 else "comment",
            "username": user,
            "tag_count": len(tags),
            "timestamp": cell(cols["time"]),
        })

    entrants = [(u, n if opts.per_comment else 1) for u, n in counts.items()]
    entrants.sort(key=lambda r: (-r[1], r[0]))
    return entrants, kept, drop


def write_data(entrants, kept):
    data = ROOT / "data"
    data.mkdir(exist_ok=True)
    total = sum(n for _, n in entrants)

    with (data / "entrants.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["username", "entries", "share_pct"])
        for u, n in entrants:
            w.writerow([u, n, f"{n / total * 100:.2f}"])

    with (data / "entries-redacted.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["type", "username", "tag_count", "timestamp"])
        for k in kept:
            w.writerow([k["type"], k["username"], k["tag_count"], k["timestamp"]])

    return total


def js_string(text):
    """A JS double-quoted literal. json.dumps escapes exactly what JS needs."""
    return json.dumps(text, ensure_ascii=False)


def rewrite_page(entrants, total, opts, note):
    page = ROOT / "index.html"
    src = page.read_text(encoding="utf-8")
    before = src

    array = json.dumps([[u, n] for u, n in entrants], ensure_ascii=False, separators=(",", ""))
    src = re.sub(
        r"var SEED_ENTRANTS = \[.*?\];",
        lambda _: f"var SEED_ENTRANTS = {array};",
        src,
        count=1,
        flags=re.S,
    )
    src = re.sub(r"(\n    winners: )\d+,", lambda m: f"{m.group(1)}{opts.winners},", src, count=1)
    src = re.sub(
        r"(\n    eyebrow: )\"(?:[^\"\\]|\\.)*\",",
        lambda m: f"{m.group(1)}{js_string(opts.eyebrow)},",
        src, count=1,
    )
    src = re.sub(
        r"(\n    subline: )\"(?:[^\"\\]|\\.)*\",",
        lambda m: f"{m.group(1)}{js_string(opts.subline)},",
        src, count=1,
    )
    src = re.sub(
        r"(\n    slots: )\"(?:[^\"\\]|\\.)*\",",
        lambda m: f"{m.group(1)}{js_string(opts.slots)},",
        src, count=1,
    )
    # note is the last key in SEED and may span several concatenated lines
    src = re.sub(
        r"\n    note: [\s\S]*?\n  \};",
        lambda _: f"\n    note: {js_string(note)}\n  }};",
        src, count=1,
    )
    # the pre-JS markup values, so the first painted frame is already correct
    src = re.sub(r'(id="fEntries">)\d+', lambda m: f"{m.group(1)}{total}", src, count=1)
    src = re.sub(r'(id="fEntrants">)\d+', lambda m: f"{m.group(1)}{len(entrants)}", src, count=1)
    src = re.sub(r'(id="fWinners">)\d+', lambda m: f"{m.group(1)}{opts.winners}", src, count=1)

    if src == before:
        sys.exit("index.html was not modified — its markers may have changed. Nothing written.")
    page.write_text(src, encoding="utf-8")


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="raw comment export (stays local; never committed)")
    ap.add_argument("--winners", type=int, default=3)
    ap.add_argument("--host", default="supersweetbyqiao", help="host account to ignore")
    ap.add_argument("--eyebrow", default="new draw")
    ap.add_argument("--subline", default="@supersweetbyqiao — giveaway")
    ap.add_argument("--slots", default="Winners")
    ap.add_argument("--deadline", default="", help="deadline sentence for the fine print")
    ap.add_argument("--keep-replies", dest="top_level_only", action="store_false",
                    help="count replies as entries too")
    ap.add_argument("--no-tag-required", dest="require_tag", action="store_false",
                    help="do not require an @ mention")
    ap.add_argument("--allow-repeat-tags", dest="unique_tags", action="store_false",
                    help="tagging the same friend again earns another entry")
    ap.add_argument("--one-per-person", dest="per_comment", action="store_false",
                    help="every account gets a single entry")
    ap.add_argument("--push", action="store_true", help="commit and push when done")
    opts = ap.parse_args()

    path = pathlib.Path(opts.csv)
    if not path.exists():
        sys.exit(f"No such file: {path}")

    with path.open(newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    if len(rows) < 2:
        sys.exit("That file has no data rows.")

    headers = rows[0]
    cols = {
        "user": find_col(headers, USER_NAMES),
        "type": find_col(headers, TYPE_NAMES),
        "tags": find_col(headers, TAG_NAMES),
        "text": find_col(headers, TEXT_NAMES),
        "time": find_col(headers, TIME_NAMES),
    }
    if cols["user"] == -1:
        sys.exit("No username column found. Expected one named username, user, author or handle.")

    entrants, kept, drop = tally(rows[1:], cols, opts)
    if not entrants:
        sys.exit("No entries survived the rules — nothing to publish.")

    total = write_data(entrants, kept)
    opts.winners = max(1, min(opts.winners, len(entrants)))

    times = sorted(k["timestamp"] for k in kept if k["timestamp"])
    span = f", {times[0][:10]} to {times[-1][:10]}" if times else ""
    note = (
        f"{total} {'entries' if opts.per_comment else 'entrants'} from {len(entrants)} accounts{span}. "
        + (f"{opts.deadline.rstrip('.')}. " if opts.deadline else "")
        + ("Replies are excluded. " if opts.top_level_only else "")
        + ("Tagging the same friend twice does not earn a second entry. " if opts.unique_tags else "")
        + ("Each qualifying comment counts as one entry."
           if opts.per_comment else "Each account counts once, however many times they commented.")
    )
    rewrite_page(entrants, total, opts, note)

    print(f"  entrants   {len(entrants)}")
    print(f"  entries    {total}")
    print(f"  winners    {opts.winners}")
    print("  excluded   " + (", ".join(f"{n} {why}" for why, n in drop.most_common()) or "nothing"))
    print("\nwrote data/entrants.csv, data/entries-redacted.csv, index.html")
    print(f"raw export left where it is, untracked: {path}")

    if opts.push:
        git("add", "index.html", "data/entrants.csv", "data/entries-redacted.csv")
        git("commit", "-m", f"Load a new draw: {len(entrants)} entrants, {total} entries")
        git("push")
        print("\npushed — GitHub Pages will rebuild in a minute or so")
    else:
        print("\nnothing committed. Re-run with --push to commit and deploy.")


if __name__ == "__main__":
    main()
