"""
REGULATE.AI — Data Schemas & Domain Models (Standard Dataclasses)
Defines structured data types for eCTD dossiers, regulatory rules, knowledge graph entities, and dossier gap outputs.
Uses standard library dataclasses for 100% zero-dependency execution.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


class ClimateZone(str, Enum):
    ZONE_I = "Zone I"
    ZONE_II = "Zone II (Subtropical)"
    ZONE_III = "Zone III (Hot/Dry)"
    ZONE_IVA = "Zone IVa (Hot/Humid)"
    ZONE_IVB = "Zone IVb (Hot/Very Humid)"


class ReferenceAuthority(str, Enum):
    US_FDA = "US FDA"
    EU_EMA = "EU EMA"
    WHO_PQ = "WHO Prequalification"
    JAPAN_PMDA = "Japan PMDA"
    UK_MHRA = "UK MHRA"
    SWISS_MEDIC = "Swissmedic"
    INDIA_CDSCO = "India CDSCO"
    NONE = "None"


@dataclass
class APISpecification:
    name: str
    dmf_number: Optional[str]
    cep_status: bool
    manufacturer_name: str
    manufacturing_site_country: str
    pharmacopoeia_grade: str = "USP/Ph. Eur"


@dataclass
class StabilityStudy:
    climate_zone: ClimateZone
    temperature_celsius: int
    relative_humidity_percent: int
    duration_months: int
    container_closure_system: str
    batch_numbers: List[str] = field(default_factory=list)
    assay_percent: float = 100.0
    degradation_products_compliant: bool = True


@dataclass
class BioequivalenceStudy:
    conducted: bool
    bcs_class_waiver: bool
    reference_innovator_product: str
    reference_product_country: str
    cmax_90_ci_lower: float = 85.0
    cmax_90_ci_upper: float = 115.0
    auc_90_ci_lower: float = 88.0
    auc_90_ci_upper: float = 112.0


@dataclass
class CertificatesProfile:
    copp_available: bool
    copp_issuing_country: str = "India"
    who_gmp_certified: bool = True
    last_gmp_inspection_date: str = "2025-06-15"


@dataclass
class DossierProfile:
    product_id: str
    brand_name: str
    inn_generic_name: str
    dosage_form: str
    strength: str
    applicant_name: str
    applicant_country: str
    reference_approvals: List[ReferenceAuthority]
    api_spec: APISpecification
    stability_data: List[StabilityStudy]
    be_study: BioequivalenceStudy
    certificates: CertificatesProfile


@dataclass
class NMRATargetRule:
    jurisdiction_code: str
    authority_name: str
    required_climate_zone: ClimateZone = ClimateZone.ZONE_IVB
    min_stability_duration_months: int = 12
    requires_local_be_reference: bool = False
    supports_wla_reliance: bool = True
    max_approval_timeline_months_standard: int = 24
    max_approval_timeline_months_reliance: int = 6


class GapStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    PARTIAL_GAP = "PARTIAL_GAP"
    CRITICAL_DEFICIENCY = "CRITICAL_DEFICIENCY"
    RELIANCE_ELIGIBLE = "RELIANCE_ELIGIBLE"


@dataclass
class SectionAnalysis:
    ctd_module: str
    status: GapStatus
    extracted_dossier_fact: str
    target_rule_requirement: str
    action_required: str
    provenance_citation: str


@dataclass
class CountryGapReport:
    jurisdiction_code: str
    authority_name: str
    overall_status: GapStatus
    reliance_pathway_eligible: bool
    applicable_reliance_framework: str
    estimated_timeline_months: int
    estimated_cost_savings_usd: float
    section_analyses: List[SectionAnalysis]


@dataclass
class FullEquivalencePassport:
    product_id: str
    brand_name: str
    inn_generic_name: str
    target_country_reports: Dict[str, CountryGapReport]
    generated_at: str
