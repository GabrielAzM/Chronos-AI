from chronos_safe.apps.api.web_ui import build_catalog_payload, render_dashboard_html


def test_dashboard_html_contains_core_sections() -> None:
    html = render_dashboard_html()
    assert "CHRONOS-SAFE" in html
    assert "Gerar Datasets" in html
    assert "Validação Apophis" in html


def test_catalog_payload_exposes_defaults() -> None:
    payload = build_catalog_payload()
    assert "defaults" in payload
    assert "fixtures" in payload
    assert "default_fixture" in payload["defaults"]
