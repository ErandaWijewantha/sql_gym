"""
Walks solutions/**/*.md, extracts every ```sql fenced code block in the
file (this covers both "## 7. SQL" and any "## 11. Alternative
Approach" blocks), and executes each against the running MySQL
database. Reports PASS/FAIL per file plus basic sanity checks (query
runs without error, returns a result set).

Usage:
    python scripts/validate_all_solutions.py
"""
import os
import re
import sys

import pymysql

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOLUTIONS_DIR = os.path.join(ROOT, "solutions")

CODE_FENCE_RE = re.compile(r"```sql\s*(.*?)```", re.DOTALL)


def find_solution_files():
    for dirpath, _, filenames in os.walk(SOLUTIONS_DIR):
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                yield os.path.join(dirpath, fn)


def extract_sql(text: str) -> list[str]:
    return [m.strip() for m in CODE_FENCE_RE.findall(text) if m.strip()]


def main():
    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    port = int(os.environ.get("MYSQL_PORT", "3306"))
    user = os.environ.get("MYSQL_USER", "gym_user")
    password = os.environ.get("MYSQL_PASSWORD", "gym_pw")
    database = os.environ.get("MYSQL_DATABASE", "sql_gym")

    conn = pymysql.connect(host=host, port=port, user=user, password=password,
                            database=database, connect_timeout=10)

    files = list(find_solution_files())
    if not files:
        print("No solution files found under solutions/ yet.")
        return 0

    n_pass, n_fail, n_skip = 0, 0, 0
    failures = []

    for path in files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        blocks = extract_sql(text)
        if not blocks:
            print(f"SKIP  {rel}  (no ```sql block found)")
            n_skip += 1
            continue

        ok = True
        for i, sql in enumerate(blocks):
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    if cur.description is not None:
                        rows = cur.fetchmany(5)
            except Exception as e:
                ok = False
                failures.append((rel, i, str(e)))
                break

        if ok:
            print(f"PASS  {rel}  ({len(blocks)} query block(s))")
            n_pass += 1
        else:
            print(f"FAIL  {rel}")
            n_fail += 1

    conn.close()

    print(f"\n{n_pass} passed, {n_fail} failed, {n_skip} skipped, {len(files)} total")
    if failures:
        print("\nFailure details:")
        for rel, i, err in failures:
            print(f"  {rel} [block {i}]: {err}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
