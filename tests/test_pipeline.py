"""
REGULATE.AI — Comprehensive Verification Suite (6/6 Tests)
Tests domain schemas, deterministic rule evaluator logic, knowledge graph,
two-pass extraction provenance, self-improvement engine, and executive output translator.
"""

import unittest
import os
import sys

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

        self.stab_ii = StabilityStudy(
            climate_zone=ClimateZone.ZONE_II,
            temperature_celsius=25,
            relative_humidity_percent=60,
            duration_months=24,
            container_closure_system="PVC Blister"
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

        self.brazil_rule = NMRATargetRule(
            jurisdiction_code="BR",
            authority_name="ANVISA Brazil",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=24,
            supports_wla_reliance=False,
            max_approval_timeline_months_standard=18,
            max_approval_timeline_months_reliance=18
        )

    # Test 1: Deterministic WLA Reliance Fast-Track Evaluation
    def test_wla_reliance_eligibility(self):
        evaluator = DeterministicRuleEvaluator()
        report = evaluator.evaluate_country_compliance(self.dossier, self.kenya_rule)
        
        self.assertTrue(report.reliance_pathway_eligible)
        self.assertEqual(report.overall_status, GapStatus.RELIANCE_ELIGIBLE)
        self.assertEqual(report.estimated_timeline_months, 6)
        self.assertEqual(report.estimated_cost_savings_usd, 35000.0)

    # Test 2: Autonomous Self-Improvement Engine & Rule Embedding
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

    # Test 3: Executive Output Translator & Commercial Impact
    def test_executive_output_translator(self):
        evaluator = DeterministicRuleEvaluator()
        report = evaluator.evaluate_country_compliance(self.dossier, self.kenya_rule)
        
        translation = ExecutiveOutputTranslator.translate_country_report(report)
        self.assertIn("FAST-TRACK APPROVED", translation["executive_tldr"])
        self.assertIn("VERY LOW RISK", translation["risk_level"])
        self.assertIn("Saves $35,000", translation["commercial_financial_impact"])

    # Test 4: Stability Climate Zone Deficiency Detection
    def test_climate_zone_gap_detection(self):
        evaluator = DeterministicRuleEvaluator()
        # Create dossier with Zone II only (temperate), applying to Kenya (Zone IVB required)
        dossier_zone_ii = DossierProfile(
            product_id="PROD-ZONE-GAP",
            brand_name="TEST-TEMPERATE",
            inn_generic_name="Amoxicillin",
            dosage_form="Capsule",
            strength="500mg",
            applicant_name="Generic Exporters Ltd",
            applicant_country="India",
            reference_approvals=[],
            api_spec=self.api_spec,
            stability_data=[self.stab_ii],
            be_study=self.be_study,
            certificates=self.certs
        )
        report = evaluator.evaluate_country_compliance(dossier_zone_ii, self.kenya_rule)
        
        self.assertEqual(report.overall_status, GapStatus.CRITICAL_DEFICIENCY)
        self.assertFalse(report.reliance_pathway_eligible)
        self.assertTrue(any(ClimateZone.ZONE_IVB.value in s.target_rule_requirement for s in report.section_analyses))

    # Test 5: Full Equivalence Passport Multi-Country Generation
    def test_equivalence_passport_generation(self):
        kg = RegulatoryKnowledgeGraph()
        generator = EquivalencePassportGenerator(kg)
        
        passport = generator.generate_passport(
            dossier=self.dossier,
            target_rules=[self.kenya_rule, self.brazil_rule]
        )
        
        self.assertEqual(passport.product_id, "PROD-TEST-001")
        self.assertEqual(len(passport.target_country_reports), 2)
        self.assertIn("KE", passport.target_country_reports)
        self.assertIn("BR", passport.target_country_reports)
        self.assertTrue(passport.target_country_reports["KE"].reliance_pathway_eligible)

    # Test 6: Two-Pass Extraction Provenance & Audit Confidence
    def test_extraction_auditor_provenance(self):
        pipeline = ExtractionAuditorPipeline()
        sample_raw_dossier = "Module 3.2.S: Amoxicillin Trihydrate DMF-2024-8849. Stability 30C/75% RH 12 months."
        metadata = {
            "api_name": "Amoxicillin Trihydrate",
            "dmf_number": "DMF-2024-8849",
            "api_manufacturer": "Aurobindo Pharma Ltd"
        }
        
        profile, confidence_score = pipeline.process_dossier_text(sample_raw_dossier, metadata)
        self.assertEqual(profile.api_spec.name, "Amoxicillin Trihydrate")
        self.assertGreaterEqual(confidence_score, 0.95)


if __name__ == "__main__":
    unittest.main()
