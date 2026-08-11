"""
Dashboard AI Context Builder
============================

Builds ONE plain-text snapshot covering every dashboard domain — Overview,
Production, Service, Access and Finance — for the AI chat assistant.

Why this module exists: the assistant used to receive only the ten Overview
scorecard KPIs plus three per-country metrics, so any question about a metric
that lives on another tab (metering ratio, water quality, JMP ladders, payment
risk, wastewater treatment, ...) came back as "I do not have data on that
within the provided context."

Every figure here is computed with the SAME formulas the matching page module
uses, so the assistant's answers agree with what is on screen. Each section is
built defensively: if one domain fails, that section degrades to a short note
instead of breaking the chat.
"""

import pandas as pd
import streamlit as st

from utils.kpi_calculator import (
    BENCHMARKS,
    calculate_all_country_kpis,
    calculate_collection_efficiency,
    calculate_commercial_nrw,
    calculate_complaint_resolution_rate,
    calculate_cost_recovery_ratio,
    calculate_metering_ratio,
    calculate_nrw,
    calculate_physical_nrw,
    calculate_staff_productivity,
    calculate_summary_kpis,
    calculate_water_quality_compliance,
    get_payment_by_zone,
    identify_payment_risk_customers,
)
from utils.currency_config import get_currency_config

# Keep list-style details short so the prompt stays compact.
TOP_N = 5


# --- small helpers -----------------------------------------------------------

def _frame(data, key, countries=None):
    """Return a country-filtered copy of a dataset, or an empty frame."""
    df = data.get(key)
    if df is None or len(df) == 0:
        return pd.DataFrame()
    df = df.copy()
    if countries and 'country' in df.columns:
        df = df[df['country'].isin(countries)]
    return df


def _sum(df, col):
    """Sum a column, tolerating a missing column or empty frame."""
    if df is None or df.empty or col not in df.columns:
        return 0
    total = df[col].sum()
    return 0 if pd.isna(total) else total


def _mean(df, col):
    """Mean of a column, tolerating a missing column or empty frame."""
    if df is None or df.empty or col not in df.columns:
        return 0
    value = df[col].mean()
    return 0 if pd.isna(value) else value


def _pct(part, whole):
    return (part / whole * 100) if whole else 0


def _latest_year_slice(df):
    """Rows belonging to the most recent year present in the frame."""
    if df is None or df.empty or 'year' not in df.columns or df['year'].isna().all():
        return df if df is not None else pd.DataFrame(), None
    latest = df['year'].max()
    return df[df['year'] == latest], int(latest)


def _currency_label(countries):
    """Currency the raw CSV values are expressed in, for the given selection."""
    if countries and len(countries) == 1:
        return get_currency_config(countries[0]).get('symbol', 'LCU')
    return 'local currency units (LCU)'


def _render_section(title, lines):
    """Format one section; lines starting with whitespace stay un-bulleted."""
    if not lines:
        lines = ["No data available for the current filter selection."]
    body = "\n".join(
        line if line.startswith((' ', '\t')) else f"- {line}"
        for line in lines
    )
    return f"## {title}\n{body}\n"


def _safe(builder, *args):
    """Run a section builder without letting one bad domain break the context."""
    try:
        return builder(*args)
    except Exception as exc:  # noqa: BLE001 - the chat must never hard-fail here
        return [f"Section unavailable ({type(exc).__name__}: {exc})."]


# --- section builders --------------------------------------------------------

def _overview_lines(data, countries):
    """The ten Overview scorecard KPIs, plus the secondary summary metrics."""
    kpis = calculate_summary_kpis(data) or {}
    if not kpis:
        return []

    labels = [
        ('total_households', 'Total Households', '{:,.0f}'),
        ('water_service_coverage', 'Water Service Coverage', '{:.1f}%'),
        ('access_rate_growth', 'Access Rate Growth (YoY)', '{:+.1f}%'),
        ('collection_efficiency', 'Revenue Collection Efficiency', '{:.1f}%'),
        ('cost_recovery_ratio', 'Cost Recovery Ratio (OCCR)', '{:.1f}%'),
        ('operational_profit_loss', 'Operational Profit/Loss', '{:,.0f}'),
        ('nrw', 'Non-Revenue Water (NRW)', '{:.1f}%'),
        ('service_continuity', 'Service Continuity', '{:.1f} hrs/day'),
        ('complaints_count', 'Reported Complaints (Total)', '{:,.0f}'),
        ('complaint_resolution_time', 'Avg. Complaint Resolution Time', '{:.1f} days'),
        ('sanitation_coverage', 'Sanitation Coverage', '{:.1f}%'),
        ('water_quality', 'Water Quality Compliance (Chlorine)', '{:.1f}%'),
        ('metering_ratio', 'Metering Ratio', '{:.1f}%'),
        ('personnel_cost_ratio', 'Personnel Cost as % of O&M', '{:.1f}%'),
        ('staff_productivity', 'Staff Productivity', '{:.1f} staff per 1,000 connections'),
    ]

    lines = []
    for key, label, fmt in labels:
        metric = kpis.get(key)
        if not metric or 'value' not in metric:
            continue
        target = metric.get('benchmark')
        target_txt = f" (target: {target}{metric.get('unit', '')})" if target else ""
        lines.append(f"{label}: {fmt.format(metric['value'])}{target_txt}")
    return lines


def _production_lines(data, countries):
    """Mirrors page_modules/production.py."""
    production = _frame(data, 'production', countries)
    if production.empty:
        return []

    w_service = _frame(data, 'w_service', countries)
    finance = _frame(data, 'finance', countries)
    billing = _frame(data, 'billing', countries)

    total_production = _sum(production, 'production_m3')
    daily_totals = production.groupby('date')['production_m3'].sum()
    daily_avg = daily_totals.mean() if not daily_totals.empty else 0
    peak_daily = daily_totals.max() if not daily_totals.empty else 0
    capacity_utilization = _pct(daily_avg, peak_daily)
    avg_service_hours = _mean(production, 'service_hours')
    total_opex = _sum(finance, 'opex')
    unit_cost = (total_opex / total_production) if total_production else 0

    if not billing.empty and 'consumption_m3' in billing.columns:
        billed_volume = _sum(billing, 'consumption_m3')
        volume_source = 'billing.csv customer consumption'
    else:
        billed_volume = _sum(w_service, 'metered')
        volume_source = 'w_service.csv metered volume'
    nrw = calculate_nrw(total_production, billed_volume)
    losses = max(total_production - billed_volume, 0)

    lines = [
        f"Total water produced: {total_production:,.0f} m³ ({total_production / 1e6:.2f} million m³)",
        f"Average daily production: {daily_avg:,.0f} m³/day (peak day: {peak_daily:,.0f} m³)",
        f"Capacity utilisation: {capacity_utilization:.1f}% of peak daily output",
        f"Average service hours: {avg_service_hours:.1f} hrs/day "
        f"(operational benchmark 20 hrs/day, ideal {BENCHMARKS['service_hours']} hrs/day)",
        f"Unit production cost: {unit_cost:,.2f} per m³ (opex ÷ volume produced)",
        f"Non-Revenue Water: {nrw:.1f}% (benchmark ≤{BENCHMARKS['nrw']}%), derived from {volume_source}",
        f"Water balance: {total_production / 1e6:.2f}M m³ produced → "
        f"{billed_volume / 1e6:.2f}M m³ billed → {losses / 1e6:.2f}M m³ lost (NRW)",
    ]

    if 'date' in production.columns and production['date'].notna().any():
        lines.append(
            f"Data period covered: {production['date'].min():%d %b %Y} to {production['date'].max():%d %b %Y}"
        )

    if 'source' in production.columns:
        by_source = (
            production.groupby('source')
            .agg(volume=('production_m3', 'sum'), hours=('service_hours', 'mean'))
            .reset_index()
            .sort_values('volume', ascending=False)
        )
        lines.append(f"Number of distinct water sources: {len(by_source)}")
        lines.append(f"Top water sources by volume (of {len(by_source)}):")
        for _, row in by_source.head(TOP_N).iterrows():
            lines.append(
                f"  · {row['source']}: {row['volume']:,.0f} m³ "
                f"({_pct(row['volume'], total_production):.1f}% of production), "
                f"{row['hours']:.1f} hrs/day"
            )
        low = by_source[by_source['hours'] < 20]
        if low.empty:
            lines.append("Sources below the 20 hrs/day benchmark: none — all sources meet the benchmark")
        else:
            lines.append(f"Sources below the 20 hrs/day benchmark: {len(low)}")
            for _, row in low.head(TOP_N).iterrows():
                lines.append(f"  · {row['source']}: {row['hours']:.1f} hrs/day")

    if 'year' in production.columns:
        yearly = production.groupby('year')['production_m3'].sum()
        if not yearly.empty:
            lines.append("Annual production trend:")
            for year, volume in yearly.items():
                lines.append(f"  · {int(year)}: {volume / 1e6:.2f} million m³")

    return lines


def _service_lines(data, countries):
    """Mirrors page_modules/service.py."""
    w_service = _frame(data, 'w_service', countries)
    s_service = _frame(data, 's_service', countries)
    finance = _frame(data, 'finance', countries)

    if w_service.empty and s_service.empty and finance.empty:
        return []

    lines = []

    # --- Water quality ---
    chlorine_rate = calculate_water_quality_compliance(
        _sum(w_service, 'test_passed_chlorine'), _sum(w_service, 'tests_conducted_chlorine')
    )
    ecoli_rate = calculate_water_quality_compliance(
        _sum(w_service, 'tests_passed_ecoli'), _sum(w_service, 'test_conducted_ecoli')
    )
    lines.append(
        f"Water quality — chlorine compliance: {chlorine_rate:.1f}% "
        f"({_sum(w_service, 'test_passed_chlorine'):,.0f} of "
        f"{_sum(w_service, 'tests_conducted_chlorine'):,.0f} tests passed, "
        f"target ≥{BENCHMARKS['water_quality']}%)"
    )
    lines.append(
        f"Water quality — E.coli compliance: {ecoli_rate:.1f}% "
        f"({_sum(w_service, 'tests_passed_ecoli'):,.0f} of "
        f"{_sum(w_service, 'test_conducted_ecoli'):,.0f} tests passed, "
        f"target ≥{BENCHMARKS['water_quality']}%)"
    )

    # --- Metering ---
    metered = _sum(w_service, 'metered')
    total_consumption = _sum(w_service, 'total_consumption')
    metering_rate = calculate_metering_ratio(metered, total_consumption)
    lines.append(
        f"Metering ratio: {metering_rate:.1f}% (target ≥{BENCHMARKS['metering_ratio']}%) — "
        f"{metered:,.0f} m³ metered out of {total_consumption:,.0f} m³ total consumption"
    )
    lines.append(f"Water supplied (w_service): {_sum(w_service, 'w_supplied'):,.0f} m³")

    if not w_service.empty and 'zone' in w_service.columns:
        by_zone = (
            w_service.groupby(['country', 'zone'])
            .agg(metered=('metered', 'sum'), consumption=('total_consumption', 'sum'))
            .reset_index()
        )
        by_zone['ratio'] = by_zone.apply(
            lambda r: calculate_metering_ratio(r['metered'], r['consumption']), axis=1
        )
        by_zone = by_zone.sort_values('ratio')
        lines.append("Zones with the lowest metering ratio (priority for meter installation):")
        for _, row in by_zone.head(TOP_N).iterrows():
            lines.append(f"  · {row['zone']} ({row['country']}): {row['ratio']:.1f}% metered")

    # --- Complaints ---
    complaints = _sum(finance, 'complaints')
    resolved = _sum(finance, 'resolved')
    resolution_rate = calculate_complaint_resolution_rate(resolved, complaints)
    lines.append(
        f"Complaints: {complaints:,.0f} reported, {resolved:,.0f} resolved, "
        f"{max(complaints - resolved, 0):,.0f} unresolved — resolution rate {resolution_rate:.1f}% "
        f"(target ≥{BENCHMARKS['complaint_resolution']}%)"
    )

    # --- Wastewater ---
    ww_collected = _sum(s_service, 'ww_collected')
    ww_treated = _sum(s_service, 'ww_treated')
    ww_reused = _sum(s_service, 'ww_reused')
    lines.append(
        f"Wastewater: {ww_collected:,.0f} m³ collected, {ww_treated:,.0f} m³ treated "
        f"(treatment rate {_pct(ww_treated, ww_collected):.1f}%), {ww_reused:,.0f} m³ reused "
        f"(reuse rate {_pct(ww_reused, ww_treated):.1f}% of treated)"
    )
    lines.append(
        f"Faecal sludge: {_sum(s_service, 'hh_emptied'):,.0f} households emptied, "
        f"{_sum(s_service, 'fs_treated'):,.0f} m³ treated, {_sum(s_service, 'fs_reused'):,.0f} m³ reused"
    )

    # --- Connections (latest reporting month per zone) ---
    if not s_service.empty and 'date' in s_service.columns:
        latest = s_service.sort_values('date').drop_duplicates(subset=['country', 'zone'], keep='last')
        lines.append(
            f"Sewer connections: {_sum(latest, 'sewer_connections'):,.0f}; "
            f"public toilets: {_sum(latest, 'public_toilets'):,.0f}; "
            f"sanitation workforce: {_sum(latest, 'workforce'):,.0f} "
            f"(of which female: {_sum(latest, 'f_workforce'):,.0f})"
        )

    if not w_service.empty and 'date' in w_service.columns:
        latest_w = w_service.sort_values('date').drop_duplicates(subset=['country', 'zone'], keep='last')
        lines.append(f"Households served (latest reporting month): {_sum(latest_w, 'households'):,.0f}")

    return lines


def _access_lines(data, countries):
    """Mirrors page_modules/access.py."""
    w_access = _frame(data, 'w_access', countries)
    s_access = _frame(data, 's_access', countries)
    if w_access.empty and s_access.empty:
        return []

    w_latest, w_year = _latest_year_slice(w_access)
    s_latest, s_year = _latest_year_slice(s_access)

    lines = []
    if w_year:
        lines.append(f"Access figures below are for the latest reporting year: {w_year}")

    # --- Water JMP ladder ---
    pop_w = _sum(w_latest, 'popn_total')
    if pop_w:
        rungs = [
            ('Safely managed', 'safely_managed'),
            ('Basic', 'basic'),
            ('Limited', 'limited'),
            ('Unimproved', 'unimproved'),
            ('Surface water', 'surface_water'),
        ]
        lines.append(f"Total population covered by water access data: {pop_w:,.0f}")
        lines.append(f"Households (water access): {_sum(w_latest, 'households'):,.0f}")
        lines.append("Water access — JMP service ladder:")
        for label, col in rungs:
            value = _sum(w_latest, col)
            lines.append(f"  · {label}: {value:,.0f} people ({_pct(value, pop_w):.1f}%)")
        coverage_w = _pct(_sum(w_latest, 'safely_managed') + _sum(w_latest, 'basic'), pop_w)
        lines.append(
            f"Water coverage (safely managed + basic): {coverage_w:.1f}% — "
            f"gap to universal coverage: {max(100 - coverage_w, 0):.1f}%"
        )
        municipal = _sum(w_latest, 'municipal_coverage')
        lines.append(
            f"Urban vs rural split: {_pct(municipal, pop_w):.1f}% municipal (urban) coverage, "
            f"{max(100 - _pct(municipal, pop_w), 0):.1f}% non-municipal (rural)"
        )

        if 'zone' in w_latest.columns:
            zones = w_latest.copy()
            zones['coverage'] = zones.apply(
                lambda r: _pct(r.get('safely_managed', 0) + r.get('basic', 0), r.get('popn_total', 0)),
                axis=1,
            )
            zones = zones.sort_values('coverage')
            underserved = zones[zones['coverage'] < 50]
            lines.append(f"Zones below 50% water coverage: {len(underserved)} of {len(zones)}")
            lines.append("Priority zones (lowest water coverage):")
            for _, row in zones.head(TOP_N).iterrows():
                lines.append(
                    f"  · {row['zone']} ({row['country']}): {row['coverage']:.1f}% coverage, "
                    f"population {row.get('popn_total', 0):,.0f}"
                )

    # --- Sanitation JMP ladder ---
    pop_s = _sum(s_latest, 'popn_total')
    if pop_s:
        if s_year and s_year != w_year:
            lines.append(f"Sanitation figures are for reporting year {s_year}")
        rungs = [
            ('Safely managed', 'safely_managed'),
            ('Basic', 'basic'),
            ('Limited', 'limited'),
            ('Unimproved', 'unimproved'),
            ('Open defecation', 'open_def'),
        ]
        lines.append("Sanitation access — JMP service ladder:")
        for label, col in rungs:
            value = _sum(s_latest, col)
            lines.append(f"  · {label}: {value:,.0f} people ({_pct(value, pop_s):.1f}%)")
        coverage_s = _pct(_sum(s_latest, 'safely_managed') + _sum(s_latest, 'basic'), pop_s)
        lines.append(
            f"Sanitation coverage (safely managed + basic): {coverage_s:.1f}% — "
            f"gap to universal coverage: {max(100 - coverage_s, 0):.1f}%"
        )
        if 'open_def' in s_latest.columns and 'zone' in s_latest.columns:
            hotspots = s_latest.nlargest(TOP_N, 'open_def')
            lines.append("Open defecation hotspots (highest absolute numbers):")
            for _, row in hotspots.iterrows():
                lines.append(
                    f"  · {row['zone']} ({row['country']}): {row['open_def']:,.0f} people "
                    f"({row.get('open_def_pct', 0):.1f}%)"
                )

    # --- Trends ---
    if not w_access.empty and 'year' in w_access.columns:
        trend = w_access.groupby('year').agg(
            sm=('safely_managed', 'sum'), basic=('basic', 'sum'), pop=('popn_total', 'sum')
        )
        if not trend.empty:
            lines.append("Water coverage trend by year (safely managed + basic):")
            for year, row in trend.iterrows():
                lines.append(f"  · {int(year)}: {_pct(row['sm'] + row['basic'], row['pop']):.1f}%")

    if not s_access.empty and 'year' in s_access.columns:
        trend = s_access.groupby('year').agg(
            sm=('safely_managed', 'sum'), basic=('basic', 'sum'), pop=('popn_total', 'sum')
        )
        if not trend.empty:
            lines.append("Sanitation coverage trend by year (safely managed + basic):")
            for year, row in trend.iterrows():
                lines.append(f"  · {int(year)}: {_pct(row['sm'] + row['basic'], row['pop']):.1f}%")

    return lines


def _finance_lines(data, countries):
    """Mirrors page_modules/finance.py."""
    finance = _frame(data, 'finance', countries)
    billing = _frame(data, 'billing', countries)
    national = _frame(data, 'national', countries)
    production = _frame(data, 'production', countries)
    w_service = _frame(data, 'w_service', countries)

    if finance.empty and billing.empty:
        return []

    currency = _currency_label(countries)
    lines = [f"All monetary values below are in {currency} unless stated otherwise."]

    # NOTE: despite the column names, `sewer_billed` / `sewer_revenue` hold
    # TOTAL billed and TOTAL revenue (see CLAUDE.md) — every financial KPI in
    # this app reads them that way.
    total_billed = _sum(finance, 'sewer_billed')
    total_revenue = _sum(finance, 'sewer_revenue')
    total_opex = _sum(finance, 'opex')
    occr = calculate_cost_recovery_ratio(total_revenue, total_opex)
    collection_efficiency = calculate_collection_efficiency(total_revenue, total_billed)

    lines.extend([
        f"Total amount billed: {total_billed:,.0f}",
        f"Total revenue collected: {total_revenue:,.0f}",
        f"Total operating expenditure (opex): {total_opex:,.0f}",
        f"Operating surplus/deficit: {total_revenue - total_opex:,.0f}",
        f"Uncollected revenue (billed − collected): {max(total_billed - total_revenue, 0):,.0f}",
        f"Cost Recovery Ratio (OCCR): {occr:.1f}% (target ≥{BENCHMARKS['cost_recovery_ratio']}%)",
        f"Revenue Collection Efficiency: {collection_efficiency:.1f}% "
        f"(target ≥{BENCHMARKS['collection_efficiency']}%)",
    ])

    total_production = _sum(production, 'production_m3')
    if total_production:
        lines.append(f"Unit operating cost: {total_opex / total_production:,.2f} per m³ produced")
        if total_revenue:
            lines.append(f"Average revenue per m³ produced: {total_revenue / total_production:,.2f}")

    # --- Staffing ---
    w_staff = _sum(finance, 'w_staff')
    san_staff = _sum(finance, 'san_staff')
    if w_staff or san_staff:
        lines.append(
            f"Staff records: {w_staff:,.0f} water staff and {san_staff:,.0f} sanitation staff "
            f"(summed across reporting periods)"
        )
        if not w_service.empty and 'date' in w_service.columns:
            latest_w = w_service.sort_values('date').drop_duplicates(subset=['country', 'zone'], keep='last')
            connections = _sum(latest_w, 'households')
            if connections:
                lines.append(
                    f"Staff productivity: "
                    f"{calculate_staff_productivity(w_staff + san_staff, connections):.1f} staff per 1,000 "
                    f"connections (target ≤{BENCHMARKS['staff_productivity']})"
                )

    national_latest, national_year = _latest_year_slice(national)
    finance_latest, _ = _latest_year_slice(finance)
    staff_cost = _sum(national_latest, 'staff_cost')
    opex_latest = _sum(finance_latest, 'opex') or total_opex
    if staff_cost and opex_latest:
        lines.append(
            f"Personnel cost as % of O&M: {_pct(staff_cost, opex_latest):.1f}% "
            f"(target ≤{BENCHMARKS['personnel_cost_ratio']}%)"
        )

    # --- Customer-level billing ---
    if not billing.empty and {'billed', 'paid'}.issubset(billing.columns):
        billed_amt = _sum(billing, 'billed')
        paid_amt = _sum(billing, 'paid')
        customers = billing['customer_id'].nunique() if 'customer_id' in billing.columns else 0
        lines.append(
            f"Customer billing records: {len(billing):,} invoices from {customers:,} unique customers"
        )
        lines.append(
            f"Customer-level billing: {billed_amt:,.0f} billed, {paid_amt:,.0f} paid — "
            f"collection rate {_pct(paid_amt, billed_amt):.1f}%"
        )

        risk = identify_payment_risk_customers(billing)
        counts = risk['risk_category'].value_counts()
        lines.append("Customer payment risk segmentation (by share of bill paid):")
        for label in ('High Risk', 'Medium Risk', 'Low Risk'):
            count = int(counts.get(label, 0))
            unpaid = risk.loc[risk['risk_category'] == label, 'unpaid_amount'].sum()
            lines.append(
                f"  · {label}: {count:,} customers ({_pct(count, len(risk)):.1f}%), "
                f"{unpaid:,.0f} unpaid"
            )

        if 'zone' in billing.columns:
            by_zone = get_payment_by_zone(billing).sort_values('collection_rate')
            # With few zones one list covers them all; only split into
            # weakest/strongest when the lists would not just repeat each other.
            if len(by_zone) <= TOP_N:
                lines.append("Collection rate by zone (weakest first):")
                subsets = [by_zone]
            else:
                lines.append("Weakest zones by collection rate:")
                subsets = [by_zone.head(TOP_N)]
            for _, row in subsets[0].iterrows():
                lines.append(
                    f"  · {row['zone']} ({row['country']}): {row['collection_rate']:.1f}% collected, "
                    f"{row['customer_count']:,} customers"
                )
            if len(by_zone) > TOP_N:
                lines.append("Strongest zones by collection rate:")
                for _, row in by_zone.tail(TOP_N).iloc[::-1].iterrows():
                    lines.append(
                        f"  · {row['zone']} ({row['country']}): {row['collection_rate']:.1f}% collected, "
                        f"{row['customer_count']:,} customers"
                    )

        # --- NRW split (finance page: commercial vs physical losses) ---
        if not production.empty and not finance.empty:
            physical = calculate_physical_nrw(production, billing)
            commercial = calculate_commercial_nrw(billing, finance)
            if total_production:
                lines.append(
                    f"NRW breakdown: physical losses {physical:,.0f} m³ "
                    f"({_pct(physical, total_production):.1f}% of production), "
                    f"commercial losses {commercial:,.0f} m³ "
                    f"({_pct(commercial, total_production):.1f}% of production)"
                )

    # --- National accounts ---
    if not national_latest.empty:
        lines.append(f"National sector accounts (reporting year {national_year}):")
        lines.append(f"  · Budget allocated: {_sum(national_latest, 'budget_allocated'):,.0f}")
        lines.append(f"  · Water allocation: {_sum(national_latest, 'wat_allocation'):,.0f}")
        lines.append(f"  · Sanitation allocation: {_sum(national_latest, 'san_allocation'):,.0f}")
        lines.append(f"  · Staff cost: {staff_cost:,.0f}")
        lines.append(f"  · Staff training budget: {_sum(national_latest, 'staff_training_budget'):,.0f}")
        lines.append(f"  · Trained staff: {_sum(national_latest, 'trained_staff'):,.0f}")
        lines.append(
            f"  · Avg. complaint resolution time: {_mean(national_latest, 'complaint_resolution'):.1f} days "
            f"(target ≤{BENCHMARKS['complaint_resolution_time']} days)"
        )
        lines.append(
            f"  · Water treatment plants: {_sum(national_latest, 'registered_wtps'):,.0f} registered, "
            f"{_sum(national_latest, 'inspected_wtps'):,.0f} inspected"
        )
        lines.append(
            f"  · Service providers: {_sum(national_latest, 'total_service_providers'):,.0f} total, "
            f"{_sum(national_latest, 'licensed_service_providers'):,.0f} licensed"
        )
        lines.append(f"  · Asset health score: {_mean(national_latest, 'asset_health'):.1f}")

    return lines


def _country_lines(data, countries):
    """Per-country roll-up of every KPI `calculate_country_kpis` produces."""
    country_kpis = calculate_all_country_kpis(data) or {}
    if not country_kpis:
        return []

    labels = [
        ('total_households', 'Total households', '{:,.0f}'),
        ('water_service_coverage', 'Water service coverage', '{:.1f}%'),
        ('sanitation_coverage', 'Sanitation coverage', '{:.1f}%'),
        ('access_rate_growth', 'Access rate growth (YoY)', '{:+.1f}%'),
        ('nrw', 'NRW', '{:.1f}%'),
        ('service_continuity', 'Service continuity', '{:.1f} hrs/day'),
        ('metering_ratio', 'Metering ratio', '{:.1f}%'),
        ('water_quality', 'Water quality compliance (chlorine)', '{:.1f}%'),
        ('collection_efficiency', 'Collection efficiency', '{:.1f}%'),
        ('cost_recovery_ratio', 'Cost recovery ratio', '{:.1f}%'),
        ('operational_profit_loss', 'Operational profit/loss', '{:,.0f}'),
        ('personnel_cost_ratio', 'Personnel cost as % of O&M', '{:.1f}%'),
        ('staff_productivity', 'Staff productivity', '{:.1f} per 1,000 connections'),
        ('complaints_count', 'Complaints reported', '{:,.0f}'),
        ('complaint_resolution_time', 'Avg. complaint resolution time', '{:.1f} days'),
    ]

    lines = []
    for country, kpis in country_kpis.items():
        lines.append(f"{country}:")
        for key, label, fmt in labels:
            if key in kpis:
                lines.append(f"  · {label}: {fmt.format(kpis[key])}")
    return lines


# --- public API --------------------------------------------------------------

NAVIGATION_NOTES = """## Dashboard Navigation
- The dashboard opens on a landing page of country cards; selecting a country opens that country's dashboard.
- A country dashboard has five tabs: Overview, Production, Service, Access and Finance.
- Overview: the KPI scorecard and AI key insights.
- Production: production volumes, service hours, water sources, seasonal patterns and the water balance.
- Service: water quality tests, metering, complaints and wastewater treatment.
- Access: JMP service ladders for water and sanitation, urban vs rural gaps and priority zones.
- Finance: billing, revenue, opex, cost recovery, customer payment behaviour and NRW loss breakdown.
- Reports (sidebar button "Generate Reports"): exportable country and zone reports.
- The sidebar holds the zone filter, the date range filter and the theme toggle.
- This assistant is available from the floating chat bubble on every tab.
"""


def build_dashboard_context(data, countries_filter=None):
    """
    Build the full cross-domain data context handed to the AI assistant.

    Args:
        data: dict of already-filtered dataframes (as produced by apply_filters).
        countries_filter: optional list of country names for an extra filter.

    Returns:
        A plain-text snapshot of every domain. Never raises — a failing section
        degrades to a short note so the chat keeps working.
    """
    countries = list(countries_filter) if countries_filter else None
    scope = ", ".join(countries) if countries else "All countries"

    sections = [
        f"# DASHBOARD DATA SNAPSHOT\nScope of the current selection: {scope}\n",
        _render_section("Overview KPIs (Overview tab)", _safe(_overview_lines, data, countries)),
        _render_section("Production (Production tab)", _safe(_production_lines, data, countries)),
        _render_section("Service Quality (Service tab)", _safe(_service_lines, data, countries)),
        _render_section("Access & Equity (Access tab)", _safe(_access_lines, data, countries)),
        _render_section("Finance (Finance tab)", _safe(_finance_lines, data, countries)),
        _render_section("Per-Country Breakdown", _safe(_country_lines, data, countries)),
        NAVIGATION_NOTES,
    ]
    return "\n".join(sections)


def _context_signature(data, countries_filter):
    """Cheap fingerprint of the current filter selection + data volume."""
    counts = tuple(
        (name, 0 if df is None else len(df))
        for name, df in sorted((data or {}).items())
    )
    return (tuple(sorted(countries_filter)) if countries_filter else None, counts)


def get_dashboard_context(data, countries_filter=None):
    """
    Cached wrapper around `build_dashboard_context`.

    Streamlit re-runs the whole script on every interaction, and the context
    walks ~720k billing rows, so recomputing it each run would make the chat
    panel sluggish. The result is memoised in session state and only rebuilt
    when the filter selection (or the underlying row counts) actually change.
    """
    signature = _context_signature(data, countries_filter)
    cached = st.session_state.get('_ai_context_cache')
    if cached and cached[0] == signature:
        return cached[1]

    context = build_dashboard_context(data, countries_filter)
    st.session_state['_ai_context_cache'] = (signature, context)
    return context
