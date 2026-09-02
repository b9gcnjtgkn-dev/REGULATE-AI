"""
REGULATE.AI — Production Web Server & Interactive AI Dashboard
Provides REST API endpoints and a zero-dependency interactive Single Page Application (SPA) dashboard.
Includes dynamic port binding and socket reuse to prevent 'Address already in use' errors.
Run with: python3 server.py
"""

import sys
import os
import json
import socket
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Import domain engine modules
from src.models.schemas import (
    DossierProfile, APISpecification, StabilityStudy, BioequivalenceStudy,
    CertificatesProfile, NMRATargetRule, ClimateZone, ReferenceAuthority, GapStatus
)
from src.ai_engine.extractor import ExtractionAuditorPipeline
from src.knowledge_graph.schema import RegulatoryKnowledgeGraph
from src.gap_engine.generator import EquivalencePassportGenerator


class ReusableHTTPServer(HTTPServer):
    """HTTPServer subclass that enables SO_REUSEADDR to prevent port lock conflicts."""
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()


def get_expanded_nmra_rules() -> list:
    """Returns expanded database of 10 international NMRA target rules."""
    return [
        NMRATargetRule(
            jurisdiction_code="KE",
            authority_name="Kenya Pharmacy & Poisons Board (PPB)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=24,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="TZ",
            authority_name="Tanzania Medicines & Medical Devices Authority (TMDA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=24,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="UG",
            authority_name="Uganda National Drug Authority (NDA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=18,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="RW",
            authority_name="Rwanda Food and Drugs Authority (FDA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=18,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="ZA",
            authority_name="South African Health Products Regulatory Authority (SAHPRA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=30,
            max_approval_timeline_months_reliance=9
        ),
        NMRATargetRule(
            jurisdiction_code="NG",
            authority_name="Nigeria NAFDAC",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=24,
            max_approval_timeline_months_reliance=8
        ),
        NMRATargetRule(
            jurisdiction_code="GH",
            authority_name="Ghana Food and Drugs Authority (FDA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=18,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="SA",
            authority_name="Saudi Food and Drug Authority (SFDA)",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=18,
            max_approval_timeline_months_reliance=6
        ),
        NMRATargetRule(
            jurisdiction_code="VN",
            authority_name="Vietnam Drug Administration (DAV)",
            required_climate_zone=ClimateZone.ZONE_IVA,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=24,
            max_approval_timeline_months_reliance=8
        ),
        NMRATargetRule(
            jurisdiction_code="BR",
            authority_name="Brazil ANVISA",
            required_climate_zone=ClimateZone.ZONE_IVB,
            min_stability_duration_months=12,
            supports_wla_reliance=True,
            max_approval_timeline_months_standard=36,
            max_approval_timeline_months_reliance=12
        )
    ]


HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>REGULATE.AI — Regulatory Reliance & Gap Engine</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent-blue: #38bdf8;
            --accent-green: #4ade80;
            --accent-yellow: #facc15;
            --accent-red: #f87171;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); line-height: 1.6; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--card-border); margin-bottom: 24px; }
        .logo { font-size: 24px; font-weight: 800; color: var(--accent-blue); letter-spacing: 1px; }
        .badge { background: #0284c7; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
        
        .grid { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }
        @media (max-width: 1024px) { .grid { grid-template-columns: 1fr; } }
        
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .card-title { font-size: 16px; font-weight: 700; color: var(--accent-blue); margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
        
        label { display: block; font-size: 13px; font-weight: 600; color: var(--text-dim); margin-bottom: 6px; }
        input, select, textarea { width: 100%; background: #0f172a; border: 1px solid var(--card-border); color: white; padding: 10px; border-radius: 6px; font-size: 14px; margin-bottom: 14px; }
        button { width: 100%; background: #2563eb; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; transition: 0.2s; }
        button:hover { background: #1d4ed8; }
        
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
        th { background: #0f172a; color: var(--text-dim); padding: 12px; border-bottom: 1px solid var(--card-border); font-size: 12px; text-transform: uppercase; }
        td { padding: 14px 12px; border-bottom: 1px solid var(--card-border); }
        
        .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; display: inline-block; }
        .status-RELIANCE_ELIGIBLE { background: rgba(74, 222, 128, 0.15); color: #4ade80; border: 1px solid #4ade80; }
        .status-COMPLIANT { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #38bdf8; }
        .status-PARTIAL_GAP { background: rgba(250, 204, 21, 0.15); color: #facc15; border: 1px solid #facc15; }
        .status-CRITICAL_DEFICIENCY { background: rgba(248, 113, 113, 0.15); color: #f87171; border: 1px solid #f87171; }
        
        .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
        .metric-card { background: #0f172a; padding: 16px; border-radius: 8px; border: 1px solid var(--card-border); text-align: center; }
        .metric-val { font-size: 24px; font-weight: 800; color: var(--accent-green); }
        .metric-lbl { font-size: 12px; color: var(--text-dim); margin-top: 4px; }
        
        .section-box { background: #0f172a; border-left: 4px solid var(--accent-blue); padding: 14px; margin-bottom: 12px; border-radius: 0 8px 8px 0; }
        .section-title { font-weight: 700; font-size: 14px; margin-bottom: 4px; display: flex; justify-content: space-between; }
        .section-detail { font-size: 13px; color: var(--text-dim); }
        .provenance { font-size: 11px; color: #64748b; margin-top: 6px; font-style: italic; }
    </style>
</head>
<body>

    <div class="header">
        <div>
            <span class="logo">REGULATE.AI</span>
            <span style="color: var(--text-dim); margin-left: 12px; font-size: 14px;">Regulatory Reliance & Dossier Gap Engine</span>
        </div>
        <div>
            <span class="badge">Zero-Hallucination Graph Architecture</span>
        </div>
    </div>

    <div class="grid">
        <!-- LEFT PANEL: DOSSIER INPUT -->
        <div>
            <div class="card">
                <div class="card-title">📦 1. Product & Dossier Profile</div>
                
                <label>Select Pre-Loaded Generic Dossier Template</label>
                <select id="templateSelect" onchange="loadTemplate()">
                    <option value="amoxclav">Amoxicclav 625mg Tablets (Cipla Exports)</option>
                    <option value="metformin">Metformin 500mg SR (Sun Pharma)</option>
                    <option value="atorvastatin">Atorvastatin 20mg Tablets (Dr Reddy's)</option>
                </select>

                <label>Product Brand Name</label>
                <input type="text" id="brandName" value="AMOXICLAV-625">

                <label>INN Generic Name</label>
                <input type="text" id="innName" value="Amoxicillin + Clavulanate Potassium">

                <label>Dosage Form & Strength</label>
                <input type="text" id="strength" value="Film-Coated Tablet 625mg">

                <label>API Supplier & DMF</label>
                <input type="text" id="apiSupplier" value="Aurobindo Pharma (DMF-2024-8849, CEP Certified)">

                <label>Reference Approvals Held</label>
                <select id="refApprovals" multiple style="height: 80px;">
                    <option value="WHO Prequalification" selected>WHO Prequalification (WHO-PQ)</option>
                    <option value="US FDA">US FDA Approved</option>
                    <option value="EU EMA">EU EMA Approved</option>
                    <option value="India CDSCO" selected>India CDSCO Approved</option>
                </select>

                <label>Tested Stability Conditions</label>
                <select id="stabilityZone">
                    <option value="IVb" selected>Zone IVb (30°C / 75% RH - 12 Months) + Zone II (24M)</option>
                    <option value="II">Zone II (25°C / 60% RH - 24 Months Only)</option>
                </select>

                <button onclick="runAnalysis()">🚀 Run Cross-Border Reliance Audit</button>
            </div>

            <div class="card">
                <div class="card-title">🌍 2. Destination Market Selector</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <label><input type="checkbox" class="market-check" value="KE" checked> Kenya (PPB)</label>
                    <label><input type="checkbox" class="market-check" value="TZ" checked> Tanzania (TMDA)</label>
                    <label><input type="checkbox" class="market-check" value="UG" checked> Uganda (NDA)</label>
                    <label><input type="checkbox" class="market-check" value="RW" checked> Rwanda (FDA)</label>
                    <label><input type="checkbox" class="market-check" value="ZA" checked> South Africa (SAHPRA)</label>
                    <label><input type="checkbox" class="market-check" value="NG" checked> Nigeria (NAFDAC)</label>
                    <label><input type="checkbox" class="market-check" value="GH" checked> Ghana (FDA)</label>
                    <label><input type="checkbox" class="market-check" value="SA" checked> Saudi Arabia (SFDA)</label>
                    <label><input type="checkbox" class="market-check" value="VN" checked> Vietnam (DAV)</label>
                    <label><input type="checkbox" class="market-check" value="BR" checked> Brazil (ANVISA)</label>
                </div>
            </div>
        </div>

        <!-- RIGHT PANEL: EQUIVALENCE PASSPORT RESULTS -->
        <div>
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-val" id="metricCountries">4</div>
                    <div class="metric-lbl">Target Markets</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val" id="metricReliance">100%</div>
                    <div class="metric-lbl">Reliance Eligible</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val" id="metricTime">18 Mo</div>
                    <div class="metric-lbl">Time Saved / Market</div>
                </div>
                <div class="metric-card">
                    <div class="metric-val" id="metricSavings">$140,000</div>
                    <div class="metric-lbl">Est. Direct Cost Savings</div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">📜 Equivalence Passport & Reliance Matrix</div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Country</th>
                                <th>Authority</th>
                                <th>Status</th>
                                <th>Reliance Pathway</th>
                                <th>Timeline</th>
                                <th>Est Savings</th>
                            </tr>
                        </thead>
                        <tbody id="passportBody">
                            <tr><td colspan="6" style="text-align: center; color: var(--text-dim);">Click 'Run Cross-Border Reliance Audit' to evaluate...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-title">🔍 Section-by-Section Gap Breakdown (Kenya PPB Example)</div>
                <div id="sectionBreakdown">
                    <div style="color: var(--text-dim);">Run audit to view granular section gap breakdown...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const templates = {
            amoxclav: {
                brand: "AMOXICLAV-625",
                inn: "Amoxicillin + Clavulanate Potassium",
                strength: "Film-Coated Tablet 625mg",
                api: "Aurobindo Pharma (DMF-2024-8849, CEP Certified)",
                zone: "IVb"
            },
            metformin: {
                brand: "METFORMIN-500-SR",
                inn: "Metformin Hydrochloride",
                strength: "Sustained Release Tablet 500mg",
                api: "Sun Pharma Advanced (DMF-2023-1102)",
                zone: "II"
            },
            atorvastatin: {
                brand: "ATORVA-20",
                inn: "Atorvastatin Calcium",
                strength: "Film-Coated Tablet 20mg",
                api: "Dr Reddy's Labs (DMF-2025-4491, CEP Certified)",
                zone: "IVb"
            }
        };

        function loadTemplate() {
            const key = document.getElementById('templateSelect').value;
            const t = templates[key];
            document.getElementById('brandName').value = t.brand;
            document.getElementById('innName').value = t.inn;
            document.getElementById('strength').value = t.strength;
            document.getElementById('apiSupplier').value = t.api;
            document.getElementById('stabilityZone').value = t.zone;
        }

        async function runAnalysis() {
            const selectedMarkets = Array.from(document.querySelectorAll('.market-check:checked')).map(c => c.value);
            const stabilityZone = document.getElementById('stabilityZone').value;

            const payload = {
                brand_name: document.getElementById('brandName').value,
                inn_name: document.getElementById('innName').value,
                strength: document.getElementById('strength').value,
                api_supplier: document.getElementById('apiSupplier').value,
                stability_zone: stabilityZone,
                target_markets: selectedMarkets
            };

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            renderDashboard(data);
        }

        function renderDashboard(data) {
            document.getElementById('metricCountries').innerText = data.total_markets;
            document.getElementById('metricReliance').innerText = data.reliance_percentage + '%';
            document.getElementById('metricTime').innerText = data.avg_time_saved_months + ' Mo';
            document.getElementById('metricSavings').innerText = '$' + data.total_savings_usd.toLocaleString();

            const tbody = document.getElementById('passportBody');
            tbody.innerHTML = '';

            for (const [code, rep] of Object.entries(data.reports)) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${rep.jurisdiction_code}</strong></td>
                    <td>${rep.authority_name}</td>
                    <td><span class="status-badge status-${rep.overall_status}">${rep.overall_status}</span></td>
                    <td style="color: var(--accent-blue); font-size: 13px;">${rep.applicable_reliance_framework}</td>
                    <td><strong>${rep.estimated_timeline_months} Months</strong></td>
                    <td style="color: var(--accent-green); font-weight: 700;">$${rep.estimated_cost_savings_usd.toLocaleString()}</td>
                `;
                tbody.appendChild(tr);
            }

            const breakdown = document.getElementById('sectionBreakdown');
            breakdown.innerHTML = '';

            const sampleReport = Object.values(data.reports)[0];
            if (sampleReport) {
                sampleReport.section_analyses.forEach(sec => {
                    const box = document.createElement('div');
                    box.className = 'section-box';
                    box.innerHTML = `
                        <div class="section-title">
                            <span>${sec.ctd_module}</span>
                            <span class="status-badge status-${sec.status}">${sec.status}</span>
                        </div>
                        <div class="section-detail"><strong>Fact:</strong> ${sec.extracted_dossier_fact}</div>
                        <div class="section-detail"><strong>Rule:</strong> ${sec.target_rule_requirement}</div>
                        <div class="section-detail" style="color: var(--accent-yellow); margin-top: 4px;"><strong>Action:</strong> ${sec.action_required}</div>
                        <div class="provenance">📌 Citation: ${sec.provenance_citation}</div>
                    `;
                    breakdown.appendChild(box);
                });
            }
        }

        window.onload = runAnalysis;
    </script>
</body>
</html>
"""


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for REST API and HTML UI Dashboard."""

    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path).path
        
        if url_path == "/" or url_path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_DASHBOARD.encode("utf-8"))
        elif url_path == "/api/rules":
            rules = get_expanded_nmra_rules()
            rules_data = [
                {
                    "code": r.jurisdiction_code,
                    "authority": r.authority_name,
                    "zone": r.required_climate_zone.value,
                    "wla_reliance": r.supports_wla_reliance,
                    "timeline_standard": r.max_approval_timeline_months_standard,
                    "timeline_reliance": r.max_approval_timeline_months_reliance
                }
                for r in rules
            ]
            self._send_json({"rules": rules_data})
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_POST(self):
        url_path = urllib.parse.urlparse(self.path).path
        
        if url_path == "/api/analyze":
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len).decode('utf-8')
            payload = json.loads(post_body) if post_body else {}
            
            result = self._process_analysis_request(payload)
            self._send_json(result)
        else:
            self.send_error(404, "Endpoint Not Found")

    def _process_analysis_request(self, payload: dict) -> dict:
        brand_name = payload.get("brand_name", "AMOXICLAV-625")
        inn_name = payload.get("inn_name", "Amoxicillin + Clavulanate Potassium")
        strength = payload.get("strength", "Film-Coated Tablet 625mg")
        api_supplier = payload.get("api_supplier", "Aurobindo Pharma")
        stability_zone = payload.get("stability_zone", "IVb")
        target_market_codes = payload.get("target_markets", ["KE", "TZ", "UG", "ZA"])

        stability_studies = [
            StabilityStudy(
                climate_zone=ClimateZone.ZONE_II,
                temperature_celsius=25,
                relative_humidity_percent=60,
                duration_months=24,
                container_closure_system="Alu-Alu Blister"
            )
        ]
        if stability_zone == "IVb":
            stability_studies.append(
                StabilityStudy(
                    climate_zone=ClimateZone.ZONE_IVB,
                    temperature_celsius=30,
                    relative_humidity_percent=75,
                    duration_months=12,
                    container_closure_system="Alu-Alu Blister"
                )
            )

        dossier = DossierProfile(
            product_id="PROD-" + brand_name[:6].upper(),
            brand_name=brand_name,
            inn_generic_name=inn_name,
            dosage_form="Tablet",
            strength=strength,
            applicant_name="Cipla Exports Pvt Ltd",
            applicant_country="India",
            reference_approvals=[ReferenceAuthority.WHO_PQ, ReferenceAuthority.INDIA_CDSCO],
            api_spec=APISpecification(
                name=inn_name.split("+")[0].strip(),
                dmf_number="DMF-2024-8849",
                cep_status=True,
                manufacturer_name=api_supplier,
                manufacturing_site_country="India",
                pharmacopoeia_grade="USP/Ph. Eur"
            ),
            stability_data=stability_studies,
            be_study=BioequivalenceStudy(
                conducted=True,
                bcs_class_waiver=False,
                reference_innovator_product="Augmentin 625mg (GSK)",
                reference_product_country="United Kingdom"
            ),
            certificates=CertificatesProfile(copp_available=True, who_gmp_certified=True)
        )

        all_rules = get_expanded_nmra_rules()
        selected_rules = [r for r in all_rules if r.jurisdiction_code in target_market_codes]

        kg = RegulatoryKnowledgeGraph()
        generator = EquivalencePassportGenerator(kg)
        passport = generator.generate_passport(dossier, selected_rules)

        reports_dict = {}
        total_savings = 0.0
        reliance_count = 0

        for code, rep in passport.target_country_reports.items():
            reports_dict[code] = {
                "jurisdiction_code": rep.jurisdiction_code,
                "authority_name": rep.authority_name,
                "overall_status": rep.overall_status.value,
                "reliance_pathway_eligible": rep.reliance_pathway_eligible,
                "applicable_reliance_framework": rep.applicable_reliance_framework,
                "estimated_timeline_months": rep.estimated_timeline_months,
                "estimated_cost_savings_usd": rep.estimated_cost_savings_usd,
                "section_analyses": [
                    {
                        "ctd_module": sec.ctd_module,
                        "status": sec.status.value,
                        "extracted_dossier_fact": sec.extracted_dossier_fact,
                        "target_rule_requirement": sec.target_rule_requirement,
                        "action_required": sec.action_required,
                        "provenance_citation": sec.provenance_citation
                    }
                    for sec in rep.section_analyses
                ]
            }
            total_savings += rep.estimated_cost_savings_usd
            if rep.reliance_pathway_eligible:
                reliance_count += 1

        total_markets = len(selected_rules)
        reliance_pct = int((reliance_count / total_markets * 100)) if total_markets > 0 else 0

        return {
            "brand_name": brand_name,
            "product_id": dossier.product_id,
            "total_markets": total_markets,
            "reliance_percentage": reliance_pct,
            "avg_time_saved_months": 18,
            "total_savings_usd": total_savings,
            "reports": reports_dict
        }

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))


def start_server_with_fallback(initial_port: int = 8080):
    candidate_ports = [initial_port, 8081, 8082, 8888, 9090, 9091]
    
    for port in candidate_ports:
        try:
            server_address = ('', port)
            httpd = ReusableHTTPServer(server_address, RequestHandler)
            print("=" * 80)
            print(f" REGULATE.AI Web Server & Interactive Dashboard Launched!")
            print(f" Access URL : http://localhost:{port}")
            print(f" REST API   : http://localhost:{port}/api/analyze")
            print("=" * 80)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer shutting down.")
            return
        except OSError as err:
            if err.errno == 48:  # Address already in use
                print(f"Port {port} is busy. Trying fallback port...")
                continue
            else:
                raise err

    print("❌ Could not bind to any available port.")


def main():
    start_server_with_fallback(8080)


if __name__ == "__main__":
    main()
