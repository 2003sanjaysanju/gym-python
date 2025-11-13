from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

from tabulate import tabulate

from .storage import DEFAULT_DB_PATH, MAX_MEMBERS, Member, Payment, Storage

DATE_FMT = "%Y-%m-%d"


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gym membership monitoring tool")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH, help="Path to SQLite database")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_member = subparsers.add_parser("add-member", help="Create a new gym member")
    add_member.add_argument("--name", required=True)
    add_member.add_argument("--phone")
    add_member.add_argument("--admission-date", default=date.today().isoformat(), help=f"defaults to today ({DATE_FMT})")
    add_member.add_argument("--plan-months", type=int, default=1, help="Billing cycle in months")
    add_member.add_argument("--fee-amount", type=float, required=True)

    list_members = subparsers.add_parser("list-members", help="List member roster")
    list_members.add_argument("--overdue-only", action="store_true", help="Show only members with overdue fees")

    record_payment = subparsers.add_parser("record-payment", help="Record a fee payment")
    record_payment.add_argument("--member-id", type=int, required=True)
    record_payment.add_argument("--amount", type=float, required=True)
    record_payment.add_argument("--paid-on", default=date.today().isoformat(), help=f"Payment date (default today {DATE_FMT})")

    list_payments = subparsers.add_parser("list-payments", help="List payment history")
    list_payments.add_argument("--member-id", type=int)

    export = subparsers.add_parser("export", help="Export members to CSV")
    export.add_argument("--output", type=Path, required=True)

    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    with Storage(args.db) as storage:
        if args.command == "add-member":
            try:
                member = storage.add_member(
                    name=args.name,
                    phone=args.phone,
                    admission_date=_parse_date(args.admission_date),
                    plan_months=args.plan_months,
                    fee_amount=args.fee_amount,
                )
            except RuntimeError as exc:
                print(f"Error: {exc}")
                print(f"The system supports up to {MAX_MEMBERS} members. Consider exporting or archiving old records.")
                return
            print(f"Created member #{member.id}: {member.name}")
        elif args.command == "list-members":
            members = list(storage.list_members())
            if args.overdue_only:
                today = date.today()
                members = [m for m in members if m.next_due_date < today]
            if not members:
                print("No members found.")
                return
            _render_members(members)
        elif args.command == "record-payment":
            payment = storage.record_payment(
                member_id=args.member_id,
                amount=args.amount,
                paid_on=_parse_date(args.paid_on),
            )
            member = storage.get_member(payment.member_id)
            print(
                f"Recorded payment #{payment.id} for member #{payment.member_id}. Next due date: {member.next_due_date.isoformat()}"
            )
        elif args.command == "list-payments":
            payments = list(storage.list_payments(member_id=args.member_id))
            if not payments:
                print("No payments found.")
                return
            _render_payments(payments)
        elif args.command == "export":
            storage.export_members_csv(args.output)
            print(f"Exported members to {args.output}")


def _render_members(members: list[Member]) -> None:
    today = date.today()
    rows = []
    for m in members:
        status = "OK"
        if m.next_due_date < today:
            status = "OVERDUE"
        elif (m.next_due_date - today).days <= 3:
            status = "DUE SOON"
        rows.append(
            [
                m.id,
                m.name,
                m.phone or "-",
                m.admission_date.isoformat(),
                m.plan_months,
                f"{m.fee_amount:.2f}",
                m.next_due_date.isoformat(),
                status,
            ]
        )
    table = tabulate(
        rows,
        headers=["ID", "Name", "Phone", "Admission", "Cycle (months)", "Fee", "Next Due", "Status"],
        tablefmt="github",
    )
    print(table)


def _render_payments(payments: list[Payment]) -> None:
    rows = []
    for p in payments:
        rows.append([
            p.id,
            p.member_id,
            f"{p.amount:.2f}",
            p.paid_on.isoformat(),
            p.recorded_at.strftime("%Y-%m-%d %H:%M"),
        ])
    print(
        tabulate(
            rows,
            headers=["ID", "Member", "Amount", "Paid On", "Recorded"],
            tablefmt="github",
        )
    )


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid date '{value}'. Expect format {DATE_FMT}.") from exc


if __name__ == "__main__":
    main()
