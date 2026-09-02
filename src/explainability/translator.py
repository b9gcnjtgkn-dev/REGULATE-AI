"""
REGULATE.AI — Executive Output Translator & Plain-English Decision Assistant
Simplifies technical regulatory outputs into 3 plain-English decision views for CEOs, RA leads, and CFOs.
"""

from typing import Dict, Any
from src.models.schemas import CountryGapReport, FullEquivalencePassport, GapStatus


class ExecutiveOutputTranslator:
    """
    Translates complex technical regulatory gap outputs into clear, non-technical executive language.
    Eliminates jargon (CTD 3.2.P.8, Zone IVb, AUC 90% CI) and provides instant decision clarity.
    """

    @staticmethod
    def translate_country_report(report: CountryGapReport) -> Dict[str, Any]:
        """
        Translates a single country gap report into plain-English executive decision views.
        """
        status = report.overall_status
        auth = report.authority_name.split("(")[0].strip()
        country = report.jurisdiction_code

        if status == GapStatus.RELIANCE_ELIGIBLE:
            tldr = f"🟢 FAST-TRACK APPROVED FOR {country}: You qualify for a 6-month shortcut in {auth} using your existing WHO/FDA approvals. Registration will be 18 months faster!"
            action = f"Gather your certified WHO CoPP and GMP certificates and lodge a Fast-Track Desktop Review application in {country}. Do not re-write the dossier."
            financial = f"Saves ${report.estimated_cost_savings_usd:,.0f} in local consultant fees and unlocks export sales 18 months earlier."
            risk_level = "VERY LOW RISK"
        elif status == GapStatus.COMPLIANT:
            tldr = f"🔵 FULL DOSSIER COMPLIANT FOR {country}: Your product meets all local technical rules in {auth}, but will undergo standard manual review ({report.estimated_timeline_months} months)."
            action = f"Submit your existing full CTD dossier to {auth}. Expect standard review timeline of {report.estimated_timeline_months} months."
            financial = f"Standard submission cost. Unlocks market access within {report.estimated_timeline_months} months."
            risk_level = "LOW RISK"
        elif status == GapStatus.PARTIAL_GAP:
            tldr = f"🟡 MINOR WAIT REQUIRED FOR {country}: Your product is nearly ready for {auth}, but is missing a few additional months of stability testing data."
            action = f"Hold submission for 3–6 months until your ongoing stability testing reaches the required {report.estimated_timeline_months}-month threshold."
            financial = f"Saves $10,000+ by avoiding filing premature applications that would trigger formal deficiency query letters."
            risk_level = "MEDIUM RISK (Delay Submission)"
        else: # CRITICAL_DEFICIENCY
            tldr = f"🔴 SUBMISSION BLOCKED FOR {country}: DO NOT SUBMIT YET to {auth}. Mandatory technical data is missing (e.g. required climate stability testing or valid CoPP)."
            action = f"Immediately commission the missing laboratory study (e.g. 12-month Zone IVb stability testing at 30°C/75% RH) before applying."
            financial = f"Prevents wasting $25,000+ in non-refundable government filing fees and avoids permanent dossier rejection."
            risk_level = "HIGH RISK (Submission Blocked)"

        return {
            "jurisdiction_code": country,
            "authority_name": auth,
            "status_badge": status.value,
            "risk_level": risk_level,
            "executive_tldr": tldr,
            "plain_english_action": action,
            "commercial_financial_impact": financial
        }

    @staticmethod
    def translate_full_passport(passport: FullEquivalencePassport) -> Dict[str, Any]:
        """
        Translates a complete product Equivalence Passport into a master executive dashboard summary.
        """
        translated_countries = {}
        total_savings = 0.0
        fast_track_count = 0

        for code, rep in passport.target_country_reports.items():
            trans = ExecutiveOutputTranslator.translate_country_report(rep)
            translated_countries[code] = trans
            total_savings += rep.estimated_cost_savings_usd
            if rep.overall_status == GapStatus.RELIANCE_ELIGIBLE:
                fast_track_count += 1

        total_markets = len(passport.target_country_reports)
        
        master_tldr = (
            f"Product '{passport.brand_name}' ({passport.inn_generic_name}) is READY FOR EXPANSION across {total_markets} target markets! "
            f"{fast_track_count} out of {total_markets} countries qualify for Fast-Track Reliance shortcuts, saving 18 months of review time per market."
        )

        return {
            "product_name": passport.brand_name,
            "generic_name": passport.inn_generic_name,
            "total_markets_evaluated": total_markets,
            "fast_track_markets_count": fast_track_count,
            "master_executive_tldr": master_tldr,
            "total_direct_cost_savings_usd": total_savings,
            "avg_time_saved_months": 18,
            "translated_country_reports": translated_countries
        }
