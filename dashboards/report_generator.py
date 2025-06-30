from typing import Dict, List
from core.models import PluginResult
import os
from pathlib import Path

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Regression Matrix Dashboard</title>
    <style>
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ccc;
            text-align: center;
            padding: 8px;
        }}
        .passed {{ background-color: #c8e6c9; }}     /* green */
        .failed {{ background-color: #ffcdd2; }}     /* red */
        .warning {{ background-color: #fff9c4; }}    /* yellow */
        .na {{ background-color: #eeeeee; }}         /* gray */
    </style>
</head>
<body>
    <h2>Regression Matrix Dashboard</h2>
    <table>
        <thead>
            <tr>
                <th>Scenario</th>
                {kpi_headers}
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""


def generate_html_report(results: Dict[str, List[PluginResult]], output_path: Path):
    all_kpis = set()

    # 1. Собираем все KPI-плагины
    for plugin_results in results.values():
        for result in plugin_results:
            all_kpis.add(result.plugin_name)

    kpi_headers_html = ''.join(f'<th>{kpi}</th>' for kpi in sorted(all_kpis))
    rows_html = ''

    # 2. Генерируем строки отчета
    for scenario_name, plugin_results_list in results.items():
        # Преобразуем список в словарь: plugin_name → PluginResult
        plugin_results = {r.plugin_name: r for r in plugin_results_list}

        row_html = f'<tr><td>{scenario_name}</td>'
        for kpi in sorted(all_kpis):
            result = plugin_results.get(kpi)
            if result is None:
                css_class = "na"
                content = "⚪"
                tooltip = "Not applicable"
            else:
                tooltip = result.message
                if not result.success:
                    css_class = "failed"
                    content = "❌"
                elif "warning" in result.message.lower():
                    css_class = "warning"
                    content = "⚠️"
                else:
                    css_class = "passed"
                    content = "✅"
            row_html += f'<td class="{css_class}" title="{tooltip}">{content}</td>'
        row_html += '</tr>'
        rows_html += row_html

    # 3. Формируем и сохраняем HTML
    html = HTML_TEMPLATE.format(kpi_headers=kpi_headers_html, rows=rows_html)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)
