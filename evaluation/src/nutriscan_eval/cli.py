import argparse
import asyncio
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from .candidates import DEFAULT_CANDIDATE_ORDER, PRICE_SNAPSHOT_DATE, get_candidates
from .costs import BudgetLedger
from .dataset import (
    load_manifest,
    prepare_public_dataset,
    validate_private_manifest,
    validate_public_manifest,
)
from .privacy import safe_error
from .provider import HuggingFaceProvider
from .runner import run_full_benchmark, run_smoke_tests


def _aliases(value: str) -> list[str]:
    aliases = [item.strip() for item in value.split(",") if item.strip()]
    get_candidates(aliases)
    return aliases


def _live_token() -> str:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        raise SystemExit(
            "HF_TOKEN is not set. Create a scoped token locally and source evaluation/.env."
        )
    return token


def _require_current_terms(args: argparse.Namespace) -> None:
    today = date.today().isoformat()
    if PRICE_SNAPSHOT_DATE != today:
        raise SystemExit(
            "The provider/price snapshot is stale. Recheck model availability, licenses, prices, "
            "and privacy terms, then update PRICE_SNAPSHOT_DATE before spending credit."
        )
    if not args.confirm_current_terms:
        raise SystemExit(
            "Recheck the linked Hugging Face/DeepInfra terms, then pass --confirm-current-terms."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NutriScan vision-model evaluation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-public", help="stream the public diagnostic set")
    prepare.add_argument("--output", type=Path, default=Path("artifacts/public"))
    prepare.add_argument("--per-class", type=int, default=5)

    private = subparsers.add_parser("validate-private", help="validate local private inputs")
    private.add_argument("--images", type=Path, required=True)
    private.add_argument("--manifest", type=Path, required=True)

    smoke = subparsers.add_parser("smoke", help="run one transport request per candidate")
    smoke.add_argument("--image", type=Path, required=True)
    smoke.add_argument("--output", type=Path, default=Path("artifacts/smoke"))
    smoke.add_argument("--models", type=_aliases, default=list(DEFAULT_CANDIDATE_ORDER))
    smoke.add_argument("--budget", type=Decimal, default=Decimal("1.00"))
    smoke.add_argument("--timeout", type=float, default=30.0)
    smoke.add_argument("--confirm-current-terms", action="store_true")

    run = subparsers.add_parser(
        "run", help="run the private selection gate and public diagnostic"
    )
    run.add_argument("--public-images", type=Path, required=True)
    run.add_argument("--public-manifest", type=Path, required=True)
    run.add_argument("--private-images", type=Path, required=True)
    run.add_argument("--private-manifest", type=Path, required=True)
    run.add_argument("--output", type=Path, default=Path("artifacts/results"))
    run.add_argument("--models", type=_aliases, default=list(DEFAULT_CANDIDATE_ORDER))
    run.add_argument("--budget", type=Decimal, default=Decimal("5.00"))
    run.add_argument("--timeout", type=float, default=30.0)
    run.add_argument("--confirm-current-terms", action="store_true")
    return parser


async def _smoke(args: argparse.Namespace) -> int:
    _require_current_terms(args)
    candidates = get_candidates(args.models)
    ledger = BudgetLedger(cap_usd=args.budget)
    async with HuggingFaceProvider(_live_token(), timeout_seconds=args.timeout) as provider:
        records = await run_smoke_tests(provider, ledger, candidates, args.image, args.output)
    failed = [alias for alias, record in records.items() if not record.schema_valid]
    if failed:
        print(f"Smoke failed; do not run the benchmark: {', '.join(failed)}")
        return 2
    print(f"Smoke passed for {len(records)} candidates; estimated spend ${ledger.spent_usd}")
    return 0


async def _run(args: argparse.Namespace) -> int:
    _require_current_terms(args)
    public_items = load_manifest(args.public_manifest, args.public_images)
    private_items = load_manifest(args.private_manifest, args.private_images)
    validate_public_manifest(public_items)
    validate_private_manifest(private_items)
    ledger = BudgetLedger(cap_usd=args.budget)
    async with HuggingFaceProvider(_live_token(), timeout_seconds=args.timeout) as provider:
        winner, _ = await run_full_benchmark(
            provider,
            ledger,
            get_candidates(args.models),
            public_items,
            args.public_images,
            private_items,
            args.private_images,
            args.output,
        )
    if winner is None:
        print("No Apache-2.0 candidate passed. Product implementation remains blocked.")
        return 3
    print(f"Selected candidate alias: {winner}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare-public":
            manifest = prepare_public_dataset(args.output, per_class=args.per_class)
            print(f"Prepared public diagnostic manifest: {manifest}")
            return 0
        if args.command == "validate-private":
            items = load_manifest(args.manifest, args.images)
            validate_private_manifest(items)
            print(f"Private manifest is valid: {len(items)} images")
            return 0
        if args.command == "smoke":
            return asyncio.run(_smoke(args))
        if args.command == "run":
            return asyncio.run(_run(args))
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {safe_error(error)}", file=sys.stderr)
        return 1
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
