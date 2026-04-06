# Lean AI Hackathon Starter

This project is a small, configurable starter for AI hackathons.

The idea is simple:

- keep the framework code minimal
- customize only the pipeline and prompts
- optionally add a small RAG knowledge file for the specific problem you get

You should not need to create multiple workflows or manage a large config during the hackathon.

## What to edit during the hackathon

In most cases, you only need to touch:

1. `config.py`
2. `app.py`
3. `data/knowledge.json`

## How it works

The pipeline is defined in `config.py` as a list of steps.

Each step has:

- `name`: module type such as `classifier`, `reasoner`, or `generator`
- `id`: step output name
- `prompt`: prompt template
- optional `model`
- optional `system_prompt`
- optional `temperature`
- optional `rag`

Example:

```python
PIPELINE = [
    {
        "name": "classifier",
        "id": "classification",
        "prompt": "Input:\n{original_input}\n\nReturn only a short category label.",
        "temperature": 0.0,
    },
    {
        "name": "reasoner",
        "id": "analysis",
        "rag": True,
        "prompt": "Input:\n{original_input}\n\nCategory:\n{classification}\n\nContext:\n{retrieved_context}",
    },
    {
        "name": "generator",
        "id": "final_output",
        "prompt": "Input:\n{original_input}\n\nAnalysis:\n{analysis}\n\nWrite the final answer.",
    },
]
```

## Available prompt variables

Inside prompts you can use:

- `{input}`
- `{original_input}`
- `{previous_output}`
- `{retrieved_context}`
- `{step_outputs_json}`
- `{<step_id>}` from any previous step

Example:

```python
"prompt": "Problem:\n{original_input}\n\nReasoning:\n{analysis}\n\nGenerate final output."
```

## Setup

1. Create a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create `.env`.

```bash
cp .env.example .env
```

4. Fill in:

- `OPENAI_API_KEY`
- `BASE_URL`

Optional:

- `DEFAULT_MODEL`
- `CLASSIFIER_MODEL`
- `EMBEDDING_MODEL`

## Running the project

Edit the `input_text` variable in `app.py`, then run:

```bash
python3 app.py
```

## Fast customization flow

When you get the actual problem statement:

1. Paste the real problem statement into `app.py`
2. Update the prompts in `config.py`
3. Add 3-10 relevant knowledge entries in `data/knowledge.json`
4. Run `python3 app.py`

That is the intended workflow.

## When to change the pipeline

Use a short 3-step pipeline if you want to move fast:

- classify
- reason
- generate

Use a 4-step pipeline if you need an intermediate draft:

- classifier
- generator
- reasoner
- generator

If the task is simple, you can even remove the classifier step and just keep:

- reasoner
- generator

## RAG guidance

RAG is optional and controlled by `RAG_CONFIG` in `config.py`.

If the problem needs grounding, keep it enabled and add compact entries to `data/knowledge.json`.

If the problem does not need retrieval, set:

```python
RAG_CONFIG = {
    "enabled": False,
    ...
}
```

## Files in the project

- `app.py`: small entry point
- `config.py`: main place to customize the pipeline
- `orchestrator.py`: runs the pipeline
- `modules/`: minimal module framework
- `data/knowledge.json`: optional RAG context

## Notes

- RAG embeddings are created when the orchestrator starts, so retrieval needs a working embedding model and endpoint.
- The framework is intentionally small. Most of the customization should happen through prompts.
