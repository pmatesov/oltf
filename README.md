# Open Loop Testing Framework (OLTF)

**OLTF** is a modular and extensible Python-based framework designed for regression testing of sensor fusion and perception algorithms in autonomous systems. It supports SIL (Software-in-the-Loop) execution of KPIs, visual regression reporting, CI/CD integration, and plugin-based KPI validation.

---

## 📦 Project Structure

```bash
oltf/
├── core/                  # Core execution engine, configuration, and orchestrator
├── configs/               # Regression configuration files (YAML)
├── plugins/               # Post-run KPI plugin implementations
├── dashboards/            # HTML report generation
├── tests/                 # Unit tests for plugin and core logic
├── requirements.txt       # Python dependencies
├── .gitlab-ci.yml         # GitLab CI/CD configuration
├── Dockerfile             # Optional: Docker container for isolated runs
```

---

## ⚙️ How OLTF Works

1. Each test scenario is defined in a YAML file (e.g., `configs/regression.yaml`).
2. Each scenario specifies:
   - Input `.jsonl` data file (e.g., radar/camera/fused)
   - List of KPI plugins to apply
   - Plugin-specific thresholds and settings
3. The `TestOrchestrator` runs each scenario and collects `PluginResult` from each KPI.
4. HTML reports are generated per test run.

📊 **Example Regression Matrix Report**  
Visual representation of pass/fail/warning status for each KPI in each scenario:

![Regression Matrix Report](./dashboards/RegressionMatrixTestReport.JPG)

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run test with a configuration

```bash
PYTHONPATH=. python core/test_orchestrator.py configs/my_custom.yaml
```

> ✅ If no `--config` is provided, the default file `configs/regression.yaml` will be used.

---

## 🧠 KPI Plugin List

| Plugin Name | Description |
|------------|-------------|
| **LatencyKPIPlugin** | Validates latency (e.g., fusion or camera) against threshold. |
| **ErrorRateKPIPlugin** | Checks max/average error rate percentage. |
| **RadarSignalQualityScorePlugin** | Ensures signal quality of radar data meets configured score. |
| **DataDropRateKPIPlugin** | Verifies frame drop rate is within acceptable range. |
| **DataAlignmentJitterKPIPlugin** | Measures timestamp jitter between sensors. |
| **DecisionConsistencyScorePlugin** | Validates consistency of decision classes over time. |
| **FusionRedundancyScorePlugin** | Measures redundancy (e.g. double detection) in sensor fusion results. |
| **SpatialCorrelationConsistencyPlugin** | Validates spatial consistency across multiple sensors. |

---

## ✅ Example Test Output

KPIs visualized over time, including detailed frame-by-frame status:

![Sensor Fusion Test Report](./dashboards/SensorFusionTestReport.JPG)

---

## 🧪 GitLab CI/CD Integration

The project supports CI/CD execution of OLTF via `.gitlab-ci.yml`:

```yaml
post_run_kpis:
  stage: report
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - PYTHONPATH=. python core/test_orchestrator.py configs/regression.yaml
    - mkdir -p public
    - cp reports/dashboard/regression_dashboard.html public/index.html
  artifacts:
    paths:
      - reports/
      - public/
```

### 🔗 GitLab Pipeline:  
[View Pipeline →](https://gitlab.com/pmatesov/oltf/-/pipelines)

---

## 📌 Command-Line Options(NOT implemented yet)

In addition to `--config`, the new CLI entrypoint allows flags:

```bash
PYTHONPATH=. python core/main.py --config configs/my_custom.yaml --test-id BUILD-1234
```

| Flag | Description |
|------|-------------|
| `--config` | Path to regression YAML configuration |
| `--test-id` | Custom ID used in logging/reports |
| `--strict` | Fails pipeline if any KPI fails |
| `--dry-run` | Parses config only, does not run any plugins |

---

## 🧱 Architecture

- Each **Scenario** holds its own input file and plugin list.
- Each **Plugin** has its own config block.
- **TestContext** carries metadata like scenario name and datapath.
- All plugin results are aggregated and visualized.

---

## 📅 ToDo

- [ ] ✨ Add visual per-KPI metrics chart to HTML reports  
  ![KPI Visualization](./dashboards/SensorFusionTestReport.JPG)
- [ ] 🧪 Write full unit test coverage for the OpenLoop Testing Framework
- [ ] 🔧 Some refactors should be done, like datapath should move from TestContext scope to Scenario scope 
- [ ] 🔧 Support more CLI options for automation  
  `--strict`, `--dry-run`, etc.
- [ ] ⏱ Benchmark performance for large `.jsonl` files

---

## 📚 Links

- [GitHub Repo](https://github.com/pmatesov/oltf)
- [GitLab Pipeline](https://gitlab.com/pmatesov/oltf/-/pipelines)