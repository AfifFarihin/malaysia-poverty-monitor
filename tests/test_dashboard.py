from dashboard_stakeholder.app import app
from dashboard_stakeholder.charts import make_choropleth
from dashboard_stakeholder.data import panel_for_year


def test_dashboard_homepage_loads() -> None:
    response = app.server.test_client().get("/")
    assert response.status_code == 200
    assert b"Malaysia Poverty Monitor" in response.data


def test_choropleth_uses_all_2022_states() -> None:
    figure = make_choropleth(panel_for_year(2022, "poverty_absolute"), "poverty_absolute")
    assert len(figure.data) == 1
    assert len(figure.data[0].locations) == 16
