"""
Semaglutide LAI · Competitor Intelligence Tracker
Built from primary sources: ADA posters, company press releases, IR decks, investor news.
All data points annotated with evidence level: ✓ Confirmed | ○ Company claim | — Not found
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
import datetime
import time

st.set_page_config(
    page_title="Semaglutide LAI · Competitor Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# EMBEDDED TECHNOLOGY OVERVIEW IMAGE
# ─────────────────────────────────────────────────────────────────────────────
import base64, pathlib, os

def _load_tech_image() -> str:
    """
    Load the formulation-technology overview image as a base64 data URI.
    Looks next to app.py first, then in common Streamlit deployment locations.
    Returns empty string if not found so the app degrades gracefully.
    """
    candidates = [
        pathlib.Path(__file__).parent / "formulation_tech_overview.png",
        pathlib.Path("formulation_tech_overview.png"),
    ]
    for p in candidates:
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

TECH_IMAGE_B64 = _load_tech_image()

def render_tech_image_panel(location: str = "landscape"):
    """
    Render the technology overview image inline.
    location = 'landscape'  → collapsible expander (Screen 1)
    location = 'deepdive'   → prominent panel at top (Screen 2)
    """
    if not TECH_IMAGE_B64:
        st.caption("ℹ️ Place `formulation_tech_overview.png` next to `app.py` to display the mechanism overview.")
        return

    img_tag = f'<img src="data:image/png;base64,{TECH_IMAGE_B64}" style="width:100%; border-radius:10px; border:1px solid #e2e8f0;" />'

    if location == "landscape":
        with st.expander("🧬 Technology mechanism overview — click to expand", expanded=False):
            st.markdown(
                '<p style="font-size:0.82rem; color:#64748b; margin-bottom:0.5rem;">'
                'How each formulation technology solves the weekly dosing problem — '
                'PLGA microsphere, lipid liquid-crystal, small molecule depot, molecular engineering, prodrug, and implant.</p>',
                unsafe_allow_html=True,
            )
            st.markdown(img_tag, unsafe_allow_html=True)
            st.caption("Source: Internal analysis · May 2024 · Based on publicly available information")
    else:  # deepdive — show prominently
        st.markdown("### 🧬 Formulation Technology Mechanism Overview")
        st.markdown(
            '<p class="sub">Visual guide to how each technology category achieves long-acting release — '
            'use this as a reference while reading the comparison table below.</p>',
            unsafe_allow_html=True,
        )
        st.markdown(img_tag, unsafe_allow_html=True)
        st.caption("Source: Internal analysis · May 2024 · Based on publicly available information")
        st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* typography */
h1 { font-size: 1.6rem !important; font-weight: 700 !important; }
h2 { font-size: 1.1rem !important; font-weight: 600 !important; color: #1e293b !important; }
.sub { font-size: 0.85rem; color: #64748b; margin-top: -0.6rem; margin-bottom: 1.2rem; }
/* metric tiles */
.metric-box { background: #f8fafc; border: 1px solid #e2e8f0;
              border-radius: 10px; padding: 0.9rem 1rem; text-align: center; }
.metric-num { font-size: 2rem; font-weight: 700; color: #0f172a; line-height: 1.1; }
.metric-lbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase;
              letter-spacing: 0.07em; margin-top: 2px; }
/* tech badges */
.badge { display:inline-block; padding: 2px 9px; border-radius: 4px;
         font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
.b-plga     { background:#dbeafe; color:#1e40af; }
.b-lipid    { background:#ccfbf1; color:#0f766e; }
.b-smol     { background:#dcfce7; color:#166534; }
.b-mol      { background:#ede9fe; color:#5b21b6; }
.b-prodrug  { background:#fef3c7; color:#92400e; }
.b-implant  { background:#fce7f3; color:#9d174d; }
.b-unknown  { background:#f1f5f9; color:#475569; }
/* stage badges */
.s-preclin  { background:#f1f5f9; color:#475569; }
.s-ind      { background:#fef9c3; color:#854d0e; }
.s-ph1      { background:#dbeafe; color:#1e40af; }
.s-ph2      { background:#ede9fe; color:#5b21b6; }
.s-ph3      { background:#dcfce7; color:#166534; }
.s-unknown  { background:#f1f5f9; color:#94a3b8; }
/* geography */
.geo-kr  { background:#fff1f2; color:#9f1239; }
.geo-gl  { background:#f0fdf4; color:#15803d; }
.geo-cn  { background:#fff7ed; color:#9a3412; }
/* evidence indicators */
.ev-confirmed { color: #16a34a; font-weight: 600; }
.ev-claim     { color: #d97706; font-weight: 600; }
.ev-inferred  { color: #0891b2; font-weight: 600; }
.ev-none      { color: #94a3b8; }
/* news tags */
.tag { display:inline-block; padding:1px 7px; border-radius:3px;
       font-size:0.68rem; font-weight:600; margin-right:4px; }
.t-clinical  { background:#dbeafe; color:#1e40af; }
.t-partner   { background:#dcfce7; color:#166534; }
.t-ind       { background:#fef3c7; color:#92400e; }
.t-conf      { background:#ede9fe; color:#5b21b6; }
.t-ip        { background:#fce7f3; color:#9d174d; }
.t-mfg       { background:#ccfbf1; color:#0f766e; }
.t-company   { background:#f1f5f9; color:#475569; }
/* card */
.card { background:#fff; border:1px solid #e2e8f0; border-radius:12px;
        padding: 1rem 1.1rem; margin-bottom: 0.6rem; }
.card-title { font-weight: 700; font-size: 1rem; margin: 0 0 2px; }
.card-sub   { font-size: 0.8rem; color: #64748b; margin: 0; }
.card-row   { display:flex; gap:6px; flex-wrap:wrap; margin: 6px 0; }
/* data maturity */
.mat-0 { background:#f1f5f9; color:#94a3b8; border-radius:4px; padding:3px 8px; font-size:0.75rem; }
.mat-1 { background:#e0f2fe; color:#0369a1; border-radius:4px; padding:3px 8px; font-size:0.75rem; }
.mat-2 { background:#bfdbfe; color:#1d4ed8; border-radius:4px; padding:3px 8px; font-size:0.75rem; }
.mat-3 { background:#818cf8; color:#fff; border-radius:4px; padding:3px 8px; font-size:0.75rem; }
.mat-4 { background:#4338ca; color:#fff; border-radius:4px; padding:3px 8px; font-size:0.75rem; }
/* scope note */
.scope-note { background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;
              padding: 0.6rem 0.9rem; font-size:0.82rem; color:#166534; margin-bottom:1rem; }
/* tier2 table override */
.tier2-table th { background: #f8fafc !important; font-size: 0.78rem !important; }
.tier2-table td { font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────
COMPETITORS = [
    {
        "id": 0, "company": "Daewoong + Tionlab",
        "product": "Quject®Sphere / CURE®",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Obesity",
        "dosing": "Monthly (target)", "dosing_confirmed": False,
        "stage": "IND Filed", "stage_order": 2,
        "geography": "Korean", "is_baseline": True,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "Suppressed", "burst_ev": "claim",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 0,
        "pk_desc": "No data published",
        "efficacy": "No data published",
        "gi_tolerability": "No data published",
        "in_house_mfg": True,
        "commercial_track": "Partial — Daewoong yes; Tionlab (startup) no",
        "partnership": "Consortium: Daewoong + Tionlab + Daehan New Pharm + Dalim Biotech",
        "trial_id": "IND filed MFDS Apr 2026",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-05-08", "headline": "IND filed with Korean MFDS; first patient dosing targeted within 2026",
             "source": "Korea Herald", "url": "https://www.koreaherald.com/article/10733813", "tag": "IND Filing"},
            {"date": "2026-05-08", "headline": "QJect Sphere (burst control) + CURE (uniform particles) combined for monthly semaglutide LAI",
             "source": "Korea Biomed", "url": "https://www.koreabiomed.com/news/articleView.html?idxno=31574", "tag": "Partnership"},
            {"date": "2026-05-08", "headline": "Four-party consortium model confirmed; parallel microneedle patch program (Daewoong Therapeutics) already in Phase 1",
             "source": "약사공론", "url": "https://www.kpanews.co.kr/news/articleView.html?idxno=534518", "tag": "Company News"},
        ],
        "refs": [
            ("Korea Herald partnership", "https://www.koreaherald.com/article/10733813"),
            ("Korea Biomed pipeline", "https://www.koreabiomed.com/news/articleView.html?idxno=31574"),
            ("약사공론 overview", "https://www.kpanews.co.kr/news/articleView.html?idxno=534518"),
        ],
    },
    {
        "id": 1, "company": "Peptron",
        "product": "PT403 / SmartDepot™",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Diabetes, Obesity",
        "dosing": "Monthly Q4W–Q8W", "dosing_confirmed": False,
        "stage": "Phase 1", "stage_order": 3,
        "geography": "Korean", "is_baseline": False,
        "needle_gauge": "27–30G", "needle_ev": "confirmed",
        "organic_solvent": "None in final product", "solvent_ev": "claim",
        "burst_claim": "No initial burst; lag <3 days", "burst_ev": "claim",
        "titration": "Not required", "titration_ev": "claim",
        "reconstitution": "Required (<10 sec, stays suspended)", "recon_ev": "confirmed",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 2,
        "pk_desc": "Mouse preclinical + 16 healthy adults Phase 1 safety (ADA 2026)",
        "efficacy": "~30% weight loss in mouse at 4 wk; no nausea/vomiting vs weekly sema (Phase 1, 16 subjects)",
        "gi_tolerability": "Favorable vs. weekly semaglutide (ADA 2026, n=16)",
        "in_house_mfg": True,
        "commercial_track": "LEUPONE™ leuprolide SmartDepot — MFDS approval pending 2026",
        "partnership": "Eli Lilly platform tech evaluation agreement (Oct 2024)",
        "trial_id": "IND filed Korea ~Apr 2026",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-06-08", "headline": "ADA 2026: favorable GI tolerability vs. weekly sema in 16 adults; ~30% mouse weight loss at 4 wk",
             "source": "Hankyung", "url": "https://www.hankyung.com/article/202606082409i", "tag": "Clinical Update"},
            {"date": "2025-06-05", "headline": "Eli Lilly–Camurus deal does not conflict with Peptron SmartDepot per Peptron; Lilly-Peptron agreement intact",
             "source": "Korea Biomed", "url": "https://www.koreabiomed.com/news/articleView.html?idxno=27792", "tag": "Partnership"},
            {"date": "2025-01-23", "headline": "Australian patent granted (valid Jun 2042); confirms SmartDepot IP estate for PT403",
             "source": "Korea Biomed", "url": "https://www.koreabiomed.com/news/articleView.html?idxno=26427", "tag": "IP/Patent"},
            {"date": "2024-12-22", "headline": "₩65B cGMP plant approved (Osong); ~10M vials/yr capacity; completion mid-2026",
             "source": "Hankyung", "url": "https://www.hankyung.com/article/2024122226161", "tag": "Manufacturing"},
        ],
        "refs": [
            ("Peptron SmartDepot tech page", "http://www.peptron.com/ds2_2_1.html"),
            ("ADA 2023 poster 781-P", "https://diabetesjournals.org/diabetes/article/72/Supplement_1/781-P/149936/"),
            ("Hankyung ADA 2026", "https://www.hankyung.com/article/202606082409i"),
            ("AU patent — Korea Biomed", "https://www.koreabiomed.com/news/articleView.html?idxno=26427"),
        ],
    },
    {
        "id": 2, "company": "InventageLab",
        "product": "IVL3021 / IVL-DrugFluidics®",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Obesity, Diabetes",
        "dosing": "Monthly (target)", "dosing_confirmed": False,
        "stage": "Preclinical", "stage_order": 1,
        "geography": "Korean", "is_baseline": False,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "Trace (~232 ppm residual — platform data)", "solvent_ev": "confirmed",
        "burst_claim": "No initial burst (platform claim)", "burst_ev": "claim",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "Required (microsphere format)", "recon_ev": "inferred",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 1,
        "pk_desc": "Mini-pig: stable 28-day drug release (ADA 2024 poster 805-P)",
        "efficacy": "Not available (preclinical only)",
        "gi_tolerability": "CEO claim: microfluidic uniform particles 'significantly reduce GI side effects'",
        "in_house_mfg": True,
        "commercial_track": "IVL3004 Ph1 complete; IVL3003 AU Phase 1/2 approved; IVL3013 licensed",
        "partnership": "Yuhan Corp (late-stage dev + commercialization + L/I option); Boehringer Ingelheim (peptide LAI)",
        "trial_id": "IND to MFDS targeted — filing not yet confirmed",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2024-06-01", "headline": "ADA 2024 poster 805-P: semaglutide-releasing long-acting microsphere shows stable 28-day release in mini-pig",
             "source": "ADA 2024", "url": "https://diabetesjournals.org/diabetes/article/73/Supplement_1/805-P/155081/", "tag": "Conference Data"},
            {"date": "2024-01-01", "headline": "Yuhan Corp co-development deal: Yuhan owns late-stage dev, commercialization rights, and license-in option for IVL3021",
             "source": "Biospectator", "url": "https://m.biospectator.com/view/news_view.php?varAtcId=20747", "tag": "Partnership"},
            {"date": "2024-06-01", "headline": "CEO: microfluidic platform controls burst release; claims GI side effects 'significantly reduced' vs conventional microspheres",
             "source": "Edaily", "url": "https://pharm.edaily.co.kr/News/Read?newsId=02102486639019136", "tag": "Company News"},
        ],
        "refs": [
            ("ADA 2024 poster 805-P", "https://diabetesjournals.org/diabetes/article/73/Supplement_1/805-P/155081/"),
            ("Biospectator Yuhan deal", "https://m.biospectator.com/view/news_view.php?varAtcId=20747"),
            ("InventageLab website", "https://inventagelab.com/en"),
        ],
    },
    {
        "id": 3, "company": "Pfizer / Metsera",
        "product": "Berobenatide (PF'3944)",
        "tech_type": "Molecular Engineering (non-depot)", "tech_cat": "molecular_eng",
        "molecule": "Proprietary GLP-1RA peptide", "mechanism": "GLP-1RA",
        "indication": "Obesity (T2D planned)",
        "dosing": "Weekly lead-in → monthly maintenance", "dosing_confirmed": True,
        "stage": "Phase 3", "stage_order": 5,
        "geography": "Global", "is_baseline": False,
        "needle_gauge": "Standard SC", "needle_ev": "none",
        "organic_solvent": "N/A (solution)", "solvent_ev": "confirmed",
        "burst_claim": "N/A (non-depot)", "burst_ev": "na",
        "titration": "Required — weekly lead-in before monthly", "titration_ev": "confirmed",
        "reconstitution": "No (prefilled solution)", "recon_ev": "confirmed",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 4,
        "pk_desc": "Phase 2b (VESPER-3): weight loss continued after weekly→monthly switch; no plateau at 28 wk",
        "efficacy": "Phase 2b: statistically significant weight reduction at 28 wk; details in Pfizer PR (Feb 2026)",
        "gi_tolerability": "Favorable: low GI AEs despite rapid dose escalation (Phase 2b)",
        "in_house_mfg": True,
        "commercial_track": "Multiple FDA-approved products; $7B Metsera acquisition (Nov 2025)",
        "partnership": "$7B Metsera acquisition closed Nov 2025",
        "trial_id": "VESPER-6 (NCT07595549) Phase 3 recruiting",
        "scope": ["all_lai", "full"],
        "news": [
            {"date": "2026-02-03", "headline": "VESPER-3 Ph2b positive: weight loss continued after weekly→monthly switch; no plateau at 28 wk",
             "source": "Pfizer", "url": "https://www.pfizer.com/news/press-release/press-release-detail/pfizers-ultra-long-acting-injectable-glp-1-ra-shows-robust", "tag": "Clinical Update"},
            {"date": "2026-01-01", "headline": "10-trial Phase 3 VESPER program advancing; VESPER-6 (NCT07595549) monthly maintenance trial now recruiting",
             "source": "TipRanks", "url": "https://www.tipranks.com/news/company-announcements/pfizer-steps-up-obesity-push-with-new-phase-3-berobenatide-trial", "tag": "Clinical Update"},
            {"date": "2025-11-01", "headline": "$7 billion Metsera acquisition closed; 20+ obesity pipeline studies planned across VESPER program",
             "source": "Managed Healthcare Exec", "url": "https://www.managedhealthcareexecutive.com/view/pivotal-trial-is-recruiting-for-monthly-glp-1-for-weight-loss-ada-2026", "tag": "Partnership"},
        ],
        "refs": [
            ("Pfizer VESPER-3 press release (Feb 2026)", "https://www.pfizer.com/news/press-release/press-release-detail/pfizers-ultra-long-acting-injectable-glp-1-ra-shows-robust"),
            ("BioPharma Dive", "https://www.biopharmadive.com/news/pfizer-obesity-metsera-phase-2-results-GLP1-monthly-shot/811201/"),
        ],
    },
    {
        "id": 4, "company": "Novo Nordisk",
        "product": "Zenagamtide (Amycretin)",
        "tech_type": "Molecular Engineering (non-depot)", "tech_cat": "molecular_eng",
        "molecule": "Proprietary GLP-1/Amylin dual agonist", "mechanism": "GLP-1 / Amylin dual agonist",
        "indication": "Obesity, T2D",
        "dosing": "Once-weekly SC + oral (not extended interval)", "dosing_confirmed": True,
        "stage": "Phase 3", "stage_order": 5,
        "geography": "Global", "is_baseline": False,
        "needle_gauge": "Standard SC", "needle_ev": "none",
        "organic_solvent": "N/A (solution)", "solvent_ev": "confirmed",
        "burst_claim": "N/A (non-depot)", "burst_ev": "na",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "No (prefilled solution)", "recon_ev": "confirmed",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 4,
        "pk_desc": "Phase 2b complete — T2D: HbA1c −1.71pp, −14.6% weight at 40mg/36 wk",
        "efficacy": "Phase 2b: −1.71pp HbA1c, −14.6% body weight at 36 wk (40mg dose, SC + oral forms)",
        "gi_tolerability": "Does not delay gastric emptying (ECO 2026 poster claim)",
        "in_house_mfg": True,
        "commercial_track": "Ozempic, Wegovy, Rybelsus — blockbuster franchise; CagriSema Phase 3 complete",
        "partnership": "Novo Nordisk internal; also partnered with Ascendis (TransCon GLP-1)",
        "trial_id": "Phase 3 AMAZE starts H2 2026; data ~2028",
        "scope": ["all_lai", "full"],
        "news": [
            {"date": "2026-06-08", "headline": "ADA 2026: Phase 2b — HbA1c −1.71pp, −14.6% weight at 40mg/36wk in T2D (oral + SC both effective)",
             "source": "PR Newswire", "url": "https://www.prnewswire.com/news-releases/novo-nordisk-advances-cardiometabolic-pipeline-302783110.html", "tag": "Clinical Update"},
            {"date": "2026-06-01", "headline": "Phase 3 AMAZE program starting H2 2026; data expected ~2028",
             "source": "Annual Report 2025", "url": "https://annualreport.novonordisk.com/2025/strategic-aspirations/innovation-and-therapeutic-focus.html", "tag": "Clinical Update"},
            {"date": "2026-05-01", "headline": "ECO 2026 poster: unimolecular GLP-1/amylin dual agonist; does not delay gastric emptying — differentiating claim",
             "source": "Novo Science Hub", "url": "https://sciencehub.novonordisk.com/congresses/eco2026/gabe.html", "tag": "Conference Data"},
        ],
        "refs": [
            ("PR Newswire ADA 2026", "https://www.prnewswire.com/news-releases/novo-nordisk-advances-cardiometabolic-pipeline-302783110.html"),
            ("ECO 2026 poster", "https://sciencehub.novonordisk.com/congresses/eco2026/gabe.html"),
            ("Novo Annual Report 2025", "https://annualreport.novonordisk.com/2025/strategic-aspirations/innovation-and-therapeutic-focus.html"),
        ],
    },
    {
        "id": 5, "company": "Camurus",
        "product": "CAM2056 / FluidCrystal®",
        "tech_type": "Lipid Liquid-Crystal Depot", "tech_cat": "depot_lipid",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Overweight, Obesity",
        "dosing": "Monthly (2 biweekly initiation doses first)", "dosing_confirmed": True,
        "stage": "Phase 1b Complete / Ph2 Planned", "stage_order": 3,
        "geography": "Global", "is_baseline": False,
        "needle_gauge": "22–23G (larger — viscous gel)", "needle_ev": "claim",
        "organic_solvent": "~20% organic solvent required", "solvent_ev": "confirmed",
        "burst_claim": "Not specified for CAM2056", "burst_ev": "none",
        "titration": "Required — 2 biweekly doses before monthly", "titration_ev": "confirmed",
        "reconstitution": "No — prefilled liquid, ready to inject", "recon_ev": "confirmed",
        "storage": "Room temp 15–30°C (refrigeration as fallback)", "storage_ev": "confirmed",
        "pk_maturity": 3,
        "pk_desc": "Phase 1b (n=80): −9.3% wt vs −5.2% (weekly sema) at Day 85 (p=0.008); A1c Δ −0.32% (p<0.001)",
        "efficacy": "Phase 1b: −9.3% weight (CAM2056 10mg) vs −5.2% (weekly Wegovy) at Day 85 (p=0.008)",
        "gi_tolerability": "Consistent with weekly sema; highest initiation cohort had more AEs",
        "in_house_mfg": False,
        "commercial_track": "Brixadi® (buprenorphine, FDA 2023); CAM2029 (octreotide, EU+US) — 2 approved FluidCrystal products",
        "partnership": "Eli Lilly $870M FluidCrystal incretins (GIP/GLP-1 + options, Jun 2025); CAM2056 itself Camurus-led",
        "trial_id": "Ph1b complete Nov 2025; Ph2 planned H2 2026 (FDA feedback received)",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2025-11-10", "headline": "Phase 1b positive: monthly CAM2056 comparable to or exceeded weekly Wegovy in weight and A1c at Day 85",
             "source": "Camurus", "url": "https://www.camurus.com/media/press-releases/2025/camurus-reports-positive-topline-results-for-cam2056-semaglutide-monthly-depot/", "tag": "Clinical Update"},
            {"date": "2025-06-01", "headline": "Eli Lilly licenses FluidCrystal for GIP/GLP-1, triple agonist + amylin option — up to $870M (CAM2056 not included in this deal)",
             "source": "Camurus", "url": "https://www.camurus.com/media/press-releases/2025/camurus-and-lilly-enter-collaboration-and-license-agreement-for-long-acting-fluidcrystal-incretins/", "tag": "Partnership"},
            {"date": "2026-04-01", "headline": "Q1 2026 CEO update: FDA feedback received for CAM2056; Phase 2 planned H2 2026; autoinjector pen in development for Phase 3",
             "source": "Camurus CEO message", "url": "https://www.camurus.com/investors/ceo-message/", "tag": "Clinical Update"},
        ],
        "refs": [
            ("Camurus Phase 1b PR Nov 2025", "https://www.camurus.com/media/press-releases/2025/camurus-reports-positive-topline-results-for-cam2056-semaglutide-monthly-depot/"),
            ("Camurus R&D pipeline", "https://www.camurus.com/us/science/rd-pipeline/"),
            ("Medicines Patent Pool — FluidCrystal", "https://lapal.medicinespatentpool.org/technology/fluidcrystal"),
        ],
    },
    {
        "id": 6, "company": "Ascendis Pharma",
        "product": "TransCon GLP-1",
        "tech_type": "Prodrug / Linker Chemistry", "tech_cat": "prodrug",
        "molecule": "GLP-1RA (prodrug-linked)", "mechanism": "GLP-1RA",
        "indication": "Obesity, T2D",
        "dosing": "Monthly (target)", "dosing_confirmed": False,
        "stage": "Preclinical", "stage_order": 1,
        "geography": "Global", "is_baseline": False,
        "needle_gauge": "N/A", "needle_ev": "na",
        "organic_solvent": "N/A (non-depot)", "solvent_ev": "na",
        "burst_claim": "N/A (non-depot)", "burst_ev": "na",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 1,
        "pk_desc": "Preclinical animal proof-of-concept only (as of Nov 2024 deal signing)",
        "efficacy": "Preclinical animal data only; no human data",
        "gi_tolerability": "Not specified",
        "in_house_mfg": True,
        "commercial_track": "Skytrofa® (growth hormone), Yorvipath® (TransCon platform approvals)",
        "partnership": "Novo Nordisk $285M licensing deal (Nov 2024); $100M milestone paid at closing; Novo leads development",
        "trial_id": "No IND/NDA found; Novo-led early development — no 2025/26 update found",
        "scope": ["all_lai", "full"],
        "news": [
            {"date": "2024-11-01", "headline": "Novo Nordisk licenses TransCon GLP-1 for $285M + milestones; $100M paid at closing; Novo leads all development",
             "source": "Ascendis IR", "url": "https://investors.ascendispharma.com/news-releases/news-release-details/ascendis-pharma-and-novo-nordisk-sign-collaboration-development", "tag": "Partnership"},
        ],
        "refs": [
            ("Ascendis IR release (Nov 2024)", "https://investors.ascendispharma.com/news-releases/news-release-details/ascendis-pharma-and-novo-nordisk-sign-collaboration-development"),
            ("SEC Form 6-K", "https://www.sec.gov/Archives/edgar/data/0001612042/000119312524280059/d918920d6k.htm"),
        ],
    },
    {
        "id": 7, "company": "Mapi Pharma",
        "product": "Semaglutide Depot",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Diabetes",
        "dosing": "Every 28 days (target)", "dosing_confirmed": False,
        "stage": "Phase 1/2 Enrolling", "stage_order": 3,
        "geography": "Global (Israel)", "is_baseline": False,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "DCM used in w/o/w manufacturing", "solvent_ev": "confirmed",
        "burst_claim": "—", "burst_ev": "none",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "Required (microsphere)", "recon_ev": "inferred",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 1,
        "pk_desc": "db/db mouse + minipig: 28-day stable plasma conc., HbA1c & glucose data (ADA 2024 poster 2052-LB)",
        "efficacy": "Preclinical: similar efficacy to daily semaglutide API over 28 days in db/db mice",
        "gi_tolerability": "Not specified (no human data)",
        "in_house_mfg": False,
        "commercial_track": "GA Depot (MS) — Phase 3 complete, FDA filing stage (not yet approved)",
        "partnership": "Seeking licensing partners",
        "trial_id": "NCT07563699 — Phase I/II enrolling Jun 2026",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-06-01", "headline": "Mapi at ADA 2026; Phase I/II (NCT07563699) enrolling — first human data expected later in 2026",
             "source": "GlobeNewswire", "url": "https://www.globenewswire.com/news-release/2026/06/01/3304425/0/en/Mapi-Pharma-to-Participate-in-the-ASCO-Annual-Meeting-and-ADA-2026-Scientific-Sessions.html", "tag": "Clinical Update"},
            {"date": "2024-06-01", "headline": "ADA 2024 poster 2052-LB: Q4W depot shows similar efficacy to daily sema API in db/db mice over 28 days",
             "source": "ADA 2024", "url": "https://diabetesjournals.org/diabetes/article/73/Supplement_1/2052-LB/155770/", "tag": "Conference Data"},
        ],
        "refs": [
            ("ADA 2024 poster 2052-LB", "https://diabetesjournals.org/diabetes/article/73/Supplement_1/2052-LB/155770/"),
            ("GlobeNewswire Jun 2026", "https://www.globenewswire.com/news-release/2026/06/01/3304425/0/en/Mapi-Pharma-to-Participate-in-the-ASCO-Annual-Meeting-and-ADA-2026-Scientific-Sessions.html"),
        ],
    },
    {
        "id": 8, "company": "SN Bio",
        "product": "Not identified",
        "tech_type": "Unknown", "tech_cat": "unknown",
        "molecule": "Unknown", "mechanism": "Unknown",
        "indication": "Unknown",
        "dosing": "—", "dosing_confirmed": False,
        "stage": "Unknown", "stage_order": 0,
        "geography": "Korean", "is_baseline": False,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "—", "burst_ev": "none",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 0,
        "pk_desc": "No public data found",
        "efficacy": "No public data found",
        "gi_tolerability": "No public data found",
        "in_house_mfg": False,
        "commercial_track": "No public data found",
        "partnership": "No public data found",
        "trial_id": "No public data found — needs internal source",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [],
        "refs": [],
    },
    {
        "id": 9, "company": "Owl Bio / Kyungdong",
        "product": "AUL009 / Xtina™",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Obesity",
        "dosing": "Monthly", "dosing_confirmed": True,
        "stage": "Phase 1", "stage_order": 3,
        "geography": "Korean", "is_baseline": False,
        "needle_gauge": "27G ultra-fine", "needle_ev": "confirmed",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "Suppressed", "burst_ev": "claim",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 2,
        "pk_desc": "Phase 1 human: single dose stable plasma >30 days in adult males (ADA 2026 late-breaker)",
        "efficacy": "Stable plasma >30 days from single dose — dosing interval confirmed in humans",
        "gi_tolerability": "Not specified beyond burst suppression claim",
        "in_house_mfg": False,
        "commercial_track": "No prior approvals for Owl Bio / Xtina platform",
        "partnership": "Kyungdong Pharm — exclusive co-dev rights (May 2024)",
        "trial_id": "ADA 2026 late-breaker PK/safety data (specific registry # not located)",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-06-08", "headline": "ADA 2026 late-breaker: single dose AUL009 maintained stable plasma >30 days in adult males; 27G ultra-fine needle confirmed",
             "source": "Hankyung", "url": "https://www.hankyung.com/article/202606119708i", "tag": "Clinical Update"},
            {"date": "2024-05-01", "headline": "Kyungdong Pharm exclusive co-development agreement with Owl Bio for AUL009 (Xtina platform)",
             "source": "Bosa", "url": "http://www.bosa.co.kr/news/articleView.html?idxno=2222356", "tag": "Partnership"},
        ],
        "refs": [
            ("Hankyung ADA 2026", "https://www.hankyung.com/article/202606119708i"),
            ("Bosa deal announcement", "http://www.bosa.co.kr/news/articleView.html?idxno=2222356"),
        ],
    },
    {
        "id": 10, "company": "Dongkook Pharma",
        "product": "DK-LADS",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide / Tirzepatide", "mechanism": "GLP-1RA / GLP-1·GIP",
        "indication": "Obesity, Diabetes",
        "dosing": "Monthly–3 months (target)", "dosing_confirmed": False,
        "stage": "Preclinical", "stage_order": 1,
        "geography": "Korean", "is_baseline": False,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "—", "burst_ev": "none",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 0,
        "pk_desc": "No data published",
        "efficacy": "No data published",
        "gi_tolerability": "No data published",
        "in_house_mfg": False,
        "commercial_track": "No depot products commercialized",
        "partnership": "None disclosed",
        "trial_id": "Phase 1 IND targeting 2027",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-05-01", "headline": "DK-LADS: targeting monthly–3 month dosing; evaluating semaglutide AND tirzepatide; Phase 1 IND targeting 2027",
             "source": "약사공론", "url": "https://www.kpanews.co.kr/news/articleView.html?idxno=534518", "tag": "Company News"},
        ],
        "refs": [
            ("약사공론 Korean LAI overview", "https://www.kpanews.co.kr/news/articleView.html?idxno=534518"),
        ],
    },
    # ── NEW ENTRANTS (from broader "long acting injectable" search) ────────────
    {
        "id": 11, "company": "Ascletis Pharma",
        "product": "ASC30 / ULAP™",
        "tech_type": "Small Molecule Depot (SC)", "tech_cat": "depot_smol",
        "molecule": "ASC30 (proprietary small-molecule GLP-1R biased agonist)", "mechanism": "GLP-1R biased agonist (small molecule)",
        "indication": "Obesity",
        "dosing": "Monthly (treatment) / Quarterly (maintenance)", "dosing_confirmed": True,
        "stage": "Phase 2 Complete", "stage_order": 4,
        "geography": "Global (HK-listed)", "is_baseline": False,
        "needle_gauge": "Standard SC (small molecule solution)", "needle_ev": "none",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "—", "burst_ev": "none",
        "titration": "Not required — directly to monthly", "titration_ev": "confirmed",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 4,
        "pk_desc": "Phase 1b: t½ = 46 days (treatment) / 75 days (maintenance) in humans. Phase 2: 7.5% wt loss at wk16.",
        "efficacy": "Phase 2 (NCT06679959, n=65 US): 7.5% placebo-adjusted wt loss at wk16 after 3 monthly doses; maintained 4 months post-dose → quarterly potential",
        "gi_tolerability": "GLP-1 class consistent; no additional safety signals reported (Phase 2)",
        "in_house_mfg": True,
        "commercial_track": "No approved products; ULAP + AISBDD platforms proprietary",
        "partnership": "Ascletis-led; no licensing deal disclosed",
        "trial_id": "NCT06679959 (Phase 2 complete Mar 2026); Phase 3 planning",
        "scope": ["all_lai", "full"],
        "news": [
            {"date": "2026-03-10", "headline": "Phase 2 positive (n=65 US): 7.5% wt loss at wk16; weight maintained 4 months after last dose — quarterly maintenance dosing supported",
             "source": "PR Newswire", "url": "https://www.prnewswire.com/news-releases/ascletis-announces-positive-topline-results-from-us-phase-ii-24-week-study-302709245.html", "tag": "Clinical Update"},
            {"date": "2025-09-09", "headline": "Phase 1b: maintenance formulation t½ = 75 days; treatment t½ = 46 days in humans — longest observed half-life in LAI GLP-1 class",
             "source": "PR Newswire", "url": "https://www.prnewswire.com/news-releases/ascletis-announces-ultra-long-acting-subcutaneous-depot-maintenance-formulation-302550420.html", "tag": "Clinical Update"},
            {"date": "2026-03-10", "headline": "First GLP-1 to achieve class-consistent weight loss with monthly injection WITHOUT requiring weekly lead-in (key differentiator vs Pfizer/Camurus)",
             "source": "Fierce Biotech", "url": "https://www.fiercebiotech.com/biotech/ascletis-posts-phase-2-obesity-data-touts-potential-quarterly-glp-1-dosing", "tag": "Company News"},
        ],
        "refs": [
            ("Phase 2 PR Newswire Mar 2026", "https://www.prnewswire.com/news-releases/ascletis-announces-positive-topline-results-from-us-phase-ii-24-week-study-302709245.html"),
            ("Phase 1b t½ 75 days Sep 2025", "https://www.prnewswire.com/news-releases/ascletis-announces-ultra-long-acting-subcutaneous-depot-maintenance-formulation-302550420.html"),
            ("Fierce Biotech coverage", "https://www.fiercebiotech.com/biotech/ascletis-posts-phase-2-obesity-data-touts-potential-quarterly-glp-1-dosing"),
        ],
    },
    {
        "id": 12, "company": "Samsung Bioepis + G2GBio",
        "product": "Long-acting semaglutide / InnoLamp™",
        "tech_type": "PLGA Microsphere Depot", "tech_cat": "depot_plga",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Obesity",
        "dosing": "Monthly (target)", "dosing_confirmed": False,
        "stage": "Preclinical", "stage_order": 1,
        "geography": "Korean / Global", "is_baseline": False,
        "needle_gauge": "—", "needle_ev": "none",
        "organic_solvent": "—", "solvent_ev": "none",
        "burst_claim": "—", "burst_ev": "none",
        "titration": "—", "titration_ev": "none",
        "reconstitution": "—", "recon_ev": "none",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 0,
        "pk_desc": "No clinical trial data disclosed; preclinical or early development",
        "efficacy": "No data disclosed",
        "gi_tolerability": "No data",
        "in_house_mfg": False,
        "commercial_track": "Samsung Bioepis: major biosimilar commercializer (Hadlima, Byooviz, Opuviz, etc.)",
        "partnership": "Samsung Bioepis full license + Epis NexLab co-dev + Samsung Epis Holdings KRW 20B (~$13.3M) G2GBio convertible bond investment (Mar 2026)",
        "trial_id": "No trial registered; preclinical stage",
        "scope": ["semaglutide_depot", "all_lai", "full"],
        "news": [
            {"date": "2026-03-16", "headline": "Samsung Bioepis + Epis NexLab sign R&D + license agreement with G2GBio; Samsung Epis Holdings invests KRW 20B in G2GBio convertible bonds",
             "source": "Business Wire", "url": "https://www.businesswire.com/news/home/20260316253695/en/", "tag": "Partnership"},
            {"date": "2026-03-16", "headline": "First strategic pivot for Samsung Bioepis from biosimilars into novel biologics following Nov 2025 Samsung Epis Holdings spin-off",
             "source": "Pearce IP", "url": "https://www.pearceip.law/2026/03/16/samsung-bioepis-g2gbio-ink-deal-for-development-of-long-acting-semaglutide/", "tag": "Company News"},
        ],
        "refs": [
            ("Business Wire Mar 2026", "https://www.businesswire.com/news/home/20260316253695/en/"),
            ("Korea Biomed coverage", "https://www.koreabiomed.com/news/articleView.html?idxno=30935"),
            ("Pearce IP analysis", "https://www.pearceip.law/2026/03/16/samsung-bioepis-g2gbio-ink-deal-for-development-of-long-acting-semaglutide/"),
        ],
    },
    {
        "id": 13, "company": "Vivani Medical",
        "product": "NPM-139 / NanoPortal™",
        "tech_type": "Subdermal Implant (6–12 months)", "tech_cat": "implant",
        "molecule": "Semaglutide", "mechanism": "GLP-1RA",
        "indication": "Obesity",
        "dosing": "Once or twice yearly (6–12 month implant)", "dosing_confirmed": False,
        "stage": "Phase 1 Initiated", "stage_order": 3,
        "geography": "Global (Nasdaq: VANI)", "is_baseline": False,
        "needle_gauge": "N/A — minor subdermal insertion procedure", "needle_ev": "confirmed",
        "organic_solvent": "N/A", "solvent_ev": "confirmed",
        "burst_claim": "Continuous steady-state delivery by design (no burst)", "burst_ev": "claim",
        "titration": "N/A", "titration_ev": "confirmed",
        "reconstitution": "N/A", "recon_ev": "confirmed",
        "storage": "—", "storage_ev": "none",
        "pk_maturity": 1,
        "pk_desc": "Preclinical: ~20% sham-adjusted wt loss >6 months from single implant. Phase 1 SLIM-1 initiating mid-2026 (Australia).",
        "efficacy": "Preclinical: ~20% weight loss maintained >6 months from single NPM-139 implant; full-year weight loss shown in latest data",
        "gi_tolerability": "Theoretically improved by smooth/steady GLP-1 delivery (no peak-trough fluctuations) — company claim only",
        "in_house_mfg": True,
        "commercial_track": "LIBERATE-1 (NPM-115 exenatide implant) Phase 1 complete — first-in-human NanoPortal validation",
        "partnership": "Vivani-led; no licensing deal; Nasdaq-listed (VANI), cash funded into mid-2027",
        "trial_id": "SLIM-1 (Phase 1) initiating mid-2026 Australia; top-line data by end 2026; Phase 2 IND targeting 2027",
        "scope": ["all_lai", "full"],
        "news": [
            {"date": "2026-05-13", "headline": "Q1 2026: SLIM-1 Phase 1 on track for mid-2026 initiation in Australia; top-line data by year-end; $28M cash into mid-2027",
             "source": "GlobeNewswire / SEC", "url": "https://www.stocktitan.net/news/VANI/vivani-medical-reports-first-quarter-2026-financial-results-and-8130ax03avhv.html", "tag": "Clinical Update"},
            {"date": "2026-03-26", "headline": "Preclinical update: single NPM-139 implant → >20% sham-adjusted wt loss maintained for a full year",
             "source": "SEC 8-K", "url": "https://www.sec.gov/Archives/edgar/data/1266806/000175392626000550/ex991_1.htm", "tag": "Conference Data"},
            {"date": "2025-08-05", "headline": "LIBERATE-1 Phase 1 complete (exenatide implant NPM-115) — NanoPortal safety + tolerability validated in humans for first time",
             "source": "Vivani IR", "url": "https://investors.vivani.com/investors/news-events/press-releases/detail/198/vivani-medical-announces-rapid-advancement-of-npm-139-a", "tag": "Clinical Update"},
        ],
        "refs": [
            ("Vivani Q1 2026 results", "https://www.stocktitan.net/news/VANI/vivani-medical-reports-first-quarter-2026-financial-results-and-8130ax03avhv.html"),
            ("SEC 8-K LIBERATE-1 & NPM-139 Mar 2026", "https://www.sec.gov/Archives/edgar/data/1266806/000175392626000550/ex991_1.htm"),
            ("Vivani NPM-139 update Sep 2025", "https://www.globenewswire.com/news-release/2025/09/04/3144519/0/en/Vivani-Medical-Provides-Update-on-Clinical-Development-Plans-for-NPM-139-Semaglutide-Implant-for-Chronic-Weight-Management.html"),
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
TECH_COLOR = {
    "depot_plga":   "#3b82f6",
    "depot_lipid":  "#14b8a6",
    "depot_smol":   "#22c55e",
    "molecular_eng":"#8b5cf6",
    "prodrug":      "#f59e0b",
    "implant":      "#ec4899",
    "unknown":      "#94a3b8",
}
TECH_BADGE = {
    "depot_plga":   ("b-plga",  "PLGA Depot"),
    "depot_lipid":  ("b-lipid", "Lipid Depot"),
    "depot_smol":   ("b-smol",  "Small Mol Depot"),
    "molecular_eng":("b-mol",   "Molecular Eng."),
    "prodrug":      ("b-prodrug","Prodrug/Linker"),
    "implant":      ("b-implant","Implant"),
    "unknown":      ("b-unknown","Unknown"),
}
STAGE_BADGE = {
    "Unknown":                          ("s-unknown", "Unknown"),
    "Preclinical":                      ("s-preclin", "Preclinical"),
    "IND Filed":                        ("s-ind",     "IND Filed"),
    "Phase 1":                          ("s-ph1",     "Phase 1"),
    "Phase 1b Complete / Ph2 Planned":  ("s-ph1",     "Ph1b ✓ / Ph2 →"),
    "Phase 1 Initiated":                ("s-ph1",     "Phase 1 →"),
    "Phase 1/2 Enrolling":              ("s-ph1",     "Ph1/2 Enrolling"),
    "Phase 2 Complete":                 ("s-ph2",     "Phase 2 ✓"),
    "Phase 3":                          ("s-ph3",     "Phase 3"),
}
TAG_CSS = {
    "Clinical Update":  "t-clinical",
    "Partnership":      "t-partner",
    "IND Filing":       "t-ind",
    "Conference Data":  "t-conf",
    "IP/Patent":        "t-ip",
    "Manufacturing":    "t-mfg",
    "Company News":     "t-company",
}
EV_HTML = {
    "confirmed":  '<span class="ev-confirmed">✓ Confirmed</span>',
    "claim":      '<span class="ev-claim">○ Company claim</span>',
    "inferred":   '<span class="ev-inferred">~ Inferred</span>',
    "na":         '<span class="ev-none">N/A</span>',
    "none":       '<span class="ev-none">— Not found</span>',
}
PK_LABELS = ["No data", "Preclinical animal", "Early human / Ph1", "Phase 1b / Ph2 partial", "Phase 2b / Ph3"]

GEO_BADGE = {
    "Korean":           ("geo-kr", "🇰🇷 Korean"),
    "Global":           ("geo-gl", "🌐 Global"),
    "Global (HK-listed)":("geo-gl","🌐 Global"),
    "Global (Israel)":  ("geo-gl", "🌐 Global"),
    "Global (Nasdaq: VANI)":("geo-gl","🌐 Global"),
    "Korean / Global":  ("geo-kr", "🇰🇷/🌐"),
}

SCOPE_LABELS = {
    "semaglutide_depot": "Semaglutide depot only (PLGA / Lipid)",
    "full": "Full landscape — all LAI technologies",
}

def badge(text, css_class):
    return f'<span class="badge {css_class}">{text}</span>'

def tag_html(tag):
    css = TAG_CSS.get(tag, "t-company")
    return f'<span class="tag {css}">{tag}</span>'

def filter_competitors(scope):
    if scope == "full":
        # full captures everything (old all_lai + full)
        return [c for c in COMPETITORS if "all_lai" in c["scope"] or "full" in c["scope"]]
    return [c for c in COMPETITORS if scope in c["scope"]]

def df_from_competitors(comps):
    rows = []
    for c in comps:
        rows.append({
            "Company": c["company"],
            "Product": c["product"],
            "Tech Type": c["tech_type"],
            "Mechanism": c["mechanism"],
            "Indication": c["indication"],
            "Dosing": c["dosing"],
            "Stage": c["stage"],
            "Geography": c["geography"],
            "In-house Mfg": "Yes" if c["in_house_mfg"] else "No",
            "Partnership": c["partnership"],
            "Trial ID": c["trial_id"],
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 1 — LANDSCAPE (REDESIGNED DASHBOARD)
# ─────────────────────────────────────────────────────────────────────────────
def render_landscape(comps):
    # ── derived metrics ────────────────────────────────────────────────────
    baseline = next((c for c in comps if c.get("is_baseline")), None)
    competitors = [c for c in comps if not c.get("is_baseline")]
    n_total = len(comps)
    n_human = sum(1 for c in comps if c["pk_maturity"] >= 2)
    n_korean = sum(1 for c in comps if "Korean" in c["geography"])
    n_global = n_total - n_korean
    top_rival = max(competitors, key=lambda c: c["stage_order"], default=None)

    # recent alerts = news items dated 2026 across all competitors
    all_news = []
    for c in comps:
        for n in c.get("news", []):
            all_news.append({**n, "company": c["company"], "tech_cat": c["tech_cat"], "is_baseline": c.get("is_baseline", False)})
    all_news.sort(key=lambda x: x.get("date", ""), reverse=True)
    recent_news = [n for n in all_news if n.get("date", "")[:4] >= "2026"]
    alert_count = len(recent_news)

    # ── top bar ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1.2rem; flex-wrap:wrap; gap:8px;">
      <div>
        <h1 style="font-size:1.4rem; font-weight:700; margin:0; color:#0f172a;">
          Semaglutide LAI · Competitor Intelligence
        </h1>
        <p class="sub" style="margin-top:4px;">
          GLP-1RA &amp; Amylin-class long-acting injectable landscape · June 2026 · {n_total} programs tracked
        </p>
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span style="background:#dcfce7; color:#166534; font-size:0.75rem; padding:4px 12px; border-radius:20px; font-weight:600;">
          ★ Quject®Sphere — our program
        </span>
        <span style="background:#fef3c7; color:#92400e; font-size:0.75rem; padding:4px 12px; border-radius:20px; font-weight:600;">
          🔔 {alert_count} updates in 2026
        </span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── five metric cards ──────────────────────────────────────────────────
    our_stage = baseline["stage"] if baseline else "—"
    top_rival_name = top_rival["company"].split("/")[0].strip() if top_rival else "—"
    top_rival_stage = top_rival["stage"] if top_rival else "—"

    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (str(n_total), "Programs tracked", f"1 ours · {n_total - 1} competitors"),
        (str(n_human), "Have human data", "pk_maturity ≥ phase 1"),
        (str(n_korean), "Korean players", f"{n_global} global / mixed"),
        (top_rival_name, "Most advanced rival", top_rival_stage),
        (our_stage, "Our stage", "Quject®Sphere / CURE®"),
    ]
    for col, (num, label, sub) in zip([c1, c2, c3, c4, c5], metrics):
        col.markdown(
            f'<div class="metric-box">'
            f'<div class="metric-num" style="font-size:1.3rem;">{num}</div>'
            f'<div class="metric-lbl">{label}</div>'
            f'<div style="font-size:0.7rem; color:#94a3b8; margin-top:3px;">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── race chart ─────────────────────────────────────────────────────────
    st.markdown("### 🏁 The race — development stage across all programs")
    st.markdown('<p class="sub">Sorted by advancement · bar length proportional to stage · hover for details</p>', unsafe_allow_html=True)

    # sort descending by stage_order; baseline always shown in its true position
    sorted_comps = sorted(comps, key=lambda c: (-c["stage_order"], 0 if c.get("is_baseline") else 1))
    max_stage = max((c["stage_order"] for c in comps), default=1) or 1

    BAR_COLORS = {
        "baseline": "#1D9E75",
        "ph2plus":  "#7F77DD",
        "ph1":      "#378ADD",
        "ind":      "#EF9F27",
        "pre":      "#B4B2A9",
    }

    def bar_color(c):
        if c.get("is_baseline"):
            return BAR_COLORS["baseline"]
        so = c["stage_order"]
        if so >= 4: return BAR_COLORS["ph2plus"]
        if so == 3: return BAR_COLORS["ph1"]
        if so == 2: return BAR_COLORS["ind"]
        return BAR_COLORS["pre"]

    def row_label(c):
        if c.get("is_baseline"):
            return "Quject®Sphere (Daewoong + Tionlab) ★"
        return c["company"]

    labels = [row_label(c) for c in sorted_comps]
    bar_vals = [max(c["stage_order"] / max_stage, 0.04) for c in sorted_comps]
    colors = [bar_color(c) for c in sorted_comps]
    pk_texts = [
        (c["pk_desc"][:65] + "…" if len(c.get("pk_desc", "")) > 65 else c.get("pk_desc", "—"))
        for c in sorted_comps
    ]
    hover_texts = [
        f"<b>{row_label(c)}</b><br>"
        f"Product: {c['product']}<br>"
        f"Stage: {c['stage']}<br>"
        f"Tech: {c['tech_type']}<br>"
        f"Dosing: {c['dosing']}<br>"
        f"PK: {c['pk_desc']}"
        for c in sorted_comps
    ]

    fig_race = go.Figure()
    fig_race.add_trace(go.Bar(
        x=bar_vals,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=pk_texts,
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(size=10, color="white"),
        hovertext=hover_texts,
        hoverinfo="text",
        cliponaxis=False,
    ))

    # legend annotations
    legend_items = [
        ("Our program", BAR_COLORS["baseline"]),
        ("Phase 2+", BAR_COLORS["ph2plus"]),
        ("Phase 1", BAR_COLORS["ph1"]),
        ("IND filed", BAR_COLORS["ind"]),
        ("Preclinical", BAR_COLORS["pre"]),
    ]
    annotations = []
    for i, (lbl, col) in enumerate(legend_items):
        annotations.append(dict(
            x=0.02 + i * 0.19, y=1.06,
            xref="paper", yref="paper",
            text=f"<span style='color:{col}'>■</span> {lbl}",
            showarrow=False,
            font=dict(size=11),
        ))

    fig_race.update_layout(
        height=max(420, len(sorted_comps) * 38 + 80),
        xaxis=dict(visible=False, range=[0, 1.02]),
        yaxis=dict(automargin=True, tickfont=dict(size=11)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=20, t=60, b=20),
        font=dict(family="Inter, sans-serif", size=11),
        annotations=annotations,
        bargap=0.35,
    )
    st.plotly_chart(fig_race, use_container_width=True)

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # ── two-column section: technology + evidence ──────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Technology landscape")
        st.markdown('<p class="sub">Programs by platform type and geography</p>', unsafe_allow_html=True)

        # count by tech_cat
        from collections import Counter
        tech_counts = Counter(c["tech_cat"] for c in comps)
        tech_order = ["depot_plga", "depot_lipid", "depot_smol", "molecular_eng", "prodrug", "implant", "unknown"]
        for tc in tech_order:
            count = tech_counts.get(tc, 0)
            if count == 0:
                continue
            badge_cls, badge_lbl = TECH_BADGE.get(tc, ("b-unknown", tc))
            color = TECH_COLOR.get(tc, "#94a3b8")
            companies_in = [c["company"].split("/")[0].strip() for c in comps if c["tech_cat"] == tc]
            pct = int(count / n_total * 100)
            st.markdown(
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">'
                f'<span class="badge {badge_cls}">{badge_lbl}</span>'
                f'<span style="font-size:0.75rem; color:#64748b;">{count} program{"s" if count > 1 else ""}</span>'
                f'</div>'
                f'<div style="background:#f1f5f9; border-radius:4px; height:8px; overflow:hidden;">'
                f'<div style="background:{color}; width:{pct}%; height:100%; border-radius:4px;"></div>'
                f'</div>'
                f'<div style="font-size:0.68rem; color:#94a3b8; margin-top:2px;">{" · ".join(companies_in[:4])}{"…" if len(companies_in) > 4 else ""}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # geography split
        st.markdown(
            f'<div style="margin-top:12px; padding:10px 12px; background:#f8fafc; border-radius:8px;">'
            f'<div style="font-size:0.72rem; color:#64748b; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:6px;">Geography split</div>'
            f'<div style="display:flex; gap:4px; border-radius:4px; overflow:hidden; height:10px;">'
            f'<div style="flex:{n_korean}; background:#dbeafe;" title="{n_korean} Korean"></div>'
            f'<div style="flex:{n_global}; background:#dcfce7;" title="{n_global} Global"></div>'
            f'</div>'
            f'<div style="display:flex; gap:16px; margin-top:5px; font-size:0.72rem; color:#64748b;">'
            f'<span>🇰🇷 {n_korean} Korean</span><span>🌐 {n_global} Global / mixed</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown("### Evidence maturity")
        st.markdown('<p class="sub">PK data depth — how much do we know about each program?</p>', unsafe_allow_html=True)

        ev_sorted = sorted(comps, key=lambda c: (-c["pk_maturity"], 0 if c.get("is_baseline") else 1))
        pk_badge_colors = ["#f1f5f9", "#dbeafe", "#ede9fe", "#dcfce7", "#166534"]
        pk_text_colors  = ["#94a3b8", "#1e40af", "#5b21b6", "#166534", "#ffffff"]

        for c in ev_sorted:
            mat = c["pk_maturity"]
            lbl = PK_LABELS[mat] if mat < len(PK_LABELS) else "—"
            bg  = pk_badge_colors[mat]
            tc  = pk_text_colors[mat]
            name = "Quject®Sphere ★" if c.get("is_baseline") else c["company"].split("/")[0].strip()
            name_color = "#166534" if c.get("is_baseline") else "#0f172a"
            pk_short = c["pk_desc"][:70] + "…" if len(c.get("pk_desc", "")) > 70 else c.get("pk_desc", "—")
            st.markdown(
                f'<div style="display:flex; align-items:flex-start; gap:10px; padding:7px 0; border-bottom:1px solid #f1f5f9;">'
                f'<div style="flex:1; min-width:0;">'
                f'<div style="font-size:0.8rem; font-weight:600; color:{name_color}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{name}</div>'
                f'<div style="font-size:0.68rem; color:#94a3b8; margin-top:1px;">{pk_short}</div>'
                f'</div>'
                f'<span style="background:{bg}; color:{tc}; font-size:0.68rem; padding:2px 8px; border-radius:10px; white-space:nowrap; flex-shrink:0; font-weight:600;">{lbl}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # ── two-column section: differentiator table + news feed ──────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Key differentiators")
        st.markdown('<p class="sub">Programs with human data only (pk_maturity ≥ 2)</p>', unsafe_allow_html=True)

        human_comps = sorted(
            [c for c in comps if c["pk_maturity"] >= 2],
            key=lambda c: (-c["pk_maturity"], 0 if c.get("is_baseline") else 1),
        )

        # table header
        th_style = "padding:6px 8px; font-size:0.72rem; color:#64748b; font-weight:600; text-align:left; border-bottom:2px solid #e2e8f0; white-space:nowrap;"
        td_style = "padding:6px 8px; font-size:0.75rem; border-bottom:1px solid #f1f5f9; vertical-align:top;"
        td_style_our = "padding:6px 8px; font-size:0.75rem; border-bottom:1px solid #f1f5f9; vertical-align:top; background:#f0fdf4;"

        table = f'<div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse;">'
        table += f'<thead><tr><th style="{th_style}">Program</th><th style="{th_style}">Dosing</th><th style="{th_style}">Titration?</th><th style="{th_style}">Needle</th></tr></thead><tbody>'

        for c in human_comps:
            is_ours = c.get("is_baseline")
            td = td_style_our if is_ours else td_style
            name = "Quject®Sphere ★" if is_ours else c["company"].split("/")[0].strip()
            name_col = "#166534" if is_ours else "#0f172a"
            titration = c.get("titration", "—")
            tit_ev = c.get("titration_ev", "none")
            ev_label = {"confirmed": "✓", "claim": "○", "inferred": "~", "none": "—", "na": "N/A"}.get(tit_ev, "—")
            ev_col = {"confirmed": "#16a34a", "claim": "#d97706", "inferred": "#0891b2"}.get(tit_ev, "#94a3b8")
            needle = c.get("needle_gauge", "—")
            dosing = c.get("dosing", "—")
            # extract t½ hint from pk_desc
            pk = c.get("pk_desc", "")
            t_half = "—"
            if "t½" in pk or "t1/2" in pk.lower():
                for part in pk.replace(",", " ").split():
                    if "day" in part.lower() or "d" == part[-1:].lower():
                        t_half = part
                        break
            table += (
                f'<tr>'
                f'<td style="{td} font-weight:600; color:{name_col};">{name}</td>'
                f'<td style="{td}">{dosing}</td>'
                f'<td style="{td}"><span style="color:{ev_col}; font-weight:600;">{ev_label}</span> {titration}</td>'
                f'<td style="{td}">{needle}</td>'
                f'</tr>'
            )

        table += "</tbody></table></div>"
        st.markdown(table, unsafe_allow_html=True)

    with col_b:
        st.markdown("### Latest intelligence")
        st.markdown('<p class="sub">Most recent updates across all programs</p>', unsafe_allow_html=True)

        feed_items = all_news[:8]
        for item in feed_items:
            tc = item.get("tech_cat", "unknown")
            dot_color = "#1D9E75" if item.get("is_baseline") else TECH_COLOR.get(tc, "#94a3b8")
            tag = item.get("tag", "Update")
            tag_css = TAG_CSS.get(tag, "t-company")
            headline = item["headline"][:90] + "…" if len(item["headline"]) > 90 else item["headline"]
            company_short = item["company"].split("/")[0].strip()
            if item.get("is_baseline"):
                company_short = "Quject®Sphere ★"
            url = item.get("url", "#")
            st.markdown(
                f'<div style="display:flex; gap:8px; padding:8px 0; border-bottom:1px solid #f1f5f9;">'
                f'<div style="width:7px; height:7px; border-radius:50%; background:{dot_color}; margin-top:5px; flex-shrink:0;"></div>'
                f'<div style="flex:1; min-width:0;">'
                f'<div style="font-size:0.78rem; color:#0f172a; line-height:1.4;">'
                f'<a href="{url}" target="_blank" style="color:#0f172a; text-decoration:none;">{headline}</a>'
                f'</div>'
                f'<div style="font-size:0.68rem; color:#94a3b8; margin-top:2px;">'
                f'{company_short} · {item.get("source", "")} · {item.get("date", "")} '
                f'<span class="tag {tag_css}">{tag}</span>'
                f'</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── export row ─────────────────────────────────────────────────────────
    df_export = pd.DataFrame([{
        "Company": c["company"], "Product": c["product"],
        "Stage": c["stage"], "Tech Type": c["tech_type"],
        "Mechanism": c["mechanism"], "Dosing": c["dosing"],
        "Geography": c["geography"], "PK Maturity": PK_LABELS[c["pk_maturity"]],
        "PK Description": c["pk_desc"], "Efficacy": c["efficacy"],
        "Partnership": c["partnership"],
    } for c in comps])
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")

    exp1, exp2, exp3 = st.columns([1, 1, 4])
    with exp1:
        st.download_button(
            "⬇️ Export CSV",
            data=csv_bytes,
            file_name=f"semaglutide_landscape_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="dl_landscape_csv",
        )
    with exp2:
        render_tech_image_panel(location="landscape")


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 2 — TIER 2 DEPOT DEEP-DIVE
# ─────────────────────────────────────────────────────────────────────────────
def render_tier2(comps):
    st.markdown("## 🔬 Screen 2 — Formulation Deep-Dive (Depot Players Only)")
    st.markdown('<p class="sub">Applies only to encapsulation/depot technologies. Non-depot (molecular engineering, prodrug, implant) shown separately.</p>', unsafe_allow_html=True)

    # ── technology mechanism overview image ─────────────────────────────────
    render_tech_image_panel(location="deepdive")

    depot_cats = {"depot_plga", "depot_lipid", "depot_smol"}
    depot = [c for c in comps if c["tech_cat"] in depot_cats]
    non_depot = [c for c in comps if c["tech_cat"] not in depot_cats and c["tech_cat"] != "unknown"]

    if not depot:
        st.warning("No depot players visible in current scope.")
        return

    # evidence legend
    st.markdown("""
    <div style="display:flex; gap:1.5rem; font-size:0.8rem; margin-bottom:1rem; flex-wrap:wrap;">
    <span class="ev-confirmed">✓ Confirmed from source</span>
    <span class="ev-claim">○ Company claim (unverified)</span>
    <span class="ev-inferred">~ Inferred from platform</span>
    <span class="ev-none">— Not found in public sources</span>
    </div>
    """, unsafe_allow_html=True)

    # build table rows
    FIELDS = [
        ("Formulation type", "tech_type", None),
        ("Needle gauge", "needle_gauge", "needle_ev"),
        ("Organic solvent use", "organic_solvent", "solvent_ev"),
        ("Reconstitution required", "reconstitution", "recon_ev"),
        ("Storage condition", "storage", "storage_ev"),
        ("Initial burst claim", "burst_claim", "burst_ev"),
        ("Titration required", "titration", "titration_ev"),
        ("Confirmed dosing interval", "dosing", None),
        ("PK data available", "pk_desc", None),
        ("Efficacy data", "efficacy", None),
        ("GI tolerability", "gi_tolerability", None),
        ("In-house manufacturing", "in_house_mfg", None),
        ("Platform commercialization track", "commercial_track", None),
        ("Key partnership", "partnership", None),
        ("Clinical trial ID", "trial_id", None),
    ]

    company_names = [c["company"] for c in depot]

    table_html = f"""
    <div style="overflow-x:auto;">
    <table style="border-collapse:collapse; font-size:0.78rem; width:100%; min-width:800px;">
    <thead><tr style="background:#f8fafc;">
    <th style="padding:8px 10px; border:1px solid #e2e8f0; white-space:nowrap; min-width:160px;">Category</th>
    """
    for c in depot:
        bc, bl = TECH_BADGE.get(c["tech_cat"], ("b-unknown", c["tech_type"]))
        star = " ★" if c.get("is_baseline") else ""
        table_html += f'<th style="padding:8px 10px; border:1px solid #e2e8f0; min-width:140px;">{c["company"]}{star}<br><span class="badge {bc}" style="font-size:0.65rem;">{bl}</span></th>'
    table_html += "</tr></thead><tbody>"

    ev_color = {
        "confirmed": "#f0fdf4",
        "claim":     "#fffbeb",
        "inferred":  "#eff6ff",
        "none":      "#fafafa",
        "na":        "#fafafa",
    }

    for label, field, ev_field in FIELDS:
        table_html += f'<tr><td style="padding:7px 10px; border:1px solid #e2e8f0; font-weight:600; background:#f8fafc; white-space:nowrap;">{label}</td>'
        for c in depot:
            val = c.get(field, "—")
            ev = c.get(ev_field, "none") if ev_field else "none"
            bg = ev_color.get(ev, "#fafafa")
            if field == "in_house_mfg":
                val = "✓ Yes" if val else "✗ No / CMO"
            ev_html = EV_HTML.get(ev, "") if ev_field else ""
            table_html += f'<td style="padding:7px 10px; border:1px solid #e2e8f0; background:{bg}; vertical-align:top;">{val}<br><span style="font-size:0.68rem;">{ev_html}</span></td>'
        table_html += "</tr>"

    table_html += "</tbody></table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

    if non_depot:
        st.markdown("---")
        st.markdown("### Non-depot players in scope")
        st.caption("Needle gauge, organic solvent, burst, and reconstitution are not applicable for these technologies.")
        nd_data = {
            "Company": [c["company"] for c in non_depot],
            "Product": [c["product"] for c in non_depot],
            "Technology": [c["tech_type"] for c in non_depot],
            "Stage": [c["stage"] for c in non_depot],
            "Titration": [c["titration"] for c in non_depot],
            "Storage": [c["storage"] for c in non_depot],
            "PK data": [c["pk_desc"] for c in non_depot],
            "GI tolerability": [c["gi_tolerability"] for c in non_depot],
        }
        st.dataframe(pd.DataFrame(nd_data), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 3 — COMPETITOR PROFILE CARDS
# ─────────────────────────────────────────────────────────────────────────────
def render_cards(comps):
    st.markdown("## 🃏 Screen 3 — Competitor Profile Cards")
    st.markdown('<p class="sub">Filter by technology, stage, or geography · expand each card for recent news and sources</p>', unsafe_allow_html=True)

    # filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        tech_options = sorted(set(c["tech_type"] for c in comps))
        sel_tech = st.multiselect("Technology type", tech_options, default=tech_options, key="card_tech")
    with fc2:
        stage_options = sorted(set(c["stage"] for c in comps))
        sel_stage = st.multiselect("Stage", stage_options, default=stage_options, key="card_stage")
    with fc3:
        geo_options = sorted(set(c["geography"] for c in comps))
        sel_geo = st.multiselect("Geography", geo_options, default=geo_options, key="card_geo")

    filtered = [c for c in comps
                if c["tech_type"] in sel_tech
                and c["stage"] in sel_stage
                and c["geography"] in sel_geo]

    if not filtered:
        st.warning("No competitors match the selected filters.")
        return

    st.caption(f"Showing {len(filtered)} of {len(comps)} competitors")

    cols = st.columns(2)
    for i, c in enumerate(filtered):
        col = cols[i % 2]
        with col:
            tc = c["tech_cat"]
            bc, bl = TECH_BADGE.get(tc, ("b-unknown", c["tech_type"]))
            sc, sl = STAGE_BADGE.get(c["stage"], ("s-unknown", c["stage"]))
            geo_cls, geo_lbl = GEO_BADGE.get(c["geography"], ("geo-gl", c["geography"]))
            star_note = " <small>★ Baseline</small>" if c.get("is_baseline") else ""
            pk_mat = c["pk_maturity"]
            pk_bar = "█" * pk_mat + "░" * (4 - pk_mat)

            card_content = f"""
            <div class="card">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <p class="card-title">{c['company']}{star_note}</p>
                  <p class="card-sub">{c['product']}</p>
                </div>
                <div style="text-align:right; font-size:0.72rem; color:#64748b;">
                  ID {c['id']:02d}
                </div>
              </div>
              <div class="card-row">
                {badge(bl, bc)}
                {badge(sl, sc)}
                {badge(geo_lbl, geo_cls)}
              </div>
              <table style="width:100%; font-size:0.78rem; border-collapse:collapse; margin-top:6px;">
                <tr><td style="color:#64748b; padding:3px 0; width:130px;">Mechanism</td><td style="padding:3px 0;">{c['mechanism']}</td></tr>
                <tr><td style="color:#64748b; padding:3px 0;">Indication</td><td style="padding:3px 0;">{c['indication']}</td></tr>
                <tr><td style="color:#64748b; padding:3px 0;">Dosing interval</td><td style="padding:3px 0;">{c['dosing']} {'✓' if c['dosing_confirmed'] else '<span style="color:#d97706; font-size:0.7rem;">target</span>'}</td></tr>
                <tr><td style="color:#64748b; padding:3px 0;">PK maturity</td>
                    <td style="padding:3px 0; font-family:monospace;">{pk_bar} <span style="font-size:0.7rem; color:#64748b;">{PK_LABELS[pk_mat]}</span></td></tr>
                <tr><td style="color:#64748b; padding:3px 0; vertical-align:top;">Partnership</td><td style="padding:3px 0;">{c['partnership'][:90]}{'…' if len(c['partnership'])>90 else ''}</td></tr>
                <tr><td style="color:#64748b; padding:3px 0;">Trial / status</td><td style="padding:3px 0;">{c['trial_id']}</td></tr>
              </table>
            </div>
            """
            st.markdown(card_content, unsafe_allow_html=True)

            # news expander
            if c["news"]:
                with st.expander(f"📰 Recent news ({len(c['news'])} items)"):
                    for item in sorted(c["news"], key=lambda x: x["date"], reverse=True):
                        st.markdown(
                            f'{tag_html(item["tag"])} '
                            f'<span style="font-size:0.75rem; color:#94a3b8;">{item["date"]}</span>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**{item['headline']}**")
                        st.markdown(f"[{item['source']} ↗]({item['url']})")
                        st.markdown("---")
            else:
                with st.expander("📰 Recent news (0 items)"):
                    st.caption("No public news found — needs internal source.")

            # sources expander
            if c["refs"]:
                with st.expander(f"📚 Sources ({len(c['refs'])})"):
                    for label, url in c["refs"]:
                        st.markdown(f"- [{label}]({url})")


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 4 — PK & EFFICACY SNAPSHOT
# ─────────────────────────────────────────────────────────────────────────────
def render_pk(comps):
    st.markdown("## 📊 Screen 4 — PK & Efficacy Snapshot")
    st.markdown('<p class="sub">Data maturity matrix — how strong is the clinical evidence for each competitor?</p>', unsafe_allow_html=True)

    st.info(
        "⚠️ PK curve charts are not shown because quantitative plasma concentration-time values "
        "have not been released in publicly accessible documents for any player. "
        "Values are only inside conference posters. Once you retrieve those, curves can be built here. "
        "This screen instead shows a **data maturity matrix** — what evidence type exists across key dimensions."
    )

    # maturity heatmap
    DIMENSIONS = ["PK stability data", "Weight loss efficacy", "GI tolerability", "Burst suppression", "Needle gauge confirmed"]

    def score_dim(c, dim):
        if dim == "PK stability data":
            return c["pk_maturity"]
        if dim == "Weight loss efficacy":
            if "No data" in c["efficacy"] or "No public" in c["efficacy"]:
                return 0
            if "Preclinical" in c["efficacy"] or "preclinical" in c["efficacy"]:
                return 1
            if "Phase 1" in c["efficacy"] or ">30-day" in c["efficacy"] or "human" in c["efficacy"].lower():
                return 2
            if "Phase 2" in c["efficacy"] or "Phase 1b" in c["efficacy"]:
                return 3
            if "Phase 3" in c["efficacy"]:
                return 4
            return 1
        if dim == "GI tolerability":
            v = c["gi_tolerability"]
            if v in ("No data published", "No data", "Not specified", "No public data found"):
                return 0
            if "preclinical" in v.lower() or "claim" in v.lower() or "theoretically" in v.lower():
                return 1
            if "Phase 1" in v or "n=16" in v or "adult" in v.lower():
                return 2
            if "Phase 1b" in v or "Phase 2" in v:
                return 3
            return 1
        if dim == "Burst suppression":
            ev = c.get("burst_ev", "none")
            if ev == "none" or ev == "na":
                return 0
            if ev == "claim":
                return 1
            if ev == "inferred":
                return 2
            if ev == "confirmed":
                return 3
            return 0
        if dim == "Needle gauge confirmed":
            ev = c.get("needle_ev", "none")
            if ev == "none":
                return 0
            if ev == "na":
                return 2  # N/A but confirmed
            if ev == "claim":
                return 1
            if ev == "confirmed":
                return 4
            return 0
        return 0

    z = []
    for dim in DIMENSIONS:
        row = [score_dim(c, dim) for c in comps]
        z.append(row)

    comp_names = [c["company"] for c in comps]
    colorscale = [
        [0.0,  "#f1f5f9"],
        [0.25, "#bfdbfe"],
        [0.5,  "#818cf8"],
        [0.75, "#4338ca"],
        [1.0,  "#1e1b4b"],
    ]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=comp_names,
        y=DIMENSIONS,
        colorscale=colorscale,
        zmin=0, zmax=4,
        colorbar=dict(
            title="Evidence strength",
            tickvals=[0, 1, 2, 3, 4],
            ticktext=["None", "Preclinical/<br>Claim", "Early human", "Ph1b/Ph2", "Ph2b/Ph3"],
            lenmode="fraction", len=0.7,
        ),
        text=[[str(v) for v in row] for row in z],
        hovertemplate="<b>%{y}</b><br>%{x}: Score %{z}<extra></extra>",
    ))
    fig.update_layout(
        height=380,
        xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
        yaxis=dict(tickfont=dict(size=11)),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=180, r=20, t=30, b=120),
        font=dict(family="Inter, sans-serif", size=11),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Efficacy & tolerability summary (text)")
    for c in comps:
        if c["pk_maturity"] >= 1:
            with st.expander(f"**{c['company']}** — {PK_LABELS[c['pk_maturity']]}"):
                st.markdown(f"**PK data:** {c['pk_desc']}")
                st.markdown(f"**Efficacy:** {c['efficacy']}")
                st.markdown(f"**GI tolerability:** {c['gi_tolerability']}")
                if c["refs"]:
                    st.markdown("**Sources:**")
                    for label, url in c["refs"]:
                        st.markdown(f"- [{label}]({url})")

    # poster links
    st.markdown("---")
    st.markdown("### 📋 Where to retrieve actual PK curve values")
    st.markdown("""
    | Company | Poster / Source | Direct link |
    |---|---|---|
    | Camurus CAM2056 | Q4 2025 investor presentation | [Camurus presentations](https://www.camurus.com/investors/presentations/) |
    | Owl Bio AUL009 | ADA 2026 late-breaker abstract | [ADA 2026 abstracts](https://diabetesjournals.org/diabetes/issue/75/Supplement_1) |
    | Peptron PT403 | ADA 2026 poster | [ADA 2026 abstracts](https://diabetesjournals.org/diabetes/issue/75/Supplement_1) |
    | Mapi Pharma | ADA 2024 poster 2052-LB | [ADA 2024 2052-LB](https://diabetesjournals.org/diabetes/article/73/Supplement_1/2052-LB/155770/) |
    | InventageLab | ADA 2024 poster 805-P | [ADA 2024 805-P](https://diabetesjournals.org/diabetes/article/73/Supplement_1/805-P/155081/) |
    | Ascletis ASC30 | Phase 1b / Phase 2 PRs | [Phase 2 PR](https://www.prnewswire.com/news-releases/ascletis-announces-positive-topline-results-from-us-phase-ii-24-week-study-302709245.html) |
    """)


# ─────────────────────────────────────────────────────────────────────────────
# LIVE SEARCH HELPERS
# ─────────────────────────────────────────────────────────────────────────────

# Default keyword presets for semaglutide LAI competitive intelligence
DEFAULT_KEYWORDS = [
    "long acting injectable semaglutide",
    "semaglutide monthly injection pipeline",
    "Korea semaglutide long acting",
    "GLP-1 depot formulation clinical trial",
    "semaglutide PLGA microsphere",
    "once monthly GLP-1 obesity pipeline",
]

def news_card_html(title, url, source, published, description="", color="#3b82f6", tag="Live Update"):
    """Render a live-fetched news item in the same card style as static items."""
    tag_css = TAG_CSS.get(tag, "t-company")
    desc_html = f'<p style="margin:3px 0 2px; font-size:0.8rem; color:#475569;">{description[:200]}{"…" if len(description)>200 else ""}</p>' if description else ""
    return f"""
    <div style="border-left:4px solid {color}; padding:0.55rem 0.9rem;
                margin:0.4rem 0; background:#fafafa; border-radius:0 6px 6px 0;">
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:3px;">
        <span class="tag {tag_css}">{tag}</span>
        <span style="font-size:0.72rem; background:#e0f2fe; color:#0369a1; padding:1px 7px;
               border-radius:3px; font-weight:600;">🔴 Live</span>
        <span style="font-size:0.75rem; color:#94a3b8;">{published}</span>
      </div>
      <p style="margin:2px 0; font-size:0.85rem; color:#1e293b; font-weight:600;">{title}</p>
      {desc_html}
      <a href="{url}" target="_blank" style="font-size:0.75rem; color:#3b82f6; text-decoration:none;">
        {source} ↗
      </a>
    </div>"""

@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)  # cache 7 days
def fetch_gnews(keyword: str, max_results: int = 5):
    """
    Fetch from GNews API (free tier: 100 req/day, no key needed for basic queries).
    Falls back gracefully if unavailable.
    """
    try:
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": keyword,
            "lang": "en",
            "country": "any",
            "max": max_results,
            "sortby": "publishedAt",
            "apikey": "demo",          # replace with real key for production
        }
        r = requests.get(url, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            return [
                {
                    "title": a.get("title", ""),
                    "url": a.get("url", "#"),
                    "source": a.get("source", {}).get("name", "News"),
                    "published": a.get("publishedAt", "")[:10],
                    "description": a.get("description", ""),
                }
                for a in articles if a.get("title")
            ]
    except Exception:
        pass
    return []

@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)
def fetch_pubmed(keyword: str, max_results: int = 5):
    """
    Fetch from PubMed E-utilities API (free, no key required).
    Returns recent abstracts matching the keyword.
    """
    results = []
    try:
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": keyword,
            "retmax": max_results,
            "sort": "date",
            "retmode": "json",
        }
        r = requests.get(search_url, params=params, timeout=8)
        if r.status_code != 200:
            return results
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return results

        # fetch summaries
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        s = requests.get(summary_url, params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"}, timeout=8)
        if s.status_code != 200:
            return results
        uids = s.json().get("result", {}).get("uids", [])
        result_data = s.json().get("result", {})
        for uid in uids:
            rec = result_data.get(uid, {})
            title = rec.get("title", "")
            pub_date = rec.get("pubdate", "")[:10]
            source = rec.get("fulljournalname", rec.get("source", "PubMed"))
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            if title:
                results.append({
                    "title": title,
                    "url": url,
                    "source": source,
                    "published": pub_date,
                    "description": "",
                })
    except Exception:
        pass
    return results

@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)
def fetch_clinicaltrials(keyword: str, max_results: int = 5):
    """Fetch from ClinicalTrials.gov v2 API (free, no key)."""
    results = []
    try:
        url = "https://clinicaltrials.gov/api/v2/studies"
        params = {
            "query.term": keyword,
            "pageSize": max_results,
            "sort": "LastUpdatePostDate:desc",
            "format": "json",
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return results
        studies = r.json().get("studies", [])
        for s in studies:
            proto = s.get("protocolSection", {})
            ident = proto.get("identificationModule", {})
            status = proto.get("statusModule", {})
            desc = proto.get("descriptionModule", {})
            nct = ident.get("nctId", "")
            title = ident.get("briefTitle", "")
            phase = status.get("phases", [""])[0] if status.get("phases") else ""
            overall_status = status.get("overallStatus", "")
            sponsor = proto.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "")
            last_update = status.get("lastUpdatePostDateStruct", {}).get("date", "")
            brief_desc = desc.get("briefSummary", "")[:200]
            if title and nct:
                results.append({
                    "title": f"[{phase or 'Study'}] {title} — {overall_status}",
                    "url": f"https://clinicaltrials.gov/study/{nct}",
                    "source": f"ClinicalTrials.gov · {sponsor}",
                    "published": last_update,
                    "description": brief_desc,
                })
    except Exception:
        pass
    return results


# ─────────────────────────────────────────────────────────────────────────────
# SCREEN 5 — INTELLIGENCE FEED
# ─────────────────────────────────────────────────────────────────────────────
def render_feed(comps):
    st.markdown("## 📡 Screen 5 — Strategic Intelligence Feed")
    st.markdown('<p class="sub">Static curated items + live weekly search from PubMed, ClinicalTrials.gov, and news · newest first</p>', unsafe_allow_html=True)

    # ── TAB layout ────────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["📋 Curated Intelligence", "🔍 Live Weekly Search"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — STATIC CURATED FEED (original)
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        all_news = []
        for c in comps:
            for item in c["news"]:
                all_news.append({
                    "date": item["date"],
                    "company": c["company"],
                    "stage": c["stage"],
                    "headline": item["headline"],
                    "source": item["source"],
                    "url": item["url"],
                    "tag": item["tag"],
                    "tech_cat": c["tech_cat"],
                })
        all_news.sort(key=lambda x: x["date"], reverse=True)

        ff1, ff2 = st.columns(2)
        with ff1:
            all_tags = sorted(set(n["tag"] for n in all_news))
            sel_tags = st.multiselect("Filter by type", all_tags, default=all_tags, key="feed_tag")
        with ff2:
            all_co = sorted(set(n["company"] for n in all_news))
            sel_co = st.multiselect("Filter by company", all_co, default=all_co, key="feed_co")

        filtered_news = [n for n in all_news if n["tag"] in sel_tags and n["company"] in sel_co]
        st.caption(f"{len(filtered_news)} curated items · manually verified from primary sources")

        for item in filtered_news:
            tc = item["tech_cat"]
            color = TECH_COLOR.get(tc, "#94a3b8")
            tag_css = TAG_CSS.get(item["tag"], "t-company")
            st.markdown(
                f"""<div style="border-left:4px solid {color}; padding:0.55rem 0.9rem;
                               margin:0.4rem 0; background:#fafafa; border-radius:0 6px 6px 0;">
                  <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:3px;">
                    <span class="tag {tag_css}">{item['tag']}</span>
                    <span style="font-weight:600; font-size:0.82rem;">{item['company']}</span>
                    <span style="font-size:0.75rem; color:#94a3b8;">{item['date']}</span>
                  </div>
                  <p style="margin:2px 0; font-size:0.83rem; color:#1e293b;">{item['headline']}</p>
                  <a href="{item['url']}" target="_blank" style="font-size:0.75rem; color:#3b82f6; text-decoration:none;">
                    {item['source']} ↗
                  </a>
                </div>""",
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — LIVE WEEKLY SEARCH
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🔍 Live Intelligence Search")
        st.markdown(
            '<p class="sub">Pulls real-time results from PubMed (research), ClinicalTrials.gov (trials), '
            'and news. Results cached for 7 days — click Refresh to force update.</p>',
            unsafe_allow_html=True,
        )

        # ── keyword manager ──────────────────────────────────────────────────
        st.markdown("#### Keyword presets")
        st.caption("Pre-loaded keywords for semaglutide LAI competitive intelligence. Add or remove as needed.")

        if "search_keywords" not in st.session_state:
            st.session_state.search_keywords = DEFAULT_KEYWORDS.copy()

        # display editable keyword chips
        kw_cols = st.columns([3, 1])
        with kw_cols[0]:
            new_kw = st.text_input("Add a keyword", placeholder='e.g. "semaglutide PLGA Phase 2"', key="new_kw_input")
        with kw_cols[1]:
            st.markdown("<div style='margin-top:1.7rem;'>", unsafe_allow_html=True)
            if st.button("➕ Add", key="add_kw"):
                if new_kw.strip() and new_kw.strip() not in st.session_state.search_keywords:
                    st.session_state.search_keywords.append(new_kw.strip())
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # show active keywords with remove buttons
        active_keywords = []
        kw_display_cols = st.columns(3)
        for i, kw in enumerate(st.session_state.search_keywords):
            col = kw_display_cols[i % 3]
            with col:
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(
                        f'<div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; '
                        f'padding:4px 10px; font-size:0.78rem; color:#1e40af; margin-bottom:4px;">'
                        f'🔎 {kw}</div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    if st.button("✕", key=f"rm_kw_{i}", help=f"Remove '{kw}'"):
                        st.session_state.search_keywords.pop(i)
                        st.rerun()
            active_keywords.append(kw)

        st.markdown("---")

        # ── source selector ───────────────────────────────────────────────────
        src_col1, src_col2, src_col3 = st.columns(3)
        with src_col1:
            use_pubmed = st.checkbox("📚 PubMed (research papers)", value=True, key="use_pubmed")
        with src_col2:
            use_ct = st.checkbox("🏥 ClinicalTrials.gov (trials)", value=True, key="use_ct")
        with src_col3:
            use_news = st.checkbox("📰 News (GNews API)", value=False, key="use_news",
                                   help="Requires a GNews API key in the code. Free tier: gnews.io")

        results_per_kw = st.slider("Results per keyword per source", 2, 10, 4, key="results_per_kw")

        # ── search trigger ────────────────────────────────────────────────────
        b1, b2 = st.columns([2, 1])
        with b1:
            run_search = st.button("🚀 Search Now", type="primary", key="run_live_search",
                                   help="Results are cached for 7 days. Click Refresh to force new fetch.")
        with b2:
            if st.button("🔄 Refresh Cache", key="clear_cache_btn"):
                fetch_pubmed.clear()
                fetch_clinicaltrials.clear()
                fetch_gnews.clear()
                st.success("Cache cleared — next search will pull fresh data.")

        # ── last fetched timestamp ────────────────────────────────────────────
        if "last_fetched" in st.session_state:
            st.caption(f"Last fetched: {st.session_state.last_fetched}")

        # ── run search ────────────────────────────────────────────────────────
        if run_search or ("live_results" in st.session_state and st.session_state.live_results):
            if run_search:
                # force new fetch by running (cache handles dedup automatically)
                all_live = []
                progress = st.progress(0, text="Fetching data…")
                total_steps = len(active_keywords) * ((1 if use_pubmed else 0) + (1 if use_ct else 0) + (1 if use_news else 0))
                step = 0

                for kw in active_keywords:
                    if use_pubmed:
                        items = fetch_pubmed(kw, results_per_kw)
                        for item in items:
                            item["keyword"] = kw
                            item["source_type"] = "pubmed"
                        all_live.extend(items)
                        step += 1
                        progress.progress(step / max(total_steps, 1), text=f"PubMed: {kw[:40]}…")

                    if use_ct:
                        items = fetch_clinicaltrials(kw, results_per_kw)
                        for item in items:
                            item["keyword"] = kw
                            item["source_type"] = "clinicaltrials"
                        all_live.extend(items)
                        step += 1
                        progress.progress(step / max(total_steps, 1), text=f"ClinicalTrials: {kw[:35]}…")

                    if use_news:
                        items = fetch_gnews(kw, results_per_kw)
                        for item in items:
                            item["keyword"] = kw
                            item["source_type"] = "news"
                        all_live.extend(items)
                        step += 1
                        progress.progress(step / max(total_steps, 1), text=f"News: {kw[:45]}…")

                progress.empty()

                # deduplicate by URL
                seen_urls = set()
                deduped = []
                for item in all_live:
                    if item["url"] not in seen_urls:
                        seen_urls.add(item["url"])
                        deduped.append(item)

                # sort by date desc
                deduped.sort(key=lambda x: x.get("published", ""), reverse=True)

                st.session_state.live_results = deduped
                st.session_state.last_fetched = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            # ── display results ───────────────────────────────────────────────
            live_results = st.session_state.get("live_results", [])
            if not live_results:
                st.warning("No results returned. Check your keywords or API availability.")
            else:
                # filter controls
                rf1, rf2 = st.columns(2)
                with rf1:
                    source_type_opts = sorted(set(r.get("source_type", "other") for r in live_results))
                    src_label_map = {"pubmed": "📚 PubMed", "clinicaltrials": "🏥 ClinicalTrials", "news": "📰 News"}
                    sel_src = st.multiselect(
                        "Filter by source",
                        source_type_opts,
                        default=source_type_opts,
                        format_func=lambda x: src_label_map.get(x, x),
                        key="live_src_filter",
                    )
                with rf2:
                    kw_opts = sorted(set(r.get("keyword", "") for r in live_results))
                    sel_kws = st.multiselect("Filter by keyword", kw_opts, default=kw_opts, key="live_kw_filter")

                filtered_live = [r for r in live_results
                                 if r.get("source_type") in sel_src and r.get("keyword") in sel_kws]

                st.caption(f"Showing {len(filtered_live)} of {len(live_results)} live results · deduplicated across all keywords")

                # source type → color and tag
                src_color = {"pubmed": "#8b5cf6", "clinicaltrials": "#22c55e", "news": "#f59e0b"}
                src_tag   = {"pubmed": "Research", "clinicaltrials": "Clinical Trial", "news": "News"}

                for item in filtered_live:
                    stype = item.get("source_type", "other")
                    color = src_color.get(stype, "#94a3b8")
                    tag = src_tag.get(stype, "Live Update")
                    st.markdown(
                        news_card_html(
                            title=item["title"],
                            url=item["url"],
                            source=item["source"],
                            published=item.get("published", ""),
                            description=item.get("description", ""),
                            color=color,
                            tag=tag,
                        ),
                        unsafe_allow_html=True,
                    )

                # ── export ────────────────────────────────────────────────────
                if filtered_live:
                    df_export = pd.DataFrame(filtered_live)[["published", "title", "source", "url", "keyword", "source_type"]]
                    csv = df_export.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "⬇️ Download results as CSV",
                        data=csv,
                        file_name=f"semaglutide_intel_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        key="dl_live_csv",
                    )
        else:
            st.info("👆 Click **Search Now** to pull the latest data from PubMed, ClinicalTrials.gov, and (optionally) News. Results are cached for 7 days.")


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR & ROUTING
# ─────────────────────────────────────────────────────────────────────────────
def main():
    with st.sidebar:
        st.markdown("### 💊 Semaglutide LAI Tracker")
        st.markdown("*Competitor Intelligence — v1.0*")
        st.markdown("**Last updated:** June 2026")
        st.markdown("---")

        comps = [c for c in COMPETITORS if "all_lai" in c["scope"] or "full" in c["scope"]]
        st.markdown(
            f'<div class="scope-note">Full landscape · <b>{len(comps)}</b> programs tracked</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### 📑 Navigation")
        screen = st.radio(
            "Go to",
            options=["1 — Landscape", "2 — Formulation deep-dive", "3 — Competitor cards", "4 — PK & Efficacy", "5 — Intelligence feed"],
            key="screen",
        )

        st.markdown("---")
        st.markdown("#### ⚡ Evidence key")
        st.markdown("""
        <div style="font-size:0.78rem; line-height:2;">
        <span class="ev-confirmed">✓</span> Confirmed from source<br>
        <span class="ev-claim">○</span> Company claim only<br>
        <span class="ev-inferred">~</span> Inferred from platform<br>
        <span class="ev-none">—</span> Not found in public sources
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Data gathered from: ADA posters, company IRs, press releases, investor news. No data fabricated or extrapolated.")

    # ── header ───────────────────────────────────────────────────────────
    st.markdown(
        '<h1>💊 Semaglutide LAI · Competitor Intelligence</h1>'
        '<p class="sub">GLP-1RA & Amylin-class long-acting injectable competitive landscape · June 2026</p>',
        unsafe_allow_html=True,
    )

    if screen.startswith("1"):
        render_landscape(comps)
    elif screen.startswith("2"):
        render_tier2(comps)
    elif screen.startswith("3"):
        render_cards(comps)
    elif screen.startswith("4"):
        render_pk(comps)
    elif screen.startswith("5"):
        render_feed(comps)


if __name__ == "__main__":
    main()
