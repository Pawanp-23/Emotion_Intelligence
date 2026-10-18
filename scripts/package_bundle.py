"""Zip a trained model bundle so another computer can run RAMEI without retraining.

    python scripts/package_bundle.py                      # -> ramei-model-bundle.zip
    python scripts/package_bundle.py --name ramei-rgcmt-1.0.0 --out D:/share/bundle.zip

Paths inside the zip use forward slashes, so it extracts correctly on Windows, macOS and Linux.
Extract it into ml/artifacts/bundles/ on the other computer (see docs/RUN-ON-ANOTHER-COMPUTER.md).
"""

import argparse
import zipfile
from pathlib import Path

BUNDLES = Path(__file__).resolve().parents[1] / "ml" / "artifacts" / "bundles"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--name", default="ramei-rgcmt-1.0.0", help="bundle folder name")
    p.add_argument("--out", type=Path, default=Path("ramei-model-bundle.zip"))
    args = p.parse_args()

    src = BUNDLES / args.name
    if not (src / "manifest.json").is_file():
        raise SystemExit(f"No bundle at {src} (run ml/scripts/run_m2.py first, or check --name)")
    files = sorted(f for f in src.rglob("*") if f.is_file())
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f.relative_to(BUNDLES).as_posix())
    with zipfile.ZipFile(args.out) as z:
        if z.testzip() is not None:
            raise SystemExit("Zip verification failed")
    print(f"wrote {args.out} ({args.out.stat().st_size / 1e6:.1f} MB, {len(files)} files)")


if __name__ == "__main__":
    main()
