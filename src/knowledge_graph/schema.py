"""
REGULATE.AI — Regulatory Knowledge Graph Architecture
Pure Python Graph representation for zero-dependency execution.
Node and Edge dictionary tracking for Products, APIs, Authorities, Regulations, Evidence, and Reliance Pathways.
"""

from typing import Dict, List, Any
from src.models.schemas import DossierProfile, NMRATargetRule


class RegulatoryKnowledgeGraph:
    """
    In-Memory Knowledge Graph tracking regulatory entities, properties, and directed relationships.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, **attributes):
        self.nodes[node_id] = attributes

    def add_edge(self, source_id: str, target_id: str, relationship: str, **attributes):
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            **attributes
        })

    def add_nmra_authority(self, target_rule: NMRATargetRule):
        """Adds a National Medicines Regulatory Authority node."""
        auth_id = f"AUTH_{target_rule.jurisdiction_code}"
        self.add_node(
            auth_id,
            type="Authority",
            name=target_rule.authority_name,
            country=target_rule.jurisdiction_code,
            required_climate_zone=target_rule.required_climate_zone.value,
            min_stability_months=target_rule.min_stability_duration_months,
            supports_wla=target_rule.supports_wla_reliance,
            standard_timeline_months=target_rule.max_approval_timeline_months_standard,
            reliance_timeline_months=target_rule.max_approval_timeline_months_reliance
        )

    def add_product_dossier(self, dossier: DossierProfile):
        """Adds a Product node and its scientific evidence dependencies."""
        prod_id = f"PROD_{dossier.product_id}"
        self.add_node(
            prod_id,
            type="Product",
            brand_name=dossier.brand_name,
            inn=dossier.inn_generic_name,
            dosage_form=dossier.dosage_form,
            strength=dossier.strength,
            applicant=dossier.applicant_name
        )

        # Add API Node
        api_id = f"API_{dossier.api_spec.name.upper()}"
        self.add_node(
            api_id,
            type="API",
            name=dossier.api_spec.name,
            manufacturer=dossier.api_spec.manufacturer_name,
            dmf=dossier.api_spec.dmf_number,
            cep=dossier.api_spec.cep_status
        )
        self.add_edge(prod_id, api_id, relationship="CONTAINS_API")

        # Add Stability Evidence Nodes
        for idx, stab in enumerate(dossier.stability_data):
            stab_id = f"EVID_STAB_{dossier.product_id}_{idx}"
            self.add_node(
                stab_id,
                type="StabilityEvidence",
                zone=stab.climate_zone.value,
                temp=stab.temperature_celsius,
                humidity=stab.relative_humidity_percent,
                duration_months=stab.duration_months,
                packaging=stab.container_closure_system
            )
            self.add_edge(prod_id, stab_id, relationship="HAS_EVIDENCE")

        # Add Reference Approval Nodes
        for app in dossier.reference_approvals:
            ref_id = f"REF_APP_{app.value.upper()}"
            self.add_node(ref_id, type="ReferenceApproval", authority=app.value)
            self.add_edge(prod_id, ref_id, relationship="APPROVED_BY")

    def get_graph_summary(self) -> Dict[str, Any]:
        node_types = list(set(attrs.get("type") for attrs in self.nodes.values()))
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types
        }
