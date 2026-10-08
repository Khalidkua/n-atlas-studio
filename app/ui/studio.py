import json
import os
import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def api_request(
    method: str,
    endpoint: str,
    timeout: int = 60,
    **kwargs,
):
    url = f"{API_URL}{endpoint}"

    response = requests.request(
        method,
        url,
        timeout=timeout,
        **kwargs,
    )

    response.raise_for_status()

    return response.json()


def load_experiments():
    """Load saved experiments through the FastAPI backend."""

    try:
        data = api_request(
            "GET",
            "/experiments",
        )

        return data.get(
            "experiments",
            [],
        )
    except requests.RequestException:
        return []


st.set_page_config(
    page_title="N-ATLAS Studio",
    page_icon="🧠",
    layout="wide",
)


st.title("N-ATLAS Studio")

st.caption(
    "Developer, evaluation and experimentation platform for N-ATLaS"
)


page = st.sidebar.radio(
    "Navigation",
    [
        "Playground",
        "Evaluation Lab",
        "Experiment History",
        "Compare Experiments",
        "System Health",
    ],
)


# ============================================================
# ACTIVE PROVIDER
# ============================================================

try:

    provider_health = api_request(
        "GET",
        "/health",
    )

    st.sidebar.divider()

    st.sidebar.subheader(
        "Active Provider"
    )

    st.sidebar.write(
        f"**Provider:** {provider_health.get('provider', 'Unknown')}"
    )

    st.sidebar.write(
        f"**Model:** {provider_health.get('model', 'Unknown')}"
    )

    st.sidebar.write(
        f"**Status:** {provider_health.get('status', 'Unknown')}"
    )

except Exception as exc:

    st.sidebar.divider()

    st.sidebar.subheader(
        "Active Provider"
    )

    st.sidebar.error(
        f"Unavailable: {exc}"
    )


# ============================================================
# PLAYGROUND
# ============================================================

if page == "Playground":

    st.header("Playground")

    st.write(
        "Test prompts against the configured N-ATLaS provider."
    )

    prompt = st.text_area(
        "Prompt",
        placeholder="Ask N-ATLaS something...",
        height=180,
    )

    col1, col2 = st.columns(2)

    with col1:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
        )

    with col2:
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=1,
            max_value=4096,
            value=512,
            step=1,
        )

    if st.button(
        "Generate",
        type="primary",
    ):

        if not prompt.strip():
            st.warning(
                "Please enter a prompt."
            )

        else:
            with st.spinner(
                "Generating response..."
            ):
                try:
                    response = api_request(
                        "POST",
                        "/generate",
                        json={
                            "prompt": prompt,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        },
                    )

                    st.subheader(
                        "Response"
                    )

                    st.write(
                        response["response"]
                    )

                    st.caption(
                        f"Provider: {response.get('provider')} "
                        f"• Model: {response.get('model')}"
                    )

                except Exception as exc:
                    st.error(
                        f"Request failed: {exc}"
                    )


# ============================================================
# EVALUATION LAB
# ============================================================

elif page == "Evaluation Lab":

    st.header("Evaluation Lab")

    st.write(
        "Run an N-ATLaS model against a registered evaluation dataset."
    )

    try:

        dataset_response = api_request(
            "GET",
            "/datasets",
        )

        datasets = dataset_response.get(
            "datasets",
            [],
        )

    except Exception as exc:

        st.error(
            f"Unable to load datasets: {exc}"
        )

        datasets = []


    if not datasets:

        st.warning(
            "No evaluation datasets are registered."
        )

    else:

        dataset_names = [
            dataset["name"]
            for dataset in datasets
        ]

        selected_dataset = st.selectbox(
            "Select evaluation dataset",
            dataset_names,
        )

        selected_info = next(
            dataset
            for dataset in datasets
            if dataset["name"]
            == selected_dataset
        )

        st.caption(
            f"Path: {selected_info['path']} "
            f"• Format: {selected_info['format']}"
        )

        st.subheader(
            "Evaluation Configuration"
        )

        config_col1, config_col2 = st.columns(2)

        with config_col1:

            evaluation_temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key="evaluation_temperature",
            )

        with config_col2:

            evaluation_max_tokens = st.number_input(
                "Max Tokens",
                min_value=1,
                max_value=4096,
                value=512,
                step=1,
                key="evaluation_max_tokens",
            )

        st.caption(
            "Generation settings for this evaluation run."
        )

        st.subheader(
            "Evaluation Filters"
        )

        filter_col1, filter_col2 = st.columns(2)

        available_languages = selected_info.get(
            "languages",
            [],
        )

        available_task_types = selected_info.get(
            "task_types",
            [],
        )

        with filter_col1:

            selected_languages = st.multiselect(
                "Languages",
                options=available_languages,
                default=available_languages,
                key="evaluation_languages",
            )

        with filter_col2:

            selected_task_types = st.multiselect(
                "Task Types",
                options=available_task_types,
                default=available_task_types,
                key="evaluation_task_types",
            )

        st.caption(
            "Select the languages and task types to include in this evaluation run."
        )

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:

            st.metric(
                "Examples",
                selected_info.get(
                    "examples",
                    0,
                ),
            )

        with info_col2:

            languages = ", ".join(
                selected_info.get(
                    "languages",
                    [],
                )
            )

            st.metric(
                "Language",
                languages,
            )

        with info_col3:

            domains = ", ".join(
                selected_info.get(
                    "domains",
                    [],
                )
            )

            st.metric(
                "Domain",
                domains,
            )


        if st.button(
            "Run Evaluation",
            type="primary",
        ):

            with st.spinner(
                f"Running evaluation on {selected_dataset}..."
            ):

                try:

                    response = api_request(
                        "POST",
                        "/evaluate",
                        timeout=300,
                       json={
    "dataset_path": selected_info[
        "path"
    ],
    "temperature": evaluation_temperature,
    "max_tokens": evaluation_max_tokens,
    "languages": selected_languages,
    "task_types": selected_task_types,
},
                    )

                    st.success(
                        "Evaluation completed successfully."
                    )

                    st.subheader(
                        "Evaluation Summary"
                    )

                    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

                    with col1:

                        st.metric(
                            "Examples",
                            response[
                                "total_examples"
                            ],
                        )

                    with col2:

                        st.metric(
                            "Exact Match",
                            f"{response['metrics']['exact_match']:.2%}",
                        )

                    with col3:

                        st.metric(
                            "Word Overlap",
                            f"{response['metrics']['word_overlap']:.2%}",
                        )

                    with col4:

                        st.metric(
                            "Token F1",
                            f"{response['metrics'].get('token_f1', 0.0):.2%}",
                        )

                    with col5:

                        st.metric(
                            "Character Similarity",
                            f"{response['metrics'].get('character_similarity', 0.0):.2%}",
                        )

                    with col6:

                        st.metric(
                            "Length Ratio",
                            f"{response['metrics'].get('length_ratio', 0.0):.2f}x",
                        )

                    with col7:

                        st.metric(
                            "Response Language",
                            f"{response['metrics'].get('response_language_accuracy', 0.0):.2%}",
                        )


                    st.subheader(
                        "Experiment"
                    )

                    st.code(
                        response["run_id"],
                        language="text",
                    )

                    st.subheader(
                        "Export Evaluation"
                    )

                    export_col1, export_col2 = st.columns(2)

                    json_export = json.dumps(
                        response,
                        indent=2,
                        ensure_ascii=False,
                    )

                    with export_col1:
                        st.download_button(
                            "Download JSON",
                            data=json_export,
                            file_name=(
                                f"evaluation_"
                                f"{response['run_id']}.json"
                            ),
                            mime="application/json",
                        )

                    csv_rows = response.get(
                        "results",
                        [],
                    )

                    if csv_rows:
                        import csv
                        from io import StringIO

                        csv_buffer = StringIO()

                        csv_writer = csv.DictWriter(
                            csv_buffer,
                            fieldnames=[
                                "id",
                                "language",
                                "domain",
                                "task_type",
                                "prompt",
                                "reference_answer",
                                "generated_answer",
                                "generated_word_count",
                                "reference_word_count",
                                "exact_match",
                                "word_overlap",
                                "token_f1",
                                "character_similarity",
                                "length_ratio",
                                "expected_response_language",
                                "detected_language",
                                "language_match",
                                "language_detection_confidence",
                            ],
                        )

                        csv_writer.writeheader()

                        for result in csv_rows:
                            csv_writer.writerow(
                                {
                                    "id": result.get("id", ""),
                                    "language": result.get("language", ""),
                                    "domain": result.get("domain", ""),
                                    "task_type": result.get("task_type", ""),
                                    "prompt": result.get("prompt", ""),
                                    "reference_answer": result.get(
                                        "reference_answer",
                                        "",
                                    ),
                                    "generated_answer": result.get(
                                        "generated_answer",
                                        "",
                                    ),
                                    "generated_word_count": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "generated_word_count",
                                        0,
                                    ),
                                    "reference_word_count": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "reference_word_count",
                                        0,
                                    ),
                                    "exact_match": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "exact_match",
                                        0.0,
                                    ),
                                    "word_overlap": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "word_overlap",
                                        0.0,
                                    ),
                                    "token_f1": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "token_f1",
                                        0.0,
                                    ),
                                    "character_similarity": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "character_similarity",
                                        0.0,
                                    ),
                                    "length_ratio": result.get(
                                        "metrics",
                                        {},
                                    ).get(
                                        "length_ratio",
                                        0.0,
                                    ),
                                    "expected_response_language": result.get(
                                        "expected_response_language",
                                        "",
                                    ),
                                    "detected_language": result.get(
                                        "detected_language",
                                        "",
                                    ),
                                    "language_match": result.get(
                                        "language_match",
                                        "",
                                    ),
                                    "language_detection_confidence": result.get(
                                        "language_detection_confidence",
                                        0.0,
                                    ),
                                }
                            )

                        csv_export = csv_buffer.getvalue()

                        with export_col2:
                            st.download_button(
                                "Download CSV",
                                data=csv_export,
                                file_name=(
                                    f"evaluation_"
                                    f"{response['run_id']}.csv"
                                ),
                                mime="text/csv",
                            )


                    st.subheader(
                        "Evaluation Results"
                    )

                      # =========================================
                    # LANGUAGE PERFORMANCE
                    # =========================================

                    st.subheader(
                        "Language Performance"
                    )

                    language_metrics = response.get(
                        "by_language",
                        {},
                    )

                    if language_metrics:

                        language_rows = []

                        for language, metrics in language_metrics.items():

                            language_rows.append(
                                {
                                    "Language": language,
                                    "Examples": metrics["examples"],
                                    "Exact Match": metrics["exact_match"],
                                    "Word Overlap": metrics["word_overlap"],
                                    "Token F1": metrics.get("token_f1", 0.0),
                                    "Character Similarity": metrics.get(
                                        "character_similarity",
                                        0.0,
                                    ),
                                    "Response Language": metrics.get(
                                        "response_language_accuracy",
                                        0.0,
                                    ),
                                }
                            )

                        display_language_rows = []

                        for row in language_rows:

                            display_language_rows.append(
                                {
                                    "Language": row["Language"],
                                    "Examples": row["Examples"],
                                    "Exact Match": f"{row['Exact Match']:.2%}",
                                    "Word Overlap": f"{row['Word Overlap']:.2%}",
                                    "Token F1": f"{row['Token F1']:.2%}",
                                    "Character Similarity": (
                                        f"{row['Character Similarity']:.2%}"
                                    ),
                                    "Response Language": (
                                        f"{row['Response Language']:.2%}"
                                    ),
                                }
                            )

                        st.table(
                            display_language_rows
                        )

                        st.markdown(
                            "#### Language Performance Chart"
                        )

                        import pandas as pd

                        language_chart_df = pd.DataFrame(
                            language_rows
                        ).set_index(
                            "Language"
                        )[
                            [
                                "Exact Match",
                                "Word Overlap",
                                "Token F1",
                                "Character Similarity",
                                "Response Language",
                            ]
                        ]

                        st.bar_chart(
                            language_chart_df,
                            use_container_width=True,
                        )

                    else:

                        st.info(
                            "No language-level metrics available."
                        )


                    # =========================================
                    # DOMAIN PERFORMANCE
                    # =========================================

                    st.subheader(
                        "Domain Performance"
                    )

                    domain_metrics = response.get(
                        "by_domain",
                        {},
                    )

                    if domain_metrics:

                        domain_rows = []

                        for domain, metrics in domain_metrics.items():

                            domain_rows.append(
                                {
                                    "Domain": domain,
                                    "Examples": metrics["examples"],
                                    "Exact Match": metrics["exact_match"],
                                    "Word Overlap": metrics["word_overlap"],
                                    "Token F1": metrics.get("token_f1", 0.0),
                                    "Character Similarity": metrics.get(
                                        "character_similarity",
                                        0.0,
                                    ),
                                    "Response Language": metrics.get(
                                        "response_language_accuracy",
                                        0.0,
                                    ),
                                }
                            )

                        display_domain_rows = []

                        for row in domain_rows:

                            display_domain_rows.append(
                                {
                                    "Domain": row["Domain"],
                                    "Examples": row["Examples"],
                                    "Exact Match": f"{row['Exact Match']:.2%}",
                                    "Word Overlap": f"{row['Word Overlap']:.2%}",
                                    "Token F1": f"{row['Token F1']:.2%}",
                                    "Character Similarity": (
                                        f"{row['Character Similarity']:.2%}"
                                    ),
                                    "Response Language": (
                                        f"{row['Response Language']:.2%}"
                                    ),
                                }
                            )

                        st.table(
                            display_domain_rows
                        )

                        st.markdown(
                            "#### Domain Performance Chart"
                        )

                        domain_chart_df = pd.DataFrame(
                            domain_rows
                        ).set_index(
                            "Domain"
                        )[
                            [
                                "Exact Match",
                                "Word Overlap",
                                "Token F1",
                                "Character Similarity",
                                "Response Language",
                            ]
                        ]

                        st.bar_chart(
                            domain_chart_df,
                            use_container_width=True,
                        )

                    else:

                        st.info(
                            "No domain-level metrics available."
                        )


                    # =========================================
                    # TASK PERFORMANCE
                    # =========================================

                    st.subheader(
                        "Task Performance"
                    )

                    task_metrics = response.get(
                        "by_task_type",
                        {},
                    )

                    if task_metrics:

                        task_rows = []

                        for task_type, metrics in task_metrics.items():

                            task_rows.append(
                                {
                                    "Task Type": task_type,
                                    "Examples": metrics["examples"],
                                    "Exact Match": metrics["exact_match"],
                                    "Word Overlap": metrics["word_overlap"],
                                    "Token F1": metrics.get("token_f1", 0.0),
                                    "Character Similarity": metrics.get(
                                        "character_similarity",
                                        0.0,
                                    ),
                                    "Response Language": metrics.get(
                                        "response_language_accuracy",
                                        0.0,
                                    ),
                                }
                            )

                        display_task_rows = []

                        for row in task_rows:

                            display_task_rows.append(
                                {
                                    "Task Type": row["Task Type"],
                                    "Examples": row["Examples"],
                                    "Exact Match": f"{row['Exact Match']:.2%}",
                                    "Word Overlap": f"{row['Word Overlap']:.2%}",
                                    "Token F1": f"{row['Token F1']:.2%}",
                                    "Character Similarity": (
                                        f"{row['Character Similarity']:.2%}"
                                    ),
                                    "Response Language": (
                                        f"{row['Response Language']:.2%}"
                                    ),
                                }
                            )

                        st.table(
                            display_task_rows
                        )

                        st.markdown(
                            "#### Task Performance Chart"
                        )

                        task_chart_df = pd.DataFrame(
                            task_rows
                        ).set_index(
                            "Task Type"
                        )[
                            [
                                "Exact Match",
                                "Word Overlap",
                                "Token F1",
                                "Character Similarity",
                                "Response Language",
                            ]
                        ]

                        st.bar_chart(
                            task_chart_df,
                            use_container_width=True,
                        )

                    else:

                        st.info(
                            "No task-level metrics available."
                        )


                    results = response.get(
                        "results",
                        [],
                    )

                    for result in results:

                        with st.expander(
                            result["id"]
                        ):

                            st.write(
                                "**Prompt:**"
                            )

                            st.write(
                                result["prompt"]
                            )

                            st.write(
                                "**Reference Answer:**"
                            )

                            st.write(
                                result["reference_answer"]
                            )

                            st.write(
                                "**Generated Answer:**"
                            )

                            st.write(
                                result["generated_answer"]
                            )

                            metric_col1, metric_col2, metric_col3, metric_col4, metric_col5, metric_col6, metric_col7 = st.columns(7)

                            with metric_col1:

                                st.metric(
                                    "Exact Match",
                                    f"{result['metrics']['exact_match']:.2%}",
                                )

                            with metric_col2:

                                st.metric(
                                    "Word Overlap",
                                    f"{result['metrics']['word_overlap']:.2%}",
                                )

                            with metric_col3:

                                st.metric(
                                    "Token F1",
                                    f"{result['metrics'].get('token_f1', 0.0):.2%}",
                                )

                            with metric_col4:

                                st.metric(
                                    "Character Similarity",
                                    f"{result['metrics'].get('character_similarity', 0.0):.2%}",
                                )

                            with metric_col5:

                                st.metric(
                                    "Generated Words",
                                    result["metrics"].get(
                                        "generated_word_count",
                                        0,
                                    ),
                                )

                            with metric_col6:

                                st.metric(
                                    "Reference Words",
                                    result["metrics"].get(
                                        "reference_word_count",
                                        0,
                                    ),
                                )

                            with metric_col7:

                                st.metric(
                                    "Length Ratio",
                                    f"{result['metrics'].get('length_ratio', 0.0):.2f}x",
                                )

                            st.markdown(
                                "#### Response Language"
                            )

                            language_col1, language_col2, language_col3, language_col4 = st.columns(4)

                            with language_col1:

                                st.metric(
                                    "Expected",
                                    result.get(
                                        "expected_response_language",
                                        "unknown",
                                    ),
                                )

                            with language_col2:

                                st.metric(
                                    "Detected",
                                    result.get(
                                        "detected_language",
                                        "unknown",
                                    ),
                                )

                            with language_col3:

                                language_match = result.get(
                                    "language_match"
                                )

                                st.metric(
                                    "Match",
                                    (
                                        "Yes"
                                        if language_match is True
                                        else "No"
                                        if language_match is False
                                        else "Unknown"
                                    ),
                                )

                            with language_col4:

                                st.metric(
                                    "Confidence",
                                    f"{result.get('language_detection_confidence', 0.0):.2%}",
                                )

                except Exception as exc:

                    st.error(
                        f"Evaluation failed: {exc}"
                    )


# ============================================================
# EXPERIMENT HISTORY
# ============================================================

elif page == "Experiment History":

    st.header(
        "Experiment History"
    )

    experiments = load_experiments()

    if not experiments:

        st.info(
            "No experiments have been saved yet."
        )

    else:

        st.write(
            f"{len(experiments)} experiment(s) found."
        )

        for experiment in experiments:

            run_id = experiment.get(
                "run_id",
                "Unknown",
            )

            dataset = experiment.get(
                "dataset",
                "Unknown",
            )

            provider = experiment.get(
                "provider",
                "Unknown",
            )

            model = experiment.get(
                "model",
                "Unknown",
            )

            metrics = experiment.get(
                "metrics",
                {},
            )

            with st.expander(
                run_id
            ):

                st.write(
                    f"**Dataset:** {dataset}"
                )

                st.write(
                    f"**Provider:** {provider}"
                )

                st.write(
                    f"**Model:** {model}"
                )

                st.write(
                    f"**Temperature:** {experiment.get('temperature', 0.7)}"
                )

                st.write(
                    f"**Max Tokens:** {experiment.get('max_tokens', 512)}"
                )

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:

                    st.metric(
                        "Exact Match",
                        f"{metrics.get('exact_match', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Word Overlap",
                        f"{metrics.get('word_overlap', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Token F1",
                        f"{metrics.get('token_f1', 0.0):.2%}",
                    )

                with col4:

                    st.metric(
                        "Character Similarity",
                        f"{metrics.get('character_similarity', 0.0):.2%}",
                    )

                with col5:

                    st.metric(
                        "Response Language",
                        f"{metrics.get('response_language_accuracy', 0.0):.2%}",
                    )


# ============================================================
# COMPARE EXPERIMENTS
# ============================================================

elif page == "Compare Experiments":

    st.header(
        "Compare Experiments"
    )

    experiments = load_experiments()

    if len(experiments) < 2:

        st.info(
            "At least two experiments are required for comparison."
        )

    else:

        experiment_map = {
            experiment["run_id"]: experiment
            for experiment in experiments
        }

        run_ids = list(
            experiment_map.keys()
        )

        col1, col2 = st.columns(2)

        with col1:

            run_id_a = st.selectbox(
                "Experiment A",
                run_ids,
            )

        with col2:

            run_id_b = st.selectbox(
                "Experiment B",
                run_ids,
                index=1,
            )


        if st.button(
            "Compare",
            type="primary",
        ):

            try:

                response = api_request(
                    "POST",
                    "/experiments/compare",
                    params={
                        "run_id_a": run_id_a,
                        "run_id_b": run_id_b,
                    },
                )

                st.subheader(
                    "Comparison"
                )

                experiment_a = response.get(
                    "experiment_a",
                    {},
                )

                experiment_b = response.get(
                    "experiment_b",
                    {},
                )

                st.write(
                    "### Experiment Configuration"
                )

                config_data = {
                    "Property": [
                        "Run ID",
                        "Dataset",
                        "Provider",
                        "Model",
                        "Temperature",
                        "Max Tokens",
                        "Languages",
                        "Task Types",
                    ],
                    "Experiment A": [
                        experiment_a.get("run_id", "Unknown"),
                        experiment_a.get("dataset", "Unknown"),
                        experiment_a.get("provider", "Unknown"),
                        experiment_a.get("model", "Unknown"),
                        experiment_a.get("temperature", 0.7),
                        experiment_a.get("max_tokens", 512),
                        ", ".join(experiment_a.get("languages", [])) or "All",
                        ", ".join(experiment_a.get("task_types", [])) or "All",
                    ],
                    "Experiment B": [
                        experiment_b.get("run_id", "Unknown"),
                        experiment_b.get("dataset", "Unknown"),
                        experiment_b.get("provider", "Unknown"),
                        experiment_b.get("model", "Unknown"),
                        experiment_b.get("temperature", 0.7),
                        experiment_b.get("max_tokens", 512),
                        ", ".join(experiment_b.get("languages", [])) or "All",
                        ", ".join(experiment_b.get("task_types", [])) or "All",
                    ],
                }

                st.table(config_data)

                metrics = response.get(
                    "metrics",
                    {},
                )

                exact = metrics.get(
                    "exact_match",
                    {},
                )

                overlap = metrics.get(
                    "word_overlap",
                    {},
                )

                token_f1 = metrics.get(
                    "token_f1",
                    {},
                )

                character_similarity = metrics.get(
                    "character_similarity",
                    {},
                )

                length = metrics.get(
                    "length_ratio",
                    {},
                )

                response_language = metrics.get(
                    "response_language_accuracy",
                    {},
                )

                st.write(
                    "### Exact Match"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{exact.get('experiment_a', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{exact.get('experiment_b', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{exact.get('difference', 0.0):+.2%}",
                    )


                st.write(
                    "### Word Overlap"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{overlap.get('experiment_a', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{overlap.get('experiment_b', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{overlap.get('difference', 0.0):+.2%}",
                    )



                st.write(
                    "### Token F1"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{token_f1.get('experiment_a', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{token_f1.get('experiment_b', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{token_f1.get('difference', 0.0):+.2%}",
                    )


                st.write(
                    "### Character Similarity"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{character_similarity.get('experiment_a', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{character_similarity.get('experiment_b', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{character_similarity.get('difference', 0.0):+.2%}",
                    )


                st.write(
                    "### Length Ratio"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{length.get('experiment_a', 0.0):.2f}x",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{length.get('experiment_b', 0.0):.2f}x",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{length.get('difference', 0.0):+.2f}x",
                    )


                st.write(
                    "### Response Language"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Experiment A",
                        f"{response_language.get('experiment_a', 0.0):.2%}",
                    )

                with col2:

                    st.metric(
                        "Experiment B",
                        f"{response_language.get('experiment_b', 0.0):.2%}",
                    )

                with col3:

                    st.metric(
                        "Difference",
                        f"{response_language.get('difference', 0.0):+.2%}",
                    )


                st.write(
                    "### Metric Comparison"
                )

                chart_data = {
                    "Metric": [
                        "Exact Match",
                        "Word Overlap",
                        "Token F1",
                        "Character Similarity",
                        "Response Language",
                    ],
                    "Experiment A": [
                        exact.get("experiment_a", 0.0),
                        overlap.get("experiment_a", 0.0),
                        token_f1.get("experiment_a", 0.0),
                        character_similarity.get(
                            "experiment_a",
                            0.0,
                        ),
                        response_language.get(
                            "experiment_a",
                            0.0,
                        ),
                    ],
                    "Experiment B": [
                        exact.get("experiment_b", 0.0),
                        overlap.get("experiment_b", 0.0),
                        token_f1.get("experiment_b", 0.0),
                        character_similarity.get(
                            "experiment_b",
                            0.0,
                        ),
                        response_language.get(
                            "experiment_b",
                            0.0,
                        ),
                    ],
                }

                st.bar_chart(
                    chart_data,
                    x="Metric",
                    y=[
                        "Experiment A",
                        "Experiment B",
                    ],
                )

            except Exception as exc:

                st.error(
                    f"Comparison failed: {exc}"
                )


# ============================================================
# SYSTEM HEALTH
# ============================================================

elif page == "System Health":

    st.header(
        "System Health"
    )

    st.write(
        "Monitor the N-ATLaS Studio API, provider, model, "
        "datasets, and saved experiments."
    )

    if st.button(
        "Check Health",
        type="primary",
    ):

        try:

            health_response = api_request(
                "GET",
                "/health",
            )

            dataset_response = api_request(
                "GET",
                "/datasets",
            )

            experiments = load_experiments()

            st.success(
                "System is healthy."
            )

            st.subheader(
                "System Overview"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "API",
                    "Online",
                )

            with col2:

                st.metric(
                    "Provider",
                    health_response.get(
                        "provider",
                        "Unknown",
                    ),
                )

            with col3:

                st.metric(
                    "Datasets",
                    len(
                        dataset_response.get(
                            "datasets",
                            [],
                        )
                    ),
                )

            with col4:

                st.metric(
                    "Experiments",
                    len(experiments),
                )

            st.subheader(
                "Active Model"
            )

            model_col1, model_col2 = st.columns(2)

            with model_col1:

                st.write(
                    f"**Model:** "
                    f"{health_response.get('model', 'Unknown')}"
                )

            with model_col2:

                st.write(
                    f"**Provider Status:** "
                    f"{health_response.get('status', 'Unknown')}"
                )

            st.subheader(
                "Provider Health Response"
            )

            st.json(
                health_response
            )

            st.subheader(
                "Registered Datasets"
            )

            datasets = dataset_response.get(
                "datasets",
                [],
            )

            if datasets:

                dataset_rows = []

                for dataset in datasets:

                    dataset_rows.append(
                        {
                            "Name": dataset.get(
                                "name",
                                "Unknown",
                            ),
                            "Format": dataset.get(
                                "format",
                                "Unknown",
                            ),
                            "Examples": dataset.get(
                                "examples",
                                0,
                            ),
                            "Languages": ", ".join(
                                dataset.get(
                                    "languages",
                                    [],
                                )
                            ),
                            "Domains": ", ".join(
                                dataset.get(
                                    "domains",
                                    [],
                                )
                            ),
                        }
                    )

                st.table(
                    dataset_rows
                )

            else:

                st.info(
                    "No registered datasets found."
                )

            st.subheader(
                "Saved Experiments"
            )

            if experiments:

                experiment_rows = []

                for experiment in experiments:

                    experiment_rows.append(
                        {
                            "Run ID": experiment.get(
                                "run_id",
                                "Unknown",
                            ),
                            "Dataset": experiment.get(
                                "dataset",
                                "Unknown",
                            ),
                            "Provider": experiment.get(
                                "provider",
                                "Unknown",
                            ),
                            "Model": experiment.get(
                                "model",
                                "Unknown",
                            ),
                            "Timestamp": experiment.get(
                                "timestamp",
                                "Unknown",
                            ),
                        }
                    )

                st.dataframe(
                    experiment_rows,
                    use_container_width=True,
                )

            else:

                st.info(
                    "No saved experiments found."
                )

        except Exception as exc:

            st.error(
                f"Health check failed: {exc}"
            )
