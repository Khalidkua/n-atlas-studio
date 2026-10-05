# N-ATLaS Studio

**N-ATLaS Studio** is an open-source developer, evaluation, and experimentation platform for Nigeria's multilingual large language model, **N-ATLaS**.

The platform is designed to make N-ATLaS easier to develop with, test, evaluate, and compare through a unified developer workflow.

> **N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.**

## Features

- Interactive N-ATLaS playground
- Text generation and chat API
- Provider abstraction for different inference backends
- Live N-ATLaS inference integration
- Evaluation datasets in JSONL format
- Automated benchmark execution
- Multilingual evaluation
- Persistent experiment history
- Experiment comparison

## Architecture

```text
                    ┌─────────────────────────┐
                    │      N-ATLaS Studio     │
                    │      Streamlit UI       │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       FastAPI API       │
                    │                         │
                    │ /generate               │
                    │ /chat                   │
                    │ /evaluate               │
                    │ /experiments            │
                    │ /experiments/compare    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Provider Abstraction  │
                    └────────────┬────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
       ┌───────────┐      ┌──────────────┐    ┌───────────┐
       │   Mock    │      │    Gradio    │    │  Remote   │
       │  Provider │      │   Provider   │    │  Provider │
       └───────────┘      └──────┬───────┘    └───────────┘
                                 │
                                 ▼
                         N-ATLaS inference


## Project Structure

```text
n-atlas-studio/
├── app/
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── evaluation.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── gradio.py
│   │   ├── mock.py
│   │   └── remote.py
│   ├── services/
│   │   ├── dataset_loader.py
│   │   ├── dataset_registry.py
│   │   ├── evaluation_engine.py
│   │   ├── experiment_comparator.py
│   │   ├── experiment_store.py
│   │   ├── language_detector.py
│   │   └── metrics.py
│   ├── ui/
│   │   └── studio.py
│   └── main.py
├── datasets/
│   ├── sample_evaluation.jsonl
│   ├── multilingual_evaluation.jsonl
│   └── natlas_benchmark.jsonl
├── experiments/
├── tests/
├── .env
├── requirements.txt
└── README.md



## Requirements

- Python 3.12+
- Internet connection for the current live Gradio provider
- Linux, macOS, Windows, or WSL

## Installation

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

Example:

```text
PROVIDER=gradio
MODEL_NAME=NCAIR1/N-ATLaS

REMOTE_API_URL=
REMOTE_API_KEY=
REMOTE_CHAT_URL=
REMOTE_GENERATE_URL=

GRADIO_SPACE=seun-ajayi/n-atlas-evaluations
GRADIO_MODEL_KEY=N-ATLaS-LLM
```

### Provider Options

#### Gradio

```text
PROVIDER=gradio
```

Uses the configured Gradio Space to access N-ATLaS.

#### Remote

```text
PROVIDER=remote
```

The remote provider supports configurable HTTP inference endpoints and optional bearer-token authentication.

#### Mock

```text
PROVIDER=mock
```

Useful for local development and UI testing without an inference backend.

## Running the Application

### Start the FastAPI Backend

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Start the Streamlit Studio

In a second terminal:

```bash
.venv/bin/streamlit run app/ui/studio.py
```

The Studio interface will be available at:

```text
http://localhost:8502
```

## API

### Health

```http
GET /health
```

Returns the active provider and model configuration.

### Generate

```http
POST /generate
```

Example request:

```json
{
  "prompt": "What is artificial intelligence?",
  "temperature": 0.3,
  "max_tokens": 128
}
```

### Chat

```http
POST /chat
```

Example request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Explain what a database is."
    }
  ]
}
```

### List Datasets

```http
GET /datasets
```

### Run Evaluation

```http
POST /evaluate
```

Example request:

```json
{
  "dataset_path": "datasets/natlas_benchmark.jsonl",
  "temperature": 0.3,
  "max_tokens": 256,
  "languages": [],
  "task_types": []
}
```

### List Experiments

```http
GET /experiments
```

### Get an Experiment

```http
GET /experiments/{run_id}
```

### Compare Experiments

```http
POST /experiments/compare?run_id_a=<RUN_ID_A>&run_id_b=<RUN_ID_B>
```

## Evaluation

N-ATLaS Studio supports reproducible evaluation runs using JSONL datasets.

### Included Datasets

- `datasets/sample_evaluation.jsonl` — 20 English computer-science examples
- `datasets/multilingual_evaluation.jsonl` — 20 examples across English, Hausa, Igbo, and Yoruba
- `datasets/natlas_benchmark.jsonl` — 24 benchmark examples covering six task types across four languages

### Supported Task Types

- Question answering
- Definition
- Explanation
- Translation
- Summarization
- Classification

### Evaluation Metrics

- Exact match
- Word overlap
- Token F1
- Character similarity
- Length ratio
- Response-language accuracy

Response-language accuracy uses a lightweight language detector for benchmark analysis. It is an evaluation signal rather than a definitive linguistic benchmark.

Each evaluation run is stored as a JSON experiment record, allowing results to be retrieved and compared later.

## Experiment Tracking

Every evaluation run is assigned a unique run ID and persisted as a JSON record in the `experiments/` directory.

The Studio provides:

- Experiment history
- Retrieval of individual experiment records
- Side-by-side experiment comparison
- Metric difference reporting
- Response-language comparison

Experiments can also be accessed through the FastAPI endpoints:

```http
GET /experiments
GET /experiments/{run_id}
POST /experiments/compare
```

## Developer Workflow

A typical N-ATLaS development workflow is:

1. Start the FastAPI backend and Streamlit Studio.
2. Use the Playground to test prompts against N-ATLaS.
3. Prepare or select a JSONL evaluation dataset.
4. Run an evaluation through the Evaluation Lab.
5. Inspect results by language, task type, and domain.
6. Save the evaluation as an experiment.
7. Compare experiments to identify changes in model behavior and evaluation metrics.

This workflow is designed to support repeatable experimentation rather than one-off model interaction.

## Testing

The project includes automated tests covering providers, evaluation logic, language detection, experiment storage, and experiment comparison.

Run the test suite from the project root:

```bash
PYTHONPATH=. .venv/bin/pytest -q
```

The test suite is intended to provide a regression check before changes are committed or demonstrated.

## N-ATLaS Integration

N-ATLaS Studio is configured to use the N-ATLaS model through a provider abstraction.

The current live integration uses the `N-ATLaS-LLM` endpoint exposed by the community-hosted Gradio Space:

`seun-ajayi/n-atlas-evaluations`

The application identifies the configured model as `NCAIR1/N-ATLaS` and routes generation and chat requests through the N-ATLaS provider interface.

The provider abstraction also supports mock and configurable remote inference backends, allowing the serving mechanism to be replaced without changing the evaluation and experiment layers.

> **Important:** The current Gradio serving environment is third-party/community-hosted. It is not presented as official NCAIR infrastructure or an official N-ATLaS deployment.

## Limitations

- The current live inference backend depends on a third-party/community-hosted Gradio Space.
- The current evaluation metrics are lightweight automated signals and should not be treated as a complete semantic or human evaluation.
- Response-language accuracy uses a heuristic language detector and is intended for comparative analysis.
- The current benchmark is a development benchmark and does not represent a comprehensive evaluation of N-ATLaS.
- Production deployment would require an appropriate official or authorized N-ATLaS inference endpoint and production infrastructure.

## Challenge Positioning

N-ATLaS Studio is designed as a Developer Infrastructure solution for the N-ATLaS ecosystem.

The platform addresses the need for practical tooling that makes N-ATLaS easier to build with, evaluate, and experiment with through:

- An interactive developer playground
- Programmatic generation and chat APIs
- Provider abstraction for flexible inference backends
- Multilingual evaluation datasets
- Automated evaluation metrics
- Persistent experiment tracking
- Side-by-side experiment comparison
- A reproducible developer workflow

The project is being developed for the National AI Innovation Challenge under the Innovation & Enterprise (Track B) pathway.

## N-ATLaS Usage Notice

N-ATLaS Studio integrates with the N-ATLaS model and should be used in accordance with the applicable N-ATLaS model license and usage requirements.

Users should review the official N-ATLaS licensing terms before commercial, large-scale, or other restricted use.

Required public attribution:

> N-ATLaS is an initiative of the Federal Ministry of Communications, Innovation and Digital Economy, and powered by Awarri Technologies.

N-ATLaS Studio does not grant additional rights to the N-ATLaS model beyond those provided by its applicable license.

## Roadmap

- Connect the provider abstraction to an official or authorized N-ATLaS inference endpoint when available.
- Expand multilingual benchmark coverage and task diversity.
- Add stronger semantic evaluation methods and human evaluation workflows.
- Add dataset management and benchmark versioning.
- Improve experiment visualization and reporting.
- Add authentication and production deployment support.
- Package the platform for broader developer adoption.
