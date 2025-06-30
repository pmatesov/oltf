def generate_html_report(self):
    import os

    report_path = Path("./reports/regression_matrix.html")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    kpi_names = set()
    for scenario_result in self.kpi_results.values():
        kpi_names.update(scenario_result.keys())
    kpi_names = sorted(kpi_names)

    def status_to_color(status):
        return {
            "pass": "green",
            "fail": "red",
            "warning": "yellow",
            "not_applicable": "lightgray"
        }.get(status, "white")

    html = ["<html><head><style>",
            "table { border-collapse: collapse; }",
            "td, th { border: 1px solid black; padding: 8px; text-align: center; }",
            "</style></head><body>",
            "<h2>Regression Matrix</h2>",
            "<table><tr><th>Scenario</th>"]

    for kpi in kpi_names:
        html.append(f"<th>{kpi}</th>")
    html.append("</tr>")

    for scenario, kpis in self.kpi_results.items():
        html.append(f"<tr><td>{scenario}</td>")
        for kpi in kpi_names:
            cell = kpis.get(kpi)
            if cell:
                color = status_to_color(cell['status'])
                value = cell['value']
                html.append(f"<td style='background-color:{color}'>{value:.2f}</td>")
            else:
                html.append("<td style='background-color:lightgray'>N/A</td>")
        html.append("</tr>")

    html.append("</table></body></html>")

    report_path.write_text("\n".join(html))
    self.logger.info(f"Regression matrix report saved to {report_path}")
