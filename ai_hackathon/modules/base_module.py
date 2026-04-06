import json

from modules.llm import call_llm


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class BaseModule:
    def _build_template_context(self, state, step):
        context = SafeDict({
            "input": state.get("input", ""),
            "original_input": state.get("original_input", ""),
            "previous_output": state.get("previous_output", ""),
            "retrieved_context": state.get("retrieved_context", ""),
            "current_step_name": step.get("name", ""),
            "current_step_id": step.get("id", ""),
            "step_outputs_json": json.dumps(state.get("step_outputs", {}), indent=2),
        })

        for key, value in state.get("step_outputs", {}).items():
            context[key] = value

        return context

    def run(self, step, state, model):
        prompt = step["prompt"].format_map(self._build_template_context(state, step))
        return call_llm(
            model=model,
            system_prompt=step["system_prompt"],
            user_prompt=prompt,
            temperature=step["temperature"],
        )
