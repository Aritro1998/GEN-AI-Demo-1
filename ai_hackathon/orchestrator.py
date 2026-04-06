from config import DEFAULT_MODEL, PIPELINE, RAG_CONFIG
from modules.module_factory import create_module
from modules.rag import RAG


class Orchestrator:
    def __init__(self, pipeline=None, rag_config=None, default_model=DEFAULT_MODEL):
        self.pipeline = pipeline or PIPELINE
        self.default_model = default_model

        rag_settings = rag_config or RAG_CONFIG
        if rag_settings.get("enabled"):
            self.rag = RAG(
                rag_settings["data_path"],
                rag_settings["embedding_model"],
                rag_settings.get("text_fields"),
            )
        else:
            self.rag = None

    def _normalize_step(self, step, index):
        normalized = dict(step)
        normalized.setdefault("id", f"{normalized['name']}_{index + 1}")
        normalized.setdefault("model", self.default_model)
        normalized.setdefault("temperature", 0.3)
        normalized.setdefault("system_prompt", "You are a helpful AI assistant.")
        normalized.setdefault("prompt", "Input:\n{input}")
        return normalized

    def _retrieve_context(self, step, state):
        if not (self.rag and step.get("rag")):
            return ""

        return str(self.rag.retrieve(state["input"]) or "")

    def run(self, input_text):
        state = {
            "original_input": input_text,
            "input": input_text,
            "previous_output": "",
            "retrieved_context": "",
            "step_outputs": {},
        }

        for index, raw_step in enumerate(self.pipeline):
            step = self._normalize_step(raw_step, index)
            module = create_module(step["name"])

            state["retrieved_context"] = self._retrieve_context(step, state)
            output = module.run(step=step, state=state, model=step["model"])

            state["previous_output"] = output
            state["input"] = output
            state["step_outputs"][step["id"]] = output

        return {
            "final_output": state["previous_output"],
            "step_outputs": state["step_outputs"],
        }
