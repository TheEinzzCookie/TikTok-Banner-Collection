#!/usr/bin/env python3
"""
Build Banner/manifest.json with multi-category support.

Usage (from anywhere):
    python banner.py

The script always works relative to its own location,
so it doesn't matter from which folder you run it.
"""

import json
import os
import sys
from datetime import datetime, timezone

EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

ROOT = os.path.dirname(os.path.abspath(__file__))

if not os.path.isdir(ROOT):
    sys.exit(f"Folder not found: {ROOT}")

banners = []

for cat in sorted(os.listdir(ROOT), key=str.lower):
    cdir = os.path.join(ROOT, cat)

    if cat.startswith(".") or not os.path.isdir(cdir):
        continue

    meta = {}
    meta_path = os.path.join(cdir, "meta.json")
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as e:
            print(f"! could not read {meta_path}: {e}")

    for fn in sorted(os.listdir(cdir), key=str.lower):
        if os.path.splitext(fn)[1].lower() not in EXTS:
            continue

        m = meta.get(fn, {})
        mtime = os.stat(os.path.join(cdir, fn)).st_mtime
        date = m.get("date") or datetime.fromtimestamp(mtime, timezone.utc).isoformat()

        cats = m.get("categories")
        if isinstance(cats, list) and cats:
            categories = [str(c).strip() for c in cats if str(c).strip()]
        else:
            categories = [cat]

        if cat not in categories:
            categories.insert(0, cat)

        entry = {
            "path": f"{cat}/{fn}",
            "categories": categories,
            "date": date,
        }

        if m.get("title"):
            entry["title"] = m["title"]
        if m.get("description"):
            entry["description"] = m["description"]

        banners.append(entry)

out = os.path.join(ROOT, "manifest.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(
        {
            "generated": datetime.now(timezone.utc).isoformat(),
            "banners": banners,
        },
        f,
        ensure_ascii=False,
        indent=1,
    )

unique_cats = set()
for b in banners:
    unique_cats.update(b["categories"])

print(f"{len(banners)} banners in {len(unique_cats)} categories → {out}")