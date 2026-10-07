import sys
from pathlib import Path
from starlette.testclient import TestClient

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app

client = TestClient(app)

def test_api_v1_dashboard_endpoints():
    """Verify all 7 analytical dashboard API endpoints return HTTP 200 with structured data."""

    # 1. Healthcheck
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"
    print("[OK] Health endpoint passed.")

    # 2. Dashboard 1: Overview
    res_overview = client.get("/api/v1/overview")
    assert res_overview.status_code == 200
    data_overview = res_overview.json()
    assert "total_conversations_analyzed" in data_overview
    assert "platform_distribution" in data_overview
    assert len(data_overview["canonical_sources_sample"]) > 0
    print("[OK] Dashboard 1 (/api/v1/overview) passed.")

    # 3. Dashboard 2: Scenarios
    res_scenarios = client.get("/api/v1/scenarios")
    assert res_scenarios.status_code == 200
    data_scenarios = res_scenarios.json()
    assert "scenario_distribution" in data_scenarios
    assert "cross_tab_scenario_vs_outcome" in data_scenarios
    print("[OK] Dashboard 2 (/api/v1/scenarios) passed.")

    # 4. Dashboard 3: Memory Patterns
    res_memory = client.get("/api/v1/memory-patterns")
    assert res_memory.status_code == 200
    data_memory = res_memory.json()
    assert "hypothesis_validation" in data_memory
    assert data_memory["hypothesis_validation"]["status"] == "CONFIRMED"
    print("[OK] Dashboard 3 (/api/v1/memory-patterns) passed.")

    # 5. Dashboard 4: Search Behaviors
    res_behaviors = client.get("/api/v1/search-behaviors")
    assert res_behaviors.status_code == 200
    data_behaviors = res_behaviors.json()
    assert "search_tactics_frequency" in data_behaviors
    assert "behavioral_transition_flows" in data_behaviors
    print("[OK] Dashboard 4 (/api/v1/search-behaviors) passed.")

    # 6. Dashboard 5: Failure Funnel
    res_funnel = client.get("/api/v1/failure-funnel")
    assert res_funnel.status_code == 200
    data_funnel = res_funnel.json()
    assert len(data_funnel["stages"]) == 7
    assert "primary_bottleneck_stage" in data_funnel
    print("[OK] Dashboard 5 (/api/v1/failure-funnel) passed.")

    # 7. Dashboard 6: Problem Clusters
    res_clusters = client.get("/api/v1/clusters")
    assert res_clusters.status_code == 200
    data_clusters = res_clusters.json()
    assert data_clusters["total_clusters"] > 0
    first_cluster_id = data_clusters["clusters"][0]["cluster_id"]
    print(f"[OK] Dashboard 6 (/api/v1/clusters) passed ({data_clusters['total_clusters']} clusters).")

    # Detail check on first cluster
    res_cluster_detail = client.get(f"/api/v1/clusters/{first_cluster_id}")
    assert res_cluster_detail.status_code == 200
    assert "all_member_evidence" in res_cluster_detail.json()
    print(f"[OK] Dashboard 6 Detail (/api/v1/clusters/{first_cluster_id}) passed.")

    # 8. Dashboard 7: Opportunities
    res_opps = client.get("/api/v1/opportunities")
    assert res_opps.status_code == 200
    data_opps = res_opps.json()
    assert data_opps["total_opportunities"] > 0
    print(f"[OK] Dashboard 7 (/api/v1/opportunities) passed ({data_opps['total_opportunities']} opportunities).")

    # 9. Executive Dossier
    res_dossier = client.get("/api/v1/executive-dossier")
    assert res_dossier.status_code == 200
    data_dossier = res_dossier.json()
    assert "q1_hardest_photos" in data_dossier
    assert "q8_priority_opportunity_areas" in data_dossier
    print("[OK] Executive Dossier (/api/v1/executive-dossier) passed.")

    # 10. Filterable Evidence List
    res_evidence = client.get("/api/v1/evidence?limit=5")
    assert res_evidence.status_code == 200
    data_evidence = res_evidence.json()
    assert data_evidence["total_records"] > 0
    assert len(data_evidence["records"]) <= 5
    print(f"[OK] Evidence Drill-down (/api/v1/evidence) passed ({data_evidence['total_records']} total records).")

if __name__ == "__main__":
    test_api_v1_dashboard_endpoints()
    print("\n=== ALL PHASE 5 API VERIFICATION CHECKS PASSED SUCCESSFULLY! ===")
