#!/usr/bin/env python3
"""
Anki Add-on Packager

Creates a .ankiaddon file (a ZIP archive) from an add-on source directory,
suitable for uploading to AnkiWeb or sharing directly.

Key points (per Anki add-on docs and common practice):
- The .ankiaddon is just a ZIP with a different extension.
- Place your add-on files at the ROOT of the archive (do NOT wrap them in an extra folder).
- Exclude meta.json (Anki generates it on install) and typical junk/build files.
- Exclude __pycache__, *.pyc, VCS folders, node_modules, etc.

Usage examples:
  python scripts/package_anki_addon.py -s path/to/addon_root
  python scripts/package_anki_addon.py -s . -o dist --name my-addon --version 1.0.0
  python scripts/package_anki_addon.py -s addon_dir --exclude "tests" --exclude "*.log"

After running, upload the resulting .ankiaddon file to AnkiWeb.
Docs: https://addon-docs.ankiweb.net/ (see Sharing/Packaging guidance)
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Iterable, List, Set


DEFAULT_EXCLUDES = [
    # VCS & IDE
    ".git", ".hg", ".svn", ".idea", ".vscode",
    # Python caches & envs
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "venv", ".venv", "env", ".env",
    # Node/build artifacts
    "node_modules", "dist", "build",
    # OS junk
    ".DS_Store", "Thumbs.db", "desktop.ini",
    # Compiled/python/object files
    "*.pyc", "*.pyo", "*.pyd",
    # Native objects (rare in add-ons; exclude if you don't intend to ship binaries)
    "*.so", "*.dylib", "*.dll", "*.exe",
    # Logs & misc
    "*.log",
    # Anki-managed metadata (should NOT be included in packages)
    "meta.json",
]


def normalize_patterns(patterns: Iterable[str]) -> List[str]:
    norm: List[str] = []
    for p in patterns:
        p = p.strip()
        if not p:
            continue
        # Normalize path separators for cross-platform matching
        p = p.replace("\\", "/")
        norm.append(p)
    return norm


def should_exclude(rel_path: str, patterns: List[str]) -> bool:
    # Ensure forward slashes for matching
    rp = rel_path.replace("\\", "/")

    # Test pattern against the whole path, and against each segment
    segments = rp.split("/")

    for pat in patterns:
        # Match entire path
        if fnmatch.fnmatch(rp, pat):
            return True
        # Match any segment
        if any(fnmatch.fnmatch(seg, pat) for seg in segments):
            return True
    return False


def iter_files(root: Path, exclude_patterns: List[str], exclude_under: Set[Path]) -> Iterable[Path]:
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dpath = Path(dirpath)

        # Skip excluded parent trees early
        skip_tree = False
        for ex in exclude_under:
            try:
                dpath.relative_to(ex)
                skip_tree = True
                break
            except ValueError:
                pass
        if skip_tree:
            continue

        # Prune directories in-place if they match excludes
        pruned: List[str] = []
        for dn in list(dirnames):
            rel = (Path(dirpath) / dn).relative_to(root).as_posix()
            if should_exclude(rel, exclude_patterns):
                dirnames.remove(dn)
                pruned.append(dn)
        # Optionally could print pruned dirs in verbose mode

        for fn in filenames:
            p = Path(dirpath) / fn
            rel = p.relative_to(root).as_posix()
            if should_exclude(rel, exclude_patterns):
                continue
            yield p


def make_archive(
    source_dir: Path,
    output_path: Path,
    excludes: List[str],
    verbose: bool = False,
) -> int:
    source_dir = source_dir.resolve()
    output_path = output_path.resolve()

    # Ensure parent exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Avoid including the output file itself if packaging from the same folder
    exclude_under: Set[Path] = set()
    if output_path.is_file():
        exclude_under.add(output_path)
    else:
        # Exclude the output directory tree if it's inside the source
        try:
            out_rel = output_path.parent.resolve().relative_to(source_dir)
            exclude_under.add(output_path.parent.resolve())
        except ValueError:
            pass

    # Open zip
    count = 0
    with zipfile.ZipFile(output_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fp in iter_files(source_dir, excludes, exclude_under):
            # Archive name should be relative to source, placed at zip root
            arcname = fp.relative_to(source_dir).as_posix()
            if verbose:
                print(f"+ {arcname}")
            zf.write(fp, arcname)
            count += 1

    return count


def derive_output_name(name: str | None, version: str | None, fallback: str) -> str:
    base = name or fallback or "addon"
    if version:
        return f"{base}-{version}.ankiaddon"
    # Timestamped fallback for uniqueness
    ts = time.strftime("%Y%m%d-%H%M%S")
    return f"{base}-{ts}.ankiaddon"


def validate_source_is_addon_root(source_dir: Path) -> None:
    # Heuristic checks with gentle warnings only
    expected_files = ["__init__.py"]
    hints = []
    for f in expected_files:
        if not (source_dir / f).exists():
            hints.append(f"Warning: '{f}' not found in {source_dir}. Is this the add-on root?")
    if (source_dir / "meta.json").exists():
        hints.append("Warning: meta.json is managed by Anki and should not be packaged; it will be excluded.")
    if hints:
        for h in hints:
            print(h, file=sys.stderr)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package an Anki add-on into a .ankiaddon file.")
    parser.add_argument("-s", "--source", type=Path, default=Path("."), help="Path to add-on root directory (default: current directory)")
    parser.add_argument("-o", "--output", type=Path, default=Path("dist"), help="Output directory or full file path. If a directory, a filename will be generated.")
    parser.add_argument("--name", type=str, default=None, help="Base name for the output file (e.g., 'my-addon'). Defaults to source directory name.")
    parser.add_argument("--version", type=str, default=None, help="Optional version tag for the output filename (e.g., '1.2.3').")
    parser.add_argument("-e", "--exclude", action="append", default=[], help="Glob or path patterns to exclude (can be repeated). Applied in addition to defaults.")
    parser.add_argument("--no-default-excludes", action="store_true", help="Do not apply the default exclude patterns.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing the archive.")
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    source_dir: Path = args.source
    if not source_dir.exists() or not source_dir.is_dir():
        print(f"Error: source directory not found: {source_dir}", file=sys.stderr)
        return 2

    validate_source_is_addon_root(source_dir)

    # Build excludes
    excludes: List[str] = [] if args.no_default_excludes else list(DEFAULT_EXCLUDES)
    excludes.extend(args.exclude or [])
    excludes = normalize_patterns(excludes)

    # Determine output path
    out_path: Path = args.output
    if out_path.suffix.lower() == ".ankiaddon":
        output_file = out_path
    elif out_path.is_dir() or out_path.suffix == "":
        base_name = args.name or source_dir.name
        fname = derive_output_name(base_name, args.version, fallback=source_dir.name)
        output_file = out_path / fname
    else:
        # Some non-.ankiaddon filename provided; normalize to .ankiaddon
        output_file = out_path.with_suffix(".ankiaddon")

    if args.verbose:
        print("Source:", source_dir)
        print("Output:", output_file)
        print("Excludes:")
        for p in excludes:
            print("  -", p)

    if args.dry_run:
        # Just list files that would be included
        count = 0
        for fp in iter_files(source_dir, excludes, exclude_under=set()):
            rel = fp.relative_to(source_dir)
            print(rel.as_posix())
            count += 1
        print(f"[dry-run] Would package {count} files into: {output_file}")
        return 0

    count = make_archive(source_dir, output_file, excludes, verbose=args.verbose)

    size = output_file.stat().st_size if output_file.exists() else 0
    print(f"Wrote {count} files -> {output_file} ({size:,} bytes)")
    print("You can now upload this .ankiaddon file to AnkiWeb.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

