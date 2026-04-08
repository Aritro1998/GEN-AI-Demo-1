import json
import logging

from modules.llm import call_llm

logger = logging.getLogger(__name__)


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
        module_type = self.__class__.__name__

        logger.info("\n>>> [%s] Model: %s", module_type, model)
        logger.info("[%s] INPUT:\n%s", module_type, prompt)

        output = call_llm(
            model=model,
            system_prompt=step["system_prompt"],
            user_prompt=prompt,
            temperature=step["temperature"],
        )

        logger.info("[%s] RESPONSE:\n%s", module_type, output)
        return output
