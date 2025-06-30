# Open Loop Testing Framework (OLTF)

## Overview

This project validates KPIs and system performance for sensor fusion systems using radar, camera, and fusion data.  
It supports both Software-in-the-Loop (SIL) and Hardware-in-the-Loop (HIL) testing scenarios.

## Features

- Modular plugin system (before, live, post-run)
- Configurable regression scenarios
- KPI dashboards with log reporting
- Docker-based test orchestration
- GitLab CI integration

## Project Structure

- `oltf/core/` – framework engine (orchestrator, logging, module launching)
- `oltf/plugins/` – before/live/post-run test logic
- `configs/` – YAML config files for regression/CI/etc.
- `reports/` – logs and KPI results
- `docker/` – SUT module definitions via Docker Compose

## Usage

### Local Test Run

```bash
python oltf/core/test_orchestrator.py --config configs/regression.yaml
```

### Run in Docker

```bash
docker build -t oltf .
docker run --rm -v $(pwd):/app oltf
```

## KPI Plugins

- `latency_kpi`
- `error_rate_kpi`
- `decision_consistency_kpi`
- `spatial_correlation_kpi`
- `confidence_stability_kpi`

## CI Pipeline

- Linting (flake8)
- Unit Tests
- Post-run KPI validations with artifact export

## License

MIT
