# Data Generation

`generate_data.py` deterministically generates the full synthetic dataset
(seed = 42) and loads it into your local MySQL install.

## Reference date

The dataset spans **2024-01-01 to 2025-12-31** (24 months). Treat
**2025-12-31** as "today" for any recency-based question (last 90 days,
last quarter, etc.) — the data does not move forward with real time, so
training questions and solutions must anchor to this fixed date rather
than `CURDATE()`/`NOW()`.

## Design choices worth knowing

- **Hidden behavioral archetypes**: customers, products, stores and
  campaigns each have a hidden "quality" parameter (spend level, order
  frequency, popularity, performance, effectiveness) that drives realistic,
  skewed generation. These are *not* stored as columns — the learner has
  to discover VIPs, best-sellers, dormant customers, etc. via SQL (RFM,
  ranking, recency), not by reading a label off a row. `customer_segment`
  is a separate, independent marketing tier field and intentionally does
  **not** correlate perfectly with actual purchasing behavior — real
  loyalty-tier programs don't either.
- **Inventory grain**: daily, but each store only stocks a random
  assortment of ~50-100 products (not the full 1,200-product catalog) to
  keep the ledger a manageable ~1.5-2M rows instead of ~30M+.
- **Never-sold products**: ~5% of products are excluded from every store's
  assortment and every order — these support "products with zero sales"
  questions.
- **Zero-order customers**: driven by the `zero` archetype (~4% of
  customers), for anti-join / "never purchased" questions.
- **Dormant customers**: ~15% of `occasional`/`regular` customers have
  their order history deliberately truncated 90-400 days before the
  dataset end, for reactivation/recency questions.

## Usage

```bash
cd data_generation
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# with the sql_gym database + gym_user already created (see
# scripts/bootstrap_local_mysql.sh) and schema applied:
python generate_data.py

# or just produce CSVs without touching the database:
python generate_data.py --csv-only
```

Connection settings come from environment variables (see `.env.example`
at the repo root): `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`,
`MYSQL_PASSWORD`, `MYSQL_DATABASE`.

Re-running the script truncates and regenerates every table, so it is
safe to run repeatedly — the seed guarantees the same dataset each time.
