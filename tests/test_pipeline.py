"""
REGULATE.AI — Comprehensive Test Suite
Tests domain schemas, rule evaluator logic, knowledge graph, self-improvement engine, and executive output translator.
"""

import unittest
import os
from src.models.schemas import (
    DossierProfile, APISpecification, StabilityStudy, BioequivalenceStudy,
    CertificatesProfile, NMRATargetRule, ClimateZone, ReferenceAuthority, GapStatus
)
from src.rule_engine.evaluator import DeterministicRuleEvaluator
from src.knowledge_graph.schema import RegulatoryKnowledgeGraph
from src.gap_engine.generator import EquivalencePassportGenerator
from src.ai_engine.extractor import ExtractionAuditorPipeline
from src.self_improvement.learning_engine import SelfImprovementEngine
from src.explainability.translator import ExecutiveOutputTranslator


class TestRegulateAIPipeline(unittest.TestCase):

    def setUp(self):
        self.api_spec = APISpecification(
            name="Amoxicillin Trihydrate",
            dmf_number="DMF-2024-8849",
            cep_status=True,
            manufacturer_name="Aurobindo Pharma",
            manufacturing_site_country="India",
            pharmacopoeia_grade="USP/Ph. Eur"
        )

        self.stab_ivb = StabilityStudy(
            climate_zone=ClimateZone.ZONE_IVB,
            temperature_celsius=30,
            relative_humidity_percent=75,
            duration_months=12,
            container_closure_system="Alu-Alu Blister"
        )

        self.be_study = BioequivalenceStudy(
            conducted=True,
            bcs_class_waiver=False,
            reference_innovator_product="Augmentin 625mg (GSK)",
            reference_product_country="United Kingdom"
        )

        self.certs = CertificatesProfile(copp_available=True, who_gmp_certified=True)

        self.dossier = DossierProfile(
            product_id="PROD-TEST-001",
            brand_name="TEST-CLAV",
            inn_generic_name="Amoxicillin + Clavulanate",
            dosage_form="Tablet",
            strength="625mg",
            applicant_name="Cipla Exports",
            applicant_country="India",
            reference_approvals=[ReferenceAuthority.WHO_PQ],
            api_spec=self.api_spec,
            stability_data=[self.stab_ivb],
            be_study=self.be_study,
            certificates=self.certs
        )

        self.kenya_rule = NMRATargetRule(
            jurisdiction_code="KE",
            authority_name="Kenya Pharmacy & Poisons Board (PPB)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=24,
            max_approval_timeline_months_reliance=6
        )

    def test_wla_reliance_eligibility(self):
        evaluator = DeterministicRuleEvaluator()
        report = evaluator.evaluate_country_compliance(self.dossier, self.kenya_rule)
        
        self.assertTrue(report.reliance_pathway_eligible)
        self.assertEqual(report.overall_status, GapStatus.RELIANCE_ELIGIBLE)
        self.assertEqual(report.estimated_timeline_months, 6)
        self.assertEqual(report.estimated_cost_savings_usd, 35000.0)

    def test_self_improvement_engine_learning(self):
        kg = RegulatoryKnowledgeGraph()
        kg.add_nmra_authority(self.kenya_rule)
        
        test_history_file = "test_learning_history.json"
        if os.path.exists(test_history_file):
            os.remove(test_history_file)

        engine = SelfImprovementEngine(kg, history_file=test_history_file)
        
        # Ingest new circular update
        log = engine.ingest_regulatory_circular(
            nmra_code="KE",
            circular_title="Kenya PPB 2026 Fast-Track Guideline Update",
            updated_rules={"reliance_timeline_months": 4}
        )
        self.assertEqual(log["status"], "GRAPH_UPDATED_SUCCESSFULLY")
        self.assertEqual(kg.nodes["AUTH_KE"]["reliance_timeline_months"], 4)

        # Learn empirical query outcome pattern
        query_log = engine.learn_from_empirical_query_outcome(
            nmra_code="KE",
            query_type="Innovator_Reference_Product",
            winning_strategy="Cite_WHO_TRS_1033_Annex_10"
        )
        self.assertEqual(query_log["status"], "PATTERN_EMBEDDED_IN_GRAPH")

        summary = engine.get_self_improvement_summary()
        self.assertEqual(summary["total_learning_iterations"], 2)

        if os.path.exists(test_history_file):
            os.remove(test_history_file)

    def test_executive_output_translator(self):
        evaluator = DeterministicRuleEvaluator()
        report = evaluator.evaluate_country_compliance(self.dossier, self.kenya_rule)
        
        translation = ExecutiveOutputTranslator.translate_country_report(report)
        self.assertIn("FAST-TRACK APPROVED", translation["executive_tldr"])
        self.assertIn("VERY LOW RISK", translation["risk_level"])
        self.assertIn("Saves $35,000", translation["commercial_financial_impact"])


if __name__ == "__main__":
    unittest.main()
