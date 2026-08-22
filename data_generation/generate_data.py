"""
generate_data.py
=================

Deterministic synthetic data generator for the SQL Analytical
Thinking Gym (see CLAUDE.md for the full design brief).

Design goals:
  - Deterministic: fixed random seed -> same dataset every run.
  - Realistic, not uniform: customers/products/stores/campaigns
    have hidden "archetypes" that drive skewed, correlated
    behavior (best-sellers, VIPs, dormant customers, seasonal
    categories, high/low performing stores, effective/ineffective
    campaigns) without those archetypes being stored as columns
    the learner could just SELECT to "cheat" the analysis.
  - Deliberately includes edge cases called out in CLAUDE.md:
    zero-order customers, one-time customers, never-sold products,
    cancelled orders, failed payments, partial/full returns,
    stockouts, NULL customer demographics, ambiguous "revenue".

Reference date for the whole dataset (used by any question that
needs a fixed "today"): 2025-12-31. Do NOT use CURDATE()/NOW() in
training questions/solutions -- always anchor to this date, since
the data does not move forward with real time.

Usage:
    python generate_data.py            # generate + load into MySQL
    python generate_data.py --csv-only # only write CSVs to output/

Connection settings are read from environment variables (see
.env.example / README.md): MYSQL_HOST, MYSQL_PORT, MYSQL_USER,
MYSQL_PASSWORD, MYSQL_DATABASE.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

SEED = 42
RNG = np.random.default_rng(SEED)
fake = Faker()
Faker.seed(SEED)

DATASET_START = date(2024, 1, 1)
DATASET_END = date(2025, 12, 31)   # "as of" reference date -- 24 months
TOTAL_DAYS = (DATASET_END - DATASET_START).days + 1

N_CATEGORIES = 24
N_BRANDS = 60
N_PRODUCTS = 1200
N_STORES = 35
N_EMPLOYEES = 350
N_CUSTOMERS = 12000
N_CAMPAIGNS = 40

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

REGIONS = [
    "Western", "Central", "Southern", "Northern", "Eastern",
    "North Western", "North Central", "Uva", "Sabaragamuwa",
]

REGION_CITIES = {
    "Western": ["Colombo", "Gampaha", "Negombo", "Kalutara"],
    "Central": ["Kandy", "Matale", "Nuwara Eliya"],
    "Southern": ["Galle", "Matara", "Hambantota"],
    "Northern": ["Jaffna", "Vavuniya", "Kilinochchi"],
    "Eastern": ["Batticaloa", "Trincomalee", "Ampara"],
    "North Western": ["Kurunegala", "Puttalam"],
    "North Central": ["Anuradhapura", "Polonnaruwa"],
    "Uva": ["Badulla", "Monaragala"],
    "Sabaragamuwa": ["Ratnapura", "Kegalle"],
}

CATEGORY_NAMES = [
    "Mobile Phones", "Laptops & Computers", "Home Appliances", "Kitchenware",
    "Furniture", "Men's Apparel", "Women's Apparel", "Kids' Apparel",
    "Footwear", "Beauty & Cosmetics", "Personal Care", "Groceries",
    "Beverages", "Sports & Fitness", "Toys & Games", "Books & Stationery",
    "Automotive Accessories", "Pet Supplies", "Home Decor", "Garden & Outdoor",
    "Jewelry & Watches", "Luggage & Bags", "Health & Wellness", "Electronics Accessories",
]
assert len(CATEGORY_NAMES) == N_CATEGORIES

# Seasonality "shape" assigned per category: monthly multiplier, Jan..Dec
SEASONALITY_SHAPES = {
    "flat": [1.0] * 12,
    "holiday_peak": [0.8, 0.7, 0.8, 0.8, 0.9, 0.9, 0.9, 1.0, 1.1, 1.3, 1.8, 2.2],
    "summer_peak": [0.7, 0.7, 0.9, 1.1, 1.3, 1.6, 1.7, 1.4, 1.0, 0.8, 0.7, 0.7],
    "new_year_peak": [1.8, 1.4, 1.1, 0.9, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 1.0, 1.3],
    "back_to_school": [0.8, 0.8, 0.8, 0.8, 0.9, 1.0, 1.2, 1.8, 1.5, 0.9, 0.8, 0.9],
    "wedding_season": [0.9, 1.0, 1.1, 1.3, 1.5, 1.4, 1.0, 0.9, 0.9, 1.0, 1.2, 1.4],
}
CATEGORY_SEASONALITY_ASSIGNMENT = {
    "Mobile Phones": "holiday_peak", "Laptops & Computers": "back_to_school",
    "Home Appliances": "wedding_season", "Kitchenware": "wedding_season",
    "Furniture": "flat", "Men's Apparel": "new_year_peak",
    "Women's Apparel": "new_year_peak", "Kids' Apparel": "back_to_school",
    "Footwear": "back_to_school", "Beauty & Cosmetics": "wedding_season",
    "Personal Care": "flat", "Groceries": "flat",
    "Beverages": "summer_peak", "Sports & Fitness": "new_year_peak",
    "Toys & Games": "holiday_peak", "Books & Stationery": "back_to_school",
    "Automotive Accessories": "flat", "Pet Supplies": "flat",
    "Home Decor": "holiday_peak", "Garden & Outdoor": "summer_peak",
    "Jewelry & Watches": "wedding_season", "Luggage & Bags": "summer_peak",
    "Health & Wellness": "new_year_peak", "Electronics Accessories": "holiday_peak",
}

ACQUISITION_CHANNELS = [
    "Organic Search", "Paid Search", "Social Media", "Referral",
    "Email Campaign", "In-Store Walk-in", "Affiliate", "Marketplace",
]
CUSTOMER_SEGMENTS = ["Premium", "Standard", "Budget", "Corporate"]
CUSTOMER_SEGMENT_WEIGHTS = [0.12, 0.55, 0.25, 0.08]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "Mobile Wallet", "Bank Transfer", "Gift Card"]
EMPLOYEE_ROLES = ["Sales Associate", "Cashier", "Store Manager", "Assistant Manager", "Stock Clerk"]
RETURN_REASONS = ["Defective", "Wrong Item Delivered", "Size/Fit Issue", "No Longer Needed",
                   "Late Delivery", "Found Cheaper Elsewhere", "Other"]
TICKET_ISSUE_TYPES = ["Delivery Delay", "Product Defect", "Billing Issue", "Return/Refund Status",
                       "Account Access", "Order Cancellation Request", "Product Inquiry", "Warranty Claim"]
CAMPAIGN_CHANNELS = ["Email", "Social Media", "Search Ads", "Display Ads", "Influencer", "Affiliate", "SMS"]

# Customer behavioral archetypes -- NOT stored as a column, only used
# to drive order generation, so learners must discover behavior via
# recency/frequency/monetary analysis rather than reading a label.
ARCHETYPES = ["zero", "one_time", "occasional", "regular", "vip"]
ARCHETYPE_WEIGHTS = [0.04, 0.28, 0.33, 0.25, 0.10]
ARCHETYPE_ORDER_RANGE = {
    "zero": (0, 0), "one_time": (1, 1), "occasional": (2, 7),
    "regular": (7, 22), "vip": (22, 70),
}


def month_index(d: date) -> int:
    return d.month - 1


def random_dates_between(start: date, end: date, n: int, rng: np.random.Generator) -> list[date]:
    span = (end - start).days
    if span <= 0:
        return [start] * n
    offsets = rng.integers(0, span + 1, size=n)
    return [start + timedelta(days=int(o)) for o in offsets]


# ------------------------------------------------------------------
# Dimension generators
# ------------------------------------------------------------------

def gen_categories() -> pd.DataFrame:
    return pd.DataFrame({
        "category_id": np.arange(1, N_CATEGORIES + 1),
        "category_name": CATEGORY_NAMES,
    })


def gen_brands() -> pd.DataFrame:
    names = set()
    while len(names) < N_BRANDS:
        names.add(fake.company().replace(",", "").replace(".", ""))
    names = sorted(names)[:N_BRANDS]
    return pd.DataFrame({
        "brand_id": np.arange(1, N_BRANDS + 1),
        "brand_name": names,
    })


def gen_products(categories: pd.DataFrame, brands: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    category_ids = RNG.choice(categories["category_id"], size=N_PRODUCTS)
    brand_ids = RNG.choice(brands["brand_id"], size=N_PRODUCTS)

    # Category-level base price bands (LKR) so e.g. Jewelry costs more than Groceries
    price_bands = {
        "Mobile Phones": (15000, 350000), "Laptops & Computers": (60000, 500000),
        "Home Appliances": (8000, 250000), "Kitchenware": (500, 25000),
        "Furniture": (5000, 300000), "Men's Apparel": (800, 15000),
        "Women's Apparel": (800, 18000), "Kids' Apparel": (500, 8000),
        "Footwear": (1200, 20000), "Beauty & Cosmetics": (400, 12000),
        "Personal Care": (200, 5000), "Groceries": (100, 4000),
        "Beverages": (100, 3000), "Sports & Fitness": (800, 60000),
        "Toys & Games": (500, 15000), "Books & Stationery": (150, 5000),
        "Automotive Accessories": (500, 45000), "Pet Supplies": (300, 10000),
        "Home Decor": (500, 25000), "Garden & Outdoor": (500, 40000),
        "Jewelry & Watches": (2000, 400000), "Luggage & Bags": (1500, 35000),
        "Health & Wellness": (300, 15000), "Electronics Accessories": (300, 20000),
    }
    cat_name_by_id = dict(zip(categories["category_id"], categories["category_name"]))

    selling_prices = np.empty(N_PRODUCTS)
    for i, cid in enumerate(category_ids):
        lo, hi = price_bands[cat_name_by_id[cid]]
        # log-uniform within the band for realistic price spread
        selling_prices[i] = np.exp(RNG.uniform(np.log(lo), np.log(hi)))
    selling_prices = np.round(selling_prices, -1)  # round to nearest 10 LKR

    margins = RNG.uniform(0.18, 0.45, size=N_PRODUCTS)
    costs = np.round(selling_prices * (1 - margins), 2)

    launch_dates = random_dates_between(date(2020, 1, 1), date(2025, 11, 1), N_PRODUCTS, RNG)

    # ~4% discontinued, biased toward older launches
    launch_age_days = np.array([(DATASET_END - d).days for d in launch_dates])
    discontinue_prob = np.clip(launch_age_days / 3000, 0, 0.5) * 0.15
    status = np.where(RNG.random(N_PRODUCTS) < discontinue_prob, "discontinued", "active")

    model_words = [fake.word().capitalize() for _ in range(N_PRODUCTS)]
    brand_name_by_id = dict(zip(brands["brand_id"], brands["brand_name"]))
    product_names = [
        f"{brand_name_by_id[brand_ids[i]]} {cat_name_by_id[category_ids[i]].split(' ')[0]} {model_words[i]} {i+1}"
        for i in range(N_PRODUCTS)
    ]

    # Zipf-like popularity weight used only for sampling in order_items,
    # never stored. ~5% of products are deliberately excluded (never sold).
    ranks = RNG.permutation(N_PRODUCTS) + 1
    popularity = 1.0 / (ranks ** 0.9)
    never_sold_mask = RNG.random(N_PRODUCTS) < 0.05
    popularity[never_sold_mask] = 0.0

    df = pd.DataFrame({
        "product_id": np.arange(1, N_PRODUCTS + 1),
        "product_name": product_names,
        "category_id": category_ids,
        "brand_id": brand_ids,
        "cost": costs,
        "selling_price": selling_prices,
        "launch_date": launch_dates,
        "status": status,
    })
    return df, popularity, category_ids


def gen_stores() -> tuple[pd.DataFrame, np.ndarray]:
    store_types = []
    regions = []
    cities = []
    names = []

    n_online = 2
    n_flagship = 5
    n_outlet = 8
    n_standard = N_STORES - n_online - n_flagship - n_outlet

    plan = (["online"] * n_online + ["flagship"] * n_flagship +
            ["outlet"] * n_outlet + ["standard"] * n_standard)
    RNG.shuffle(plan)

    for st in plan:
        if st == "online":
            region = "Western"
            city = "Colombo"
            name = f"Online Store - {fake.word().capitalize()}"
        else:
            region = RNG.choice(REGIONS)
            city = RNG.choice(REGION_CITIES[region])
            name = f"{city} {st.capitalize()} Store"
        store_types.append(st)
        regions.append(region)
        cities.append(city)
        names.append(name)

    # Hidden performance multiplier: some stores are strong, some weak
    performance = RNG.lognormal(mean=0.0, sigma=0.45, size=N_STORES)
    performance[np.array(store_types) == "online"] *= 2.5   # online moves more volume
    performance[np.array(store_types) == "flagship"] *= 1.6

    df = pd.DataFrame({
        "store_id": np.arange(1, N_STORES + 1),
        "store_name": names,
        "city": cities,
        "region": regions,
        "store_type": store_types,
    })
    return df, performance


def gen_employees(stores: pd.DataFrame) -> pd.DataFrame:
    # More employees at flagship/standard stores, few at outlets, a small
    # ops team for online stores
    weights = stores["store_type"].map({
        "flagship": 4.0, "standard": 2.0, "outlet": 1.0, "online": 1.5,
    }).to_numpy()
    weights = weights / weights.sum()
    store_ids = RNG.choice(stores["store_id"], size=N_EMPLOYEES, p=weights)
    roles = RNG.choice(EMPLOYEE_ROLES, size=N_EMPLOYEES, p=[0.45, 0.20, 0.10, 0.10, 0.15])
    hire_dates = random_dates_between(date(2016, 1, 1), date(2025, 11, 1), N_EMPLOYEES, RNG)
    return pd.DataFrame({
        "employee_id": np.arange(1, N_EMPLOYEES + 1),
        "store_id": store_ids,
        "employee_role": roles,
        "hire_date": hire_dates,
    })


def gen_customers() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    genders = RNG.choice(["M", "F", "Other", None], size=N_CUSTOMERS, p=[0.47, 0.47, 0.02, 0.04])
    dobs = random_dates_between(date(1955, 1, 1), date(2007, 12, 31), N_CUSTOMERS, RNG)
    dobs = [d if RNG.random() > 0.03 else None for d in dobs]  # ~3% missing DOB

    # Registration spans well before the dataset window too, so some
    # customers are "pre-existing" and some are newly acquired mid-window
    reg_dates = random_dates_between(date(2021, 1, 1), DATASET_END, N_CUSTOMERS, RNG)

    regions = RNG.choice(REGIONS, size=N_CUSTOMERS, p=[0.32, 0.14, 0.12, 0.07, 0.08, 0.08, 0.06, 0.06, 0.07])
    cities = [RNG.choice(REGION_CITIES[r]) for r in regions]
    # ~2% missing city/region (NULL demographic edge case)
    missing_geo = RNG.random(N_CUSTOMERS) < 0.02
    cities = [c if not m else None for c, m in zip(cities, missing_geo)]
    regions_out = [r if not m else None for r, m in zip(regions, missing_geo)]

    segments = RNG.choice(CUSTOMER_SEGMENTS, size=N_CUSTOMERS, p=CUSTOMER_SEGMENT_WEIGHTS)
    channels = RNG.choice(ACQUISITION_CHANNELS, size=N_CUSTOMERS)
    missing_channel = RNG.random(N_CUSTOMERS) < 0.03
    channels = [c if not m else None for c, m in zip(channels, missing_channel)]

    names = [fake.name() for _ in range(N_CUSTOMERS)]

    df = pd.DataFrame({
        "customer_id": np.arange(1, N_CUSTOMERS + 1),
        "customer_name": names,
        "gender": genders,
        "date_of_birth": dobs,
        "registration_date": reg_dates,
        "city": cities,
        "region": regions_out,
        "customer_segment": segments,
        "acquisition_channel": channels,
    })

    archetypes = RNG.choice(ARCHETYPES, size=N_CUSTOMERS, p=ARCHETYPE_WEIGHTS)
    # Hidden per-customer spend multiplier (independent of frequency)
    spend_multiplier = RNG.lognormal(mean=0.0, sigma=0.5, size=N_CUSTOMERS)
    return df, archetypes, spend_multiplier


# ------------------------------------------------------------------
# Fact generators
# ------------------------------------------------------------------

def gen_orders(customers: pd.DataFrame, archetypes: np.ndarray,
               stores: pd.DataFrame, store_performance: np.ndarray) -> pd.DataFrame:
    reg_dates = pd.to_datetime(customers["registration_date"]).dt.date.to_numpy()
    regions = customers["region"].to_numpy()

    physical_mask = (stores["store_type"] != "online").to_numpy()
    online_mask = ~physical_mask
    physical_store_ids = stores.loc[physical_mask, "store_id"].to_numpy()
    physical_weights = store_performance[physical_mask]
    physical_weights = physical_weights / physical_weights.sum()
    online_store_ids = stores.loc[online_mask, "store_id"].to_numpy()
    online_weights = store_performance[online_mask]
    online_weights = online_weights / online_weights.sum()
    store_region = dict(zip(stores["store_id"], stores["region"]))

    rows = []
    order_id = 1

    # ~15% of occasional/regular customers become "dormant": their last
    # order is well before DATASET_END even though they aren't one-time
    dormant_eligible = np.isin(archetypes, ["occasional", "regular"])
    dormant_flag = dormant_eligible & (RNG.random(len(archetypes)) < 0.15)

    for idx in range(N_CUSTOMERS):
        arch = archetypes[idx]
        lo, hi = ARCHETYPE_ORDER_RANGE[arch]
        if hi == 0:
            continue
        n_orders = int(RNG.integers(lo, hi + 1))
        if n_orders == 0:
            continue

        window_start = max(reg_dates[idx], DATASET_START)
        window_end = DATASET_END
        if dormant_flag[idx]:
            cutoff = RNG.integers(90, 400)
            candidate_end = DATASET_END - timedelta(days=int(cutoff))
            if candidate_end > window_start:
                window_end = candidate_end

        if window_start >= window_end:
            window_start, window_end = DATASET_START, DATASET_END

        order_dates = random_dates_between(window_start, window_end, n_orders, RNG)
        order_dates.sort()

        cust_region = regions[idx]
        for od in order_dates:
            is_online = RNG.random() < 0.25
            if is_online:
                store_id = RNG.choice(online_store_ids, p=online_weights)
                hour = int(RNG.integers(0, 24))
            else:
                if cust_region is not None and RNG.random() < 0.8:
                    same_region = [sid for sid in physical_store_ids if store_region[sid] == cust_region]
                else:
                    same_region = []
                if same_region:
                    store_id = RNG.choice(same_region)
                else:
                    store_id = RNG.choice(physical_store_ids, p=physical_weights)
                hour = int(RNG.integers(9, 21))

            minute = int(RNG.integers(0, 60))
            order_dt = datetime.combine(od, datetime.min.time()) + timedelta(hours=hour, minutes=minute)

            days_from_end = (DATASET_END - od).days
            if days_from_end <= 14:
                status = RNG.choice(
                    ["completed", "cancelled", "pending", "refunded"],
                    p=[0.70, 0.08, 0.18, 0.04],
                )
            else:
                status = RNG.choice(
                    ["completed", "cancelled", "pending", "refunded"],
                    p=[0.90, 0.055, 0.005, 0.04],
                )

            rows.append((
                order_id, customers["customer_id"].iat[idx], int(store_id),
                order_dt, status, "online" if is_online else "in_store",
                RNG.choice(PAYMENT_METHODS),
            ))
            order_id += 1

    df = pd.DataFrame(rows, columns=[
        "order_id", "customer_id", "store_id", "order_date",
        "order_status", "sales_channel", "payment_method",
    ])
    return df


def gen_order_items(orders: pd.DataFrame, products: pd.DataFrame, popularity: np.ndarray) -> pd.DataFrame:
    n_orders = len(orders)
    item_counts = RNG.choice([1, 2, 3, 4, 5, 6, 7, 8], size=n_orders,
                              p=[.25, .25, .20, .13, .08, .05, .03, .01])
    total_items = int(item_counts.sum())

    order_id_repeated = np.repeat(orders["order_id"].to_numpy(), item_counts)

    prob = popularity / popularity.sum()
    product_choice_idx = RNG.choice(len(products), size=total_items, p=prob)
    chosen_products = products.iloc[product_choice_idx].reset_index(drop=True)

    quantities = RNG.choice([1, 2, 3, 4, 5], size=total_items, p=[.55, .25, .12, .05, .03])

    unit_prices = chosen_products["selling_price"].to_numpy()

    has_discount = RNG.random(total_items) < 0.30
    discount_pct = np.where(has_discount, RNG.uniform(0.05, 0.35, size=total_items), 0.0)
    discount_amount = np.round(unit_prices * quantities * discount_pct, 2)

    df = pd.DataFrame({
        "order_id": order_id_repeated,
        "product_id": chosen_products["product_id"].to_numpy(),
        "quantity": quantities,
        "unit_price": unit_prices,
        "discount_amount": discount_amount,
    })
    df.insert(0, "order_item_id", np.arange(1, len(df) + 1))
    return df


def gen_payments(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    order_totals = (
        order_items.assign(line_total=order_items["quantity"] * order_items["unit_price"] - order_items["discount_amount"])
        .groupby("order_id")["line_total"].sum()
    )

    rows = []
    payment_id = 1
    for o in orders.itertuples(index=False):
        total = float(order_totals.get(o.order_id, 0.0))
        pay_dt = o.order_date + timedelta(hours=int(RNG.integers(0, 6)), minutes=int(RNG.integers(0, 60)))

        if o.order_status == "completed":
            if RNG.random() < 0.05:
                # a failed attempt followed by a successful retry
                rows.append((payment_id, o.order_id, pay_dt, total, "failed", o.payment_method))
                payment_id += 1
                pay_dt2 = pay_dt + timedelta(minutes=int(RNG.integers(5, 120)))
                rows.append((payment_id, o.order_id, pay_dt2, total, "success", o.payment_method))
                payment_id += 1
            else:
                rows.append((payment_id, o.order_id, pay_dt, total, "success", o.payment_method))
                payment_id += 1
        elif o.order_status == "cancelled":
            status = RNG.choice(["failed", "success"], p=[0.7, 0.3])
            rows.append((payment_id, o.order_id, pay_dt, total, status, o.payment_method))
            payment_id += 1
        elif o.order_status == "pending":
            rows.append((payment_id, o.order_id, pay_dt, total, "pending", o.payment_method))
            payment_id += 1
        else:  # refunded
            rows.append((payment_id, o.order_id, pay_dt, total, "refunded", o.payment_method))
            payment_id += 1

    return pd.DataFrame(rows, columns=[
        "payment_id", "order_id", "payment_date", "amount", "payment_status", "payment_method",
    ])


def gen_returns(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    order_status_by_id = dict(zip(orders["order_id"], orders["order_status"]))
    order_date_by_id = dict(zip(orders["order_id"], orders["order_date"]))

    eligible = order_items[order_items["order_id"].map(order_status_by_id).isin(["completed", "refunded"])]
    # ~4.5% of eligible line items get returned (partially or fully)
    sample = eligible.sample(frac=0.045, random_state=SEED)

    rows = []
    return_id = 1
    for r in sample.itertuples(index=False):
        order_dt = order_date_by_id[r.order_id]
        max_gap = min(45, (DATASET_END - order_dt.date()).days)
        if max_gap <= 0:
            continue
        gap = int(RNG.integers(1, max_gap + 1))
        return_date = order_dt.date() + timedelta(days=gap)
        return_qty = r.quantity if RNG.random() < 0.6 else int(RNG.integers(1, r.quantity + 1))
        reason = RNG.choice(RETURN_REASONS)
        rows.append((return_id, r.order_id, r.product_id, return_date, return_qty, reason))
        return_id += 1

    return pd.DataFrame(rows, columns=[
        "return_id", "order_id", "product_id", "return_date", "quantity", "return_reason",
    ])


def gen_inventory(stores: pd.DataFrame, products: pd.DataFrame, popularity: np.ndarray,
                   store_performance: np.ndarray, category_ids: np.ndarray) -> pd.DataFrame:
    """
    Daily store-product inventory ledger, but each store only carries a
    random assortment of products (not the full catalog), and never-sold
    products (popularity == 0) are excluded from every store's assortment.
    This keeps volume manageable while preserving realistic stockouts.
    """
    sellable_idx = np.where(popularity > 0)[0]
    cat_name_by_id = dict(zip(range(1, N_CATEGORIES + 1), CATEGORY_NAMES))

    pairs_store = []
    pairs_product = []
    for s_idx, store_id in enumerate(stores["store_id"]):
        assortment_size = int(RNG.integers(50, 100))
        chosen = RNG.choice(sellable_idx, size=assortment_size, replace=False)
        pairs_store.extend([store_id] * assortment_size)
        pairs_product.extend(products["product_id"].to_numpy()[chosen])

    pairs_store = np.array(pairs_store)
    pairs_product = np.array(pairs_product)
    n_pairs = len(pairs_store)

    perf_by_store = dict(zip(stores["store_id"], store_performance))
    pop_by_product = dict(zip(products["product_id"], popularity))
    cat_by_product = dict(zip(products["product_id"], products["category_id"]))

    base_demand = np.array([
        pop_by_product[p] * perf_by_store[s] * 400 for p, s in zip(pairs_product, pairs_store)
    ])
    seasonality_shape_by_cat = {
        cid: SEASONALITY_SHAPES[CATEGORY_SEASONALITY_ASSIGNMENT[cat_name_by_id[cid]]]
        for cid in range(1, N_CATEGORIES + 1)
    }
    pair_cat = np.array([cat_by_product[p] for p in pairs_product])

    opening = RNG.integers(30, 250, size=n_pairs).astype(float)
    restock_prob = 1.0 / RNG.integers(7, 21, size=n_pairs)

    all_rows_store = []
    all_rows_product = []
    all_rows_date = []
    all_opening = []
    all_received = []
    all_sold = []
    all_closing = []

    current_date = DATASET_START
    day_idx = 0
    while current_date <= DATASET_END:
        month = current_date.month
        seasonality = np.array([seasonality_shape_by_cat[c][month - 1] for c in pair_cat])

        restock_mask = RNG.random(n_pairs) < restock_prob
        received = np.where(restock_mask, RNG.integers(50, 300, size=n_pairs), 0).astype(float)

        demand_mean = np.clip(base_demand * seasonality * 0.02, 0.05, None)
        demand = RNG.poisson(demand_mean)

        available = opening + received
        sold = np.minimum(demand, available)
        closing = available - sold

        all_rows_store.append(pairs_store)
        all_rows_product.append(pairs_product)
        all_rows_date.append(np.full(n_pairs, current_date))
        all_opening.append(opening.copy())
        all_received.append(received.copy())
        all_sold.append(sold.copy())
        all_closing.append(closing.copy())

        opening = closing
        current_date += timedelta(days=1)
        day_idx += 1

    df = pd.DataFrame({
        "store_id": np.concatenate(all_rows_store),
        "product_id": np.concatenate(all_rows_product),
        "inventory_date": np.concatenate(all_rows_date),
        "opening_stock": np.concatenate(all_opening).astype(int),
        "received_quantity": np.concatenate(all_received).astype(int),
        "sold_quantity": np.concatenate(all_sold).astype(int),
        "closing_stock": np.concatenate(all_closing).astype(int),
    })
    return df


def gen_campaigns() -> tuple[pd.DataFrame, np.ndarray]:
    starts = random_dates_between(DATASET_START, DATASET_END - timedelta(days=14), N_CAMPAIGNS, RNG)
    durations = RNG.integers(10, 60, size=N_CAMPAIGNS)
    ends = [min(s + timedelta(days=int(d)), DATASET_END) for s, d in zip(starts, durations)]
    channels = RNG.choice(CAMPAIGN_CHANNELS, size=N_CAMPAIGNS)
    budgets = np.round(RNG.uniform(50000, 3000000, size=N_CAMPAIGNS), -2)
    names = [f"{channels[i]} Campaign {starts[i].strftime('%b %Y')} #{i+1}" for i in range(N_CAMPAIGNS)]

    # Hidden effectiveness score: most campaigns are mediocre, a few are
    # standouts, a few are duds -- for the "did this campaign work?" questions
    effectiveness = RNG.beta(2, 5, size=N_CAMPAIGNS)

    df = pd.DataFrame({
        "campaign_id": np.arange(1, N_CAMPAIGNS + 1),
        "campaign_name": names,
        "channel": channels,
        "start_date": starts,
        "end_date": ends,
        "budget": budgets,
    })
    return df, effectiveness


def gen_customer_campaigns(customers: pd.DataFrame, campaigns: pd.DataFrame, effectiveness: np.ndarray) -> pd.DataFrame:
    rows = []
    interaction_id = 1
    customer_ids = customers["customer_id"].to_numpy()

    for c in campaigns.itertuples(index=False):
        eff = effectiveness[c.campaign_id - 1]
        reach = int(RNG.integers(800, 4000))
        reached = RNG.choice(customer_ids, size=min(reach, len(customer_ids)), replace=False)

        for cust_id in reached:
            interaction_date = c.start_date + timedelta(
                days=int(RNG.integers(0, max(1, (c.end_date - c.start_date).days + 1)))
            )
            rows.append((interaction_id, cust_id, c.campaign_id, interaction_date, "impression"))
            interaction_id += 1

            if RNG.random() < (0.15 + 0.35 * eff):
                click_date = interaction_date + timedelta(days=int(RNG.integers(0, 3)))
                click_date = min(click_date, c.end_date)
                rows.append((interaction_id, cust_id, c.campaign_id, click_date, "click"))
                interaction_id += 1

                if RNG.random() < (0.05 + 0.5 * eff):
                    conv_date = click_date + timedelta(days=int(RNG.integers(0, 5)))
                    rows.append((interaction_id, cust_id, c.campaign_id, conv_date, "conversion"))
                    interaction_id += 1

    df = pd.DataFrame(rows, columns=[
        "interaction_id", "customer_id", "campaign_id", "interaction_date", "interaction_type",
    ])
    return df


def gen_support_tickets(customers: pd.DataFrame) -> pd.DataFrame:
    # Most customers never file a ticket; a few file several
    n_tickets = 35000
    weights = RNG.exponential(scale=1.0, size=N_CUSTOMERS)
    weights = weights / weights.sum()
    customer_ids = RNG.choice(customers["customer_id"], size=n_tickets, p=weights)

    created_dates = random_dates_between(DATASET_START, DATASET_END, n_tickets, RNG)
    created_ats = [
        datetime.combine(d, datetime.min.time()) + timedelta(hours=int(RNG.integers(8, 20)), minutes=int(RNG.integers(0, 60)))
        for d in created_dates
    ]

    priorities = RNG.choice(["low", "medium", "high", "urgent"], size=n_tickets, p=[0.35, 0.40, 0.20, 0.05])
    issue_types = RNG.choice(TICKET_ISSUE_TYPES, size=n_tickets)

    resolved_ats = []
    statuses = []
    for created, prio in zip(created_ats, priorities):
        days_since_created = (DATASET_END - created.date()).days
        resolution_hours = {"urgent": 6, "high": 24, "medium": 72, "low": 168}[prio]
        resolution_hours = int(RNG.exponential(resolution_hours))

        if days_since_created * 24 < resolution_hours or RNG.random() < 0.05:
            resolved_ats.append(None)
            statuses.append(RNG.choice(["open", "pending"], p=[0.6, 0.4]))
        else:
            resolved_at = created + timedelta(hours=resolution_hours)
            if resolved_at.date() > DATASET_END:
                resolved_ats.append(None)
                statuses.append(RNG.choice(["open", "pending"], p=[0.6, 0.4]))
            else:
                resolved_ats.append(resolved_at)
                statuses.append(RNG.choice(["resolved", "closed"], p=[0.4, 0.6]))

    df = pd.DataFrame({
        "ticket_id": np.arange(1, n_tickets + 1),
        "customer_id": customer_ids,
        "created_at": created_ats,
        "resolved_at": resolved_ats,
        "issue_type": issue_types,
        "priority": priorities,
        "status": statuses,
    })
    return df


# ------------------------------------------------------------------
# Orchestration
# ------------------------------------------------------------------

def build_all() -> dict[str, pd.DataFrame]:
    print("Generating categories, brands, products...")
    categories = gen_categories()
    brands = gen_brands()
    products, popularity, category_ids = gen_products(categories, brands)

    print("Generating stores, employees...")
    stores, store_performance = gen_stores()
    employees = gen_employees(stores)

    print("Generating customers...")
    customers, archetypes, spend_multiplier = gen_customers()

    print("Generating orders (this covers 24 months per customer archetype)...")
    orders = gen_orders(customers, archetypes, stores, store_performance)
    print(f"  -> {len(orders):,} orders")

    print("Generating order_items...")
    order_items = gen_order_items(orders, products, popularity)
    print(f"  -> {len(order_items):,} order_items")

    print("Generating payments...")
    payments = gen_payments(orders, order_items)
    print(f"  -> {len(payments):,} payments")

    print("Generating returns...")
    returns = gen_returns(orders, order_items)
    print(f"  -> {len(returns):,} returns")

    print("Generating inventory ledger (day-by-day vectorized)...")
    inventory = gen_inventory(stores, products, popularity, store_performance, category_ids)
    print(f"  -> {len(inventory):,} inventory rows")

    print("Generating campaigns and interactions...")
    campaigns, effectiveness = gen_campaigns()
    customer_campaigns = gen_customer_campaigns(customers, campaigns, effectiveness)
    print(f"  -> {len(customer_campaigns):,} customer_campaigns interactions")

    print("Generating support tickets...")
    support_tickets = gen_support_tickets(customers)
    print(f"  -> {len(support_tickets):,} support_tickets")

    return {
        "categories": categories,
        "brands": brands,
        "products": products,
        "stores": stores,
        "employees": employees,
        "customers": customers,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "returns": returns,
        "inventory": inventory,
        "campaigns": campaigns,
        "customer_campaigns": customer_campaigns,
        "support_tickets": support_tickets,
    }


LOAD_ORDER = [
    "categories", "brands", "products", "stores", "employees", "customers",
    "orders", "order_items", "payments", "returns", "inventory",
    "campaigns", "customer_campaigns", "support_tickets",
]


def write_csvs(tables: dict[str, pd.DataFrame]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name in LOAD_ORDER:
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        tables[name].to_csv(path, index=False)
        print(f"  wrote {path} ({len(tables[name]):,} rows)")


def load_to_mysql(tables: dict[str, pd.DataFrame]) -> None:
    from sqlalchemy import create_engine, text

    host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    port = os.environ.get("MYSQL_PORT", "3306")
    user = os.environ.get("MYSQL_USER", "gym_user")
    password = os.environ.get("MYSQL_PASSWORD", "gym_pw")
    database = os.environ.get("MYSQL_DATABASE", "sql_gym")

    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)

    print(f"Connecting to {host}:{port}/{database} as {user}...")
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for name in reversed(LOAD_ORDER):
            conn.execute(text(f"TRUNCATE TABLE {name}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    for name in LOAD_ORDER:
        df = tables[name]
        print(f"Loading {name} ({len(df):,} rows)...")
        df.to_sql(name, engine, if_exists="append", index=False, chunksize=5000, method="multi")

    print("Done loading all tables.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv-only", action="store_true", help="Write CSVs only, skip MySQL load")
    args = parser.parse_args()

    tables = build_all()

    print("\nWriting CSVs to data_generation/output/ ...")
    write_csvs(tables)

    if not args.csv_only:
        load_to_mysql(tables)

    print("\nSummary:")
    for name in LOAD_ORDER:
        print(f"  {name:<20} {len(tables[name]):>10,} rows")


if __name__ == "__main__":
    sys.exit(main())
