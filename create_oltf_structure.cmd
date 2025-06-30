@echo off
REM Create folders
mkdir configs
mkdir core
mkdir plugins
mkdir plugins\before_run
mkdir plugins\live
mkdir plugins\post_run
mkdir data
mkdir reports
mkdir reports\logs
mkdir reports\summary
mkdir dashboards

REM Create config YAMLs
echo.> configs\regression.yaml
echo.> configs\ci_camera.yaml
echo.> configs\ci_radar.yaml
echo.> configs\ci_fusion.yaml

REM Create core Python files
echo.> core\test_orchestrator.py
echo.> core\logger_manager.py
echo.> core\plugin_registry.py
echo.> core\module_launcher.py

REM Create plugin files
echo.> plugins\before_run\clean_output_dir.py
echo.> plugins\live\cpu_monitor.py
echo.> plugins\post_run\latency_kpi.py
echo.> plugins\post_run\error_rate_kpi.py
echo.> plugins\post_run\decision_consistency_kpi.py
echo.> plugins\post_run\spatial_correlation_kpi.py
echo.> plugins\post_run\confidence_stability_kpi.py

REM Create sample data files
echo.> data\radar_data.jsonl
echo.> data\camera_data.jsonl
echo.> data\fused_data.jsonl

REM Create report files
echo.> reports\kpi_results.json

REM Create dashboard HTML
echo.> dashboards\index.html

REM Create top-level files
echo.> requirements.txt
echo.> Dockerfile
echo.> .gitlab-ci.yml
echo.> README.md

echo Project structure created successfully in current directory.
