import json
import logging

from modules.llm import call_llm

logger = logging.getLogger(__name__)


class SafeDict(dict):
    def __missing__(self, key):
        """Preserve unknown placeholders so partial templates can still render."""
        return "{" + key + "}"


class BaseModule:
    def _build_template_context(self, state, step):
        """Create the prompt-formatting context for the current pipeline step."""
        # Keep the formatting context centralized so each pipeline step can
        # reference previous outputs without repeating boilerplate mapping code.
        context = SafeDict({
            "input": state.get("input", ""),
            "original_input": state.get("original_input", ""),
            "typed_input": state.get("typed_input", ""),
            "speech_transcript": state.get("speech_transcript", ""),
            "image_findings": state.get("image_findings", ""),
            "multimodal_context": state.get("multimodal_context", ""),
            "previous_output": state.get("previous_output", ""),
            "retrieved_context": state.get("retrieved_context", ""),
            "current_step_name": step.get("name", ""),
            "current_step_id": step.get("id", ""),
            "step_outputs_json": json.dumps(state.get("step_outputs", {}), indent=2),
        })

        for key, value in state.get("step_outputs", {}).items():
            context[key] = value

        return context

    def _format_model_output_log(self, module_type, step, model, output):
        """Render a visually separated log block for a model response."""
        # A single, high-contrast block makes it easier to visually scan which
        # model produced which section when multiple stages run back-to-back.
        divider = "=" * 80
        return (
            f"\n{divider}\n"
            f"MODEL OUTPUT | step={step['id']} | module={module_type} | model={model}\n"
            f"{divider}\n"
            f"{output.strip() if isinstance(output, str) else output}\n"
            f"{divider}"
        )

    def run(self, step, state, model):
        """Build the prompt, call the model, and log the resulting output."""
        # Prompt templates are resolved at the last possible moment so they use
        # the most recent shared state from earlier pipeline stages.
        prompt = step["prompt"].format_map(self._build_template_context(state, step))
        module_type = self.__class__.__name__

        output = call_llm(
            model=model,
            system_prompt=step["system_prompt"],
            user_prompt=prompt,
            temperature=step["temperature"],
        )

        logger.info("%s", self._format_model_output_log(module_type, step, model, output))

        if not output or not str(output).strip():
            logger.warning(
                "Potential issue detected: empty model response for step=%s model=%s",
                step["id"],
                model,
            )

        return output
