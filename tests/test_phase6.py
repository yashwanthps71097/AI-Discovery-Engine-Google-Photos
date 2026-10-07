import os
import json
from pathlib import Path

def test_phase6_frontend_structure_and_build():
    """Verify Phase 6 frontend build artifacts, configuration, and components exist and are intact."""
    project_root = Path(__file__).resolve().parent.parent
    frontend_dir = project_root / "frontend"

    # 1. Verify critical frontend files exist
    assert (frontend_dir / "package.json").exists(), "package.json missing"
    assert (frontend_dir / "vite.config.ts").exists(), "vite.config.ts missing"
    assert (frontend_dir / "tailwind.config.js").exists(), "tailwind.config.js missing"
    assert (frontend_dir / "index.html").exists(), "index.html missing"
    assert (frontend_dir / "src" / "App.tsx").exists(), "App.tsx missing"
    assert (frontend_dir / "src" / "main.tsx").exists(), "main.tsx missing"
    assert (frontend_dir / "src" / "index.css").exists(), "index.css missing"
    assert (frontend_dir / "src" / "data" / "mockDiscoveryData.ts").exists(), "mockDiscoveryData.ts missing"
    assert (frontend_dir / "src" / "api" / "client.ts").exists(), "api/client.ts missing"

    # 2. Verify production build output exists
    dist_dir = frontend_dir / "dist"
    assert dist_dir.exists(), "dist/ directory missing - build did not complete"
    assert (dist_dir / "index.html").exists(), "dist/index.html missing"

    assets_dir = dist_dir / "assets"
    assert assets_dir.exists(), "dist/assets/ missing"
    asset_files = list(assets_dir.glob("*"))
    assert len(asset_files) >= 2, f"Expected at least CSS and JS asset bundles, found {len(asset_files)}"

    has_js = any(f.suffix == ".js" for f in asset_files)
    has_css = any(f.suffix == ".css" for f in asset_files)
    assert has_js, "JavaScript production bundle missing"
    assert has_css, "CSS production bundle missing"

    # 3. Verify App.tsx contains all 7 Dashboard tabs and 3-Layer Epistemic structures
    app_tsx = (frontend_dir / "src" / "App.tsx").read_text(encoding="utf-8")
    assert "Source Overview" in app_tsx
    assert "Retrieval Scenarios" in app_tsx
    assert "Memory Patterns" in app_tsx
    assert "Search Behaviors" in app_tsx
    assert "Failure Funnel" in app_tsx
    assert "Problem Clusters" in app_tsx
    assert "Opportunity Prioritization" in app_tsx
    assert "Layer 1: Verbatim Qualitative Evidence" in app_tsx
    assert "Layer 2: 7-Dimensional Semantic Tagging" in app_tsx
    assert "Layer 3: Testable Opportunity Hypothesis" in app_tsx
    assert "Executive Dossier" in app_tsx
    assert "EXECUTIVE_DOSSIER" in app_tsx

    print("\n[OK] Phase 6 Frontend verification passed completely.")
