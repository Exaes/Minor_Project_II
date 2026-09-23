"""
Generate a realistic synthetic reference dataset of ~500 startups.

Covers all required columns for the analysis pipeline:
- Company identifiers (name, industry, founding year, funding stage)
- Financial metrics (revenue, expenses, burn, funding, etc.)
- Operational metrics (headcount, customers, marketing spend)
- Outcome labels (success/fail status)

Run:
    python scripts/generate_synthetic_data.py
"""

import os
import sys
import numpy as np
import pandas as pd

# ── Ensure project root is on the path ──
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# ── Configuration ──
NUM_STARTUPS = 500
RANDOM_SEED = 42
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data_layer", "raw", "reference_startups.csv")

INDUSTRIES = {
    "SaaS":        {"weight": 0.30, "margin_mean": 0.70, "margin_std": 0.12},
    "Fintech":     {"weight": 0.20, "margin_mean": 0.55, "margin_std": 0.15},
    "HealthTech":  {"weight": 0.15, "margin_mean": 0.50, "margin_std": 0.14},
    "E-commerce":  {"weight": 0.15, "margin_mean": 0.35, "margin_std": 0.12},
    "EdTech":      {"weight": 0.10, "margin_mean": 0.60, "margin_std": 0.13},
    "CleanTech":   {"weight": 0.10, "margin_mean": 0.40, "margin_std": 0.16},
}

FUNDING_STAGES = ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"]
STAGE_FUNDING_RANGES = {
    "Pre-seed":  (50_000,    500_000),
    "Seed":      (300_000,  3_000_000),
    "Series A":  (2_000_000, 15_000_000),
    "Series B":  (10_000_000, 50_000_000),
    "Series C+": (30_000_000, 150_000_000),
}
STAGE_WEIGHTS = [0.20, 0.30, 0.25, 0.15, 0.10]

SIZE_HEADCOUNT = {
    "Pre-seed":  (2, 10),
    "Seed":      (5, 30),
    "Series A":  (20, 80),
    "Series B":  (50, 250),
    "Series C+": (100, 500),
}

# Tech company name prefixes and suffixes for realistic names
NAME_PREFIXES = [
    "Nova", "Apex", "Pulse", "Vero", "Flux", "Zeta", "Aura", "Nexo",
    "Lyra", "Hexa", "Qubit", "Orbis", "Vela", "Axon", "Dyna", "Crest",
    "Prio", "Sync", "Byte", "Echo", "Mira", "Alto", "Revo", "Luma",
    "Core", "Fuse", "Halo", "Neon", "Sage", "Tide", "Vibe", "Wave",
    "Zoom", "Agile", "Bloom", "Cloud", "Dart", "Edge", "Grid", "Hyper",
    "Ionic", "Jolt", "Kite", "Leap", "Mesh", "Node", "Opti", "Peak",
]
NAME_SUFFIXES = [
    "Labs", "AI", "Tech", "ly", "io", "Hub", "Stack", "Works",
    "ify", "Base", "X", "Flow", "Mind", "Shift", "Spark", "Forge",
    "Net", "Sense", "Logic", "Ware", "Point", "Path", "Link", "Cloud",
]


def _generate_company_names(n: int, rng: np.random.Generator) -> list[str]:
    """Generate unique startup-like company names."""
    names = set()
    while len(names) < n:
        prefix = rng.choice(NAME_PREFIXES)
        suffix = rng.choice(NAME_SUFFIXES)
        names.add(f"{prefix}{suffix}")
    return list(names)[:n]


def _assign_industries(n: int, rng: np.random.Generator) -> list[str]:
    """Assign industries based on configured weights."""
    industries = list(INDUSTRIES.keys())
    weights = [INDUSTRIES[i]["weight"] for i in industries]
    return rng.choice(industries, size=n, p=weights).tolist()


def _assign_stages(n: int, rng: np.random.Generator) -> list[str]:
    """Assign funding stages based on configured weights."""
    return rng.choice(FUNDING_STAGES, size=n, p=STAGE_WEIGHTS).tolist()


def generate_dataset() -> pd.DataFrame:
    """Generate the full synthetic startup dataset."""
    rng = np.random.default_rng(RANDOM_SEED)

    names = _generate_company_names(NUM_STARTUPS, rng)
    industries = _assign_industries(NUM_STARTUPS, rng)
    stages = _assign_stages(NUM_STARTUPS, rng)

    records = []
    for i in range(NUM_STARTUPS):
        industry = industries[i]
        stage = stages[i]
        ind_cfg = INDUSTRIES[industry]

        # ── Founding year (2010–2023) ──
        founding_year = int(rng.integers(2010, 2024))
        company_age_years = 2024 - founding_year

        # ── Headcount ──
        hc_lo, hc_hi = SIZE_HEADCOUNT[stage]
        headcount = int(rng.integers(hc_lo, hc_hi + 1))

        # ── Funding ──
        fund_lo, fund_hi = STAGE_FUNDING_RANGES[stage]
        total_funding = float(rng.lognormal(
            mean=np.log((fund_lo + fund_hi) / 2),
            sigma=0.5
        ))
        total_funding = np.clip(total_funding, fund_lo * 0.5, fund_hi * 2)

        funding_rounds = max(1, FUNDING_STAGES.index(stage) + int(rng.integers(0, 2)))

        # ── Revenue (correlated with stage & funding) ──
        revenue_multiplier = rng.lognormal(mean=0.0, sigma=0.6)
        monthly_revenue = total_funding * revenue_multiplier * (0.02 + 0.03 * FUNDING_STAGES.index(stage))
        monthly_revenue = max(1000, monthly_revenue)

        # ── COGS & Gross Margin ──
        gross_margin = np.clip(
            rng.normal(ind_cfg["margin_mean"], ind_cfg["margin_std"]),
            0.05, 0.95
        )
        cogs = monthly_revenue * (1 - gross_margin)

        # ── Operating Expenses ──
        # Salary-heavy for early stage, more diverse later
        avg_salary_monthly = rng.normal(8000, 2000)
        salary_expense = headcount * max(3000, avg_salary_monthly)

        marketing_spend = monthly_revenue * rng.uniform(0.1, 0.6)
        other_opex = monthly_revenue * rng.uniform(0.05, 0.25)

        operating_expenses = salary_expense + marketing_spend + other_opex
        monthly_expenses = cogs + operating_expenses

        # ── Burn Rate ──
        monthly_burn = max(0, monthly_expenses - monthly_revenue)

        # ── Customers ──
        if industry in ("SaaS", "EdTech"):
            customer_count = int(rng.lognormal(mean=np.log(headcount * 20), sigma=0.8))
        elif industry == "E-commerce":
            customer_count = int(rng.lognormal(mean=np.log(headcount * 100), sigma=0.9))
        else:
            customer_count = int(rng.lognormal(mean=np.log(headcount * 15), sigma=0.7))
        customer_count = max(10, customer_count)

        # ── Growth rates (MoM) ──
        mom_revenue_growth = rng.normal(0.06, 0.08)  # ~6% MoM mean
        mom_customer_growth = rng.normal(0.05, 0.06)
        yoy_revenue_growth = (1 + mom_revenue_growth) ** 12 - 1

        # ── New customers per month (for CAC computation) ──
        new_customers_monthly = max(1, int(customer_count * max(0.02, mom_customer_growth)))

        # ── Average revenue per customer ──
        avg_revenue_per_customer = monthly_revenue / max(1, customer_count)

        # ── Customer lifetime (months) ──
        avg_customer_lifetime = rng.uniform(12, 48)

        # ── Gross profit ──
        gross_profit = monthly_revenue - cogs

        # ── Success label ──
        # Success is influenced by: good margins, runway, growth, unit economics
        runway = total_funding / max(1, monthly_burn) if monthly_burn > 0 else 120
        ltv = avg_revenue_per_customer * avg_customer_lifetime
        cac = marketing_spend / max(1, new_customers_monthly)
        ltv_cac = ltv / max(1, cac)
        funding_efficiency = (monthly_revenue * 12) / max(1, total_funding)

        # Composite success score (higher = more likely successful)
        success_score = (
            0.20 * min(gross_margin / 0.70, 1.5) +
            0.15 * min(runway / 24, 1.5) +
            0.20 * min(max(mom_revenue_growth, 0) / 0.10, 1.5) +
            0.20 * min(ltv_cac / 3.0, 1.5) +
            0.10 * min(funding_efficiency / 0.5, 1.5) +
            0.15 * min(company_age_years / 5, 1.5)
        )
        # Add noise
        success_score += rng.normal(0, 0.15)
        # Threshold — ~35% success rate
        is_successful = 1 if success_score > 0.72 else 0

        records.append({
            "company_name": names[i],
            "industry": industry,
            "founding_year": founding_year,
            "funding_stage": stage,
            "total_funding_usd": round(total_funding, 2),
            "funding_rounds_count": funding_rounds,
            "monthly_revenue": round(monthly_revenue, 2),
            "monthly_expenses": round(monthly_expenses, 2),
            "cogs": round(cogs, 2),
            "operating_expenses": round(operating_expenses, 2),
            "gross_profit": round(gross_profit, 2),
            "headcount": headcount,
            "customer_count": customer_count,
            "monthly_burn": round(monthly_burn, 2),
            "marketing_spend": round(marketing_spend, 2),
            "avg_revenue_per_customer": round(avg_revenue_per_customer, 2),
            "avg_customer_lifetime_months": round(avg_customer_lifetime, 1),
            "new_customers_monthly": new_customers_monthly,
            "mom_revenue_growth": round(mom_revenue_growth, 4),
            "mom_customer_growth": round(mom_customer_growth, 4),
            "yoy_revenue_growth": round(yoy_revenue_growth, 4),
            "status": is_successful,
        })

    df = pd.DataFrame(records)

    # Print summary
    print(f"Generated {len(df)} startup records")
    print(f"Success rate: {df['status'].mean():.1%}")
    print(f"\nIndustry distribution:")
    print(df["industry"].value_counts().to_string())
    print(f"\nStage distribution:")
    print(df["funding_stage"].value_counts().to_string())
    print(f"\nSample columns: {list(df.columns)}")

    return df


def main():
    df = generate_dataset()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
