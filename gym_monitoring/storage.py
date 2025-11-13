from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional
import sqlite3

from .utils import add_months

APP_DIR = Path.home() / ".local" / "share" / "gym-monitoring"
DEFAULT_DB_PATH = APP_DIR / "gym.db"
MAX_MEMBERS = 5000


@dataclass
class Member:
    id: int
    name: str
    phone: Optional[str]
    admission_date: date
    plan_months: int
    fee_amount: float
    next_due_date: date
    created_at: datetime


@dataclass
class Payment:
    id: int
    member_id: int
    amount: float
    paid_on: date
    recorded_at: datetime


class Storage:
    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def __enter__(self) -> "Storage":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _init_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                admission_date TEXT NOT NULL,
                plan_months INTEGER NOT NULL,
                fee_amount REAL NOT NULL,
                next_due_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                amount REAL NOT NULL,
                paid_on TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    def add_member(
        self,
        name: str,
        phone: Optional[str],
        admission_date: date,
        plan_months: int,
        fee_amount: float,
    ) -> Member:
        if self.count_members() >= MAX_MEMBERS:
            raise RuntimeError(f"Member limit of {MAX_MEMBERS} has been reached.")
        next_due = add_months(admission_date, plan_months)
        now = datetime.utcnow()
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO members (name, phone, admission_date, plan_months, fee_amount, next_due_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                phone,
                admission_date.isoformat(),
                plan_months,
                fee_amount,
                next_due.isoformat(),
                now.isoformat(),
            ),
        )
        member_id = cur.lastrowid
        self._conn.commit()
        return self.get_member(member_id)

    def get_member(self, member_id: int) -> Member:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Member {member_id} not found")
        return self._row_to_member(row)

    def list_members(self) -> Iterable[Member]:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM members ORDER BY created_at DESC")
        for row in cur.fetchall():
            yield self._row_to_member(row)

    def count_members(self) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM members")
        (count,) = cur.fetchone()
        return int(count)

    def record_payment(self, member_id: int, amount: float, paid_on: date) -> Payment:
        member = self.get_member(member_id)
        next_due = add_months(member.next_due_date, member.plan_months)
        now = datetime.utcnow()
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO payments (member_id, amount, paid_on, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                member_id,
                amount,
                paid_on.isoformat(),
                now.isoformat(),
            ),
        )
        cur.execute(
            "UPDATE members SET next_due_date = ? WHERE id = ?",
            (next_due.isoformat(), member_id),
        )
        self._conn.commit()
        payment_id = cur.lastrowid
        return self.get_payment(payment_id)

    def list_payments(self, member_id: Optional[int] = None) -> Iterable[Payment]:
        cur = self._conn.cursor()
        if member_id is not None:
            cur.execute("SELECT * FROM payments WHERE member_id = ? ORDER BY paid_on DESC", (member_id,))
        else:
            cur.execute("SELECT * FROM payments ORDER BY paid_on DESC")
        for row in cur.fetchall():
            yield self._row_to_payment(row)

    def get_payment(self, payment_id: int) -> Payment:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"Payment {payment_id} not found")
        return self._row_to_payment(row)

    def export_members_csv(self, output_path: Path) -> None:
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM members ORDER BY id")
        rows = cur.fetchall()
        if not rows:
            output_path.write_text("id,name,phone,admission_date,plan_months,fee_amount,next_due_date,created_at\n")
            return
        with output_path.open("w", encoding="utf-8") as handle:
            handle.write("id,name,phone,admission_date,plan_months,fee_amount,next_due_date,created_at\n")
            for row in rows:
                handle.write(
                    ",".join(
                        [
                            str(row["id"]),
                            row["name"],
                            row["phone"] or "",
                            row["admission_date"],
                            str(row["plan_months"]),
                            f"{row['fee_amount']:.2f}",
                            row["next_due_date"],
                            row["created_at"],
                        ]
                    )
                    + "\n"
                )

    def close(self) -> None:
        self._conn.close()

    def _row_to_member(self, row: sqlite3.Row) -> Member:
        return Member(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
            admission_date=date.fromisoformat(row["admission_date"]),
            plan_months=row["plan_months"],
            fee_amount=row["fee_amount"],
            next_due_date=date.fromisoformat(row["next_due_date"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _row_to_payment(self, row: sqlite3.Row) -> Payment:
        return Payment(
            id=row["id"],
            member_id=row["member_id"],
            amount=row["amount"],
            paid_on=date.fromisoformat(row["paid_on"]),
            recorded_at=datetime.fromisoformat(row["recorded_at"]),
        )


__all__ = ["Storage", "Member", "Payment", "DEFAULT_DB_PATH", "MAX_MEMBERS"]
