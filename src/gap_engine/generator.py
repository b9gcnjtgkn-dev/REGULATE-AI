"""
REGULATE.AI — Dossier Gap Analysis & Equivalence Passport Generator
Aggregates compliance evaluation reports across target markets and outputs the Equivalence Passport.
"""

from typing import List, Dict
from datetime import datetime, timezone
from src.models.schemas import DossierProfile, NMRATargetRule, FullEquivalencePassport, CountryGapReport
from src.rule_engine.evaluator import DeterministicRuleEvaluator
from src.knowledge_graph.schema import RegulatoryKnowledgeGraph


class EquivalencePassportGenerator:
    """
    Generates the complete Cross-Jurisdiction Regulatory Equivalence Passport.
    """

    def __init__(self, knowledge_graph: RegulatoryKnowledgeGraph):
        self.kg = knowledge_graph
        self.evaluator = DeterministicRuleEvaluator()

    def generate_passport(self, dossier: DossierProfile, target_rules: List[NMRATargetRule]) -> FullEquivalencePassport:
        self.kg.add_product_dossier(dossier)
        
        country_reports: Dict[str, CountryGapReport] = {}
        for rule in target_rules:
            self.kg.add_nmra_authority(rule)
            report = self.evaluator.evaluate_country_compliance(dossier, rule)
            country_reports[rule.jurisdiction_code] = report

        return FullEquivalencePassport(
            product_id=dossier.product_id,
            brand_name=dossier.brand_name,
            inn_generic_name=dossier.inn_generic_name,
            target_country_reports=country_reports,
            generated_at=datetime.now(timezone.utc).isoformat()
        )
