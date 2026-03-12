"""
Wapas.Health — Dental Follow-up Intelligence
Demo script: reads patient CSV, outputs a WhatsApp-ready follow-up list.
"""

import csv
from datetime import date, datetime

# --- Configuration ---

CLINIC_NAME = "Dr. Sharma's Dental Clinic"

# Expected return windows per procedure (in days)
RETURN_WINDOWS = {
    "Root Canal":              180,   # 6 months — follow-up crown/check
    "Cleaning":                180,   # 6 months — routine cycle
    "Orthodontic Adjustment":  45,    # Every 6 weeks
    "Filling":                 365,   # Annual check
    "Crown":                   365,   # Annual check
}

# Estimated revenue per procedure (₹)
REVENUE = {
    "Root Canal":              5500,
    "Cleaning":                1200,
    "Orthodontic Adjustment":  2000,
    "Filling":                 1800,
    "Crown":                   8000,
}

# Urgency scoring weight (higher = more urgent)
URGENCY_WEIGHT = {
    "Root Canal":              5,
    "Orthodontic Adjustment":  4,
    "Crown":                   3,
    "Filling":                 2,
    "Cleaning":                1,
}

# --- Core Logic ---

def days_overdue(last_visit_str, procedure):
    last_visit = datetime.strptime(last_visit_str, "%Y-%m-%d").date()
    expected_return = RETURN_WINDOWS.get(procedure, 180)
    days_since = (date.today() - last_visit).days
    overdue_by = days_since - expected_return
    return days_since, overdue_by

def urgency_score(overdue_by, procedure):
    weight = URGENCY_WEIGHT.get(procedure, 1)
    return overdue_by * weight

def load_patients(filepath):
    patients = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            patients.append(row)
    return patients

def analyse(patients):
    results = []
    for p in patients:
        procedure = p["Procedure"].strip()
        days_since, overdue_by = days_overdue(p["Last Visit"].strip(), procedure)

        if overdue_by <= 0:
            continue  # Not yet overdue, skip

        score = urgency_score(overdue_by, procedure)
        revenue = REVENUE.get(procedure, 1000)

        results.append({
            "name":       p["Name"].strip(),
            "phone":      p["Phone"].strip(),
            "procedure":  procedure,
            "days_since": days_since,
            "overdue_by": overdue_by,
            "revenue":    revenue,
            "score":      score,
        })

    # Sort by urgency score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def format_whatsapp(clinic_name, patients):
    today = date.today().strftime("%d %b %Y")
    total_revenue = sum(p["revenue"] for p in patients)

    lines = []
    lines.append(f"🦷 *Wapas Weekly Follow-Up List*")
    lines.append(f"*{clinic_name}* — {today}")
    lines.append("─" * 36)

    for i, p in enumerate(patients, 1):
        overdue_str = f"{p['overdue_by']} days overdue" if p['overdue_by'] < 60 else f"{p['overdue_by'] // 30} months overdue"
        lines.append(
            f"\n*{i}. {p['name']}*\n"
            f"   Procedure: {p['procedure']}\n"
            f"   Last visit: {p['days_since']} days ago ({overdue_str})\n"
            f"   Est. revenue: ₹{p['revenue']:,}\n"
            f"   📞 {p['phone']}"
        )

    lines.append("\n" + "─" * 36)
    lines.append(f"💰 *Total recoverable this week: ₹{total_revenue:,}*")
    lines.append(f"👆 Forward this list to your receptionist.")
    lines.append("\n_Powered by Wapas.Health_")

    return "\n".join(lines)

# --- Main ---

if __name__ == "__main__":
    import sys

    filepath = sys.argv[1] if len(sys.argv) > 1 else "patients.csv"

    print(f"\nLoading patients from: {filepath}\n")
    patients = load_patients(filepath)
    overdue = analyse(patients)

    if not overdue:
        print("✅ No overdue patients found. Everyone is on track!")
    else:
        print(f"Found {len(overdue)} overdue patients.\n")
        message = format_whatsapp(CLINIC_NAME, overdue)
        print("=" * 40)
        print(message)
        print("=" * 40)
