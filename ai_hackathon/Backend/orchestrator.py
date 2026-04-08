import logging

from config import DEFAULT_MODEL, PIPELINE, PREPROCESSING_PIPELINE, RAG_CONFIG
from modules.llm import call_vision_model, transcribe_audio
from modules.module_factory import create_module
from modules.rag import RAG

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        pipeline=None,
        preprocessing_pipeline=None,
        rag_config=None,
        default_model=DEFAULT_MODEL,
    ):
        """Prepare the pipeline configuration and optional retriever."""
        # Pipeline defaults stay configurable so individual stages can be swapped
        # during testing without changing the orchestration logic itself.
        self.pipeline = pipeline or PIPELINE
        self.preprocessing_pipeline = preprocessing_pipeline or PREPROCESSING_PIPELINE
        self.default_model = default_model

        rag_settings = rag_config or RAG_CONFIG
        if rag_settings.get("enabled"):
            # Build the retriever once during startup so each request reuses the
            # same knowledge index instead of recomputing embeddings repeatedly.
            self.rag = RAG(
                rag_settings["data_path"],
                rag_settings["embedding_model"],
                rag_settings.get("text_fields"),
            )
        else:
            self.rag = None

    def _normalize_step(self, step, index):
        """Fill in any omitted step fields with safe defaults."""
        normalized = dict(step)
        # Fill in safe defaults so each pipeline step only needs to define the
        # fields it truly customizes.
        normalized.setdefault("id", f"{normalized['name']}_{index + 1}")
        normalized.setdefault("model", self.default_model)
        normalized.setdefault("temperature", 0.3)
        normalized.setdefault("system_prompt", "You are a helpful AI assistant.")
        normalized.setdefault("prompt", "Input:\n{input}")
        normalized.setdefault("capability", "text")
        return normalized

    def _build_context(self, state, step=None):
        """Build a minimal formatting context shared across all pipeline stages."""
        current_step = step or {}
        return {
            "input": state.get("input", ""),
            "original_input": state.get("original_input", ""),
            "typed_input": state.get("typed_input", ""),
            "speech_transcript": state.get("speech_transcript", ""),
            "image_findings": state.get("image_findings", ""),
            "multimodal_context": state.get("multimodal_context", ""),
            "retrieved_context": state.get("retrieved_context", ""),
            "previous_output": state.get("previous_output", ""),
            "current_step_name": current_step.get("name", ""),
            "current_step_id": current_step.get("id", ""),
        }

    def _format_model_output_log(self, step, output):
        """Render a visually separated log block for preprocessing model outputs."""
        divider = "=" * 80
        return (
            f"\n{divider}\n"
            f"MODEL OUTPUT | step={step['id']} | capability={step['capability']} | "
            f"model={step['model']}\n"
            f"{divider}\n"
            f"{output.strip() if isinstance(output, str) else output}\n"
            f"{divider}"
        )

    def _compose_original_input(self, state):
        """Merge typed, spoken, and visual evidence into one troubleshooting input."""
        sections = []
        typed_input = state.get("typed_input", "").strip()
        speech_transcript = state.get("speech_transcript", "").strip()
        image_findings = state.get("image_findings", "").strip()

        if typed_input:
            sections.append(f"Typed issue description:\n{typed_input}")
        if speech_transcript:
            sections.append(f"Speech transcript:\n{speech_transcript}")
        if image_findings:
            sections.append(f"Screenshot analysis:\n{image_findings}")

        combined = "\n\n".join(sections).strip()
        state["multimodal_context"] = combined
        state["original_input"] = combined
        state["input"] = combined

    def _run_preprocessing(self, state, audio_path=None, image_paths=None):
        """Normalize speech and screenshots before the text pipeline begins."""
        for index, raw_step in enumerate(self.preprocessing_pipeline):
            step = self._normalize_step(raw_step, index)
            input_key = step.get("input_key")

            if input_key == "audio_path" and audio_path:
                output = transcribe_audio(
                    model=step["model"],
                    audio_path=audio_path,
                    prompt=step.get("prompt"),
                )
                state[step["id"]] = output
                logger.info("%s", self._format_model_output_log(step, output))
            elif input_key == "image_paths" and image_paths:
                prompt = step["prompt"].format_map(self._build_context(state, step))
                output = call_vision_model(
                    model=step["model"],
                    system_prompt=step["system_prompt"],
                    user_prompt=prompt,
                    image_paths=image_paths,
                    temperature=step["temperature"],
                )
                state[step["id"]] = output
                logger.info("%s", self._format_model_output_log(step, output))

        self._compose_original_input(state)

    def _retrieve_context(self, step, state):
        """Fetch retrieval context only for steps that opt into RAG."""
        if not (self.rag and step.get("rag")):
            return ""

        # Retrieval is opt-in per step, which keeps lightweight stages from
        # paying the embedding lookup cost unnecessarily.
        return str(self.rag.retrieve(state["input"]) or "")

    def run(self, input_text="", audio_path=None, image_paths=None):
        """Execute preprocessing, then run each text step in order."""
        # Shared state is passed from one stage to the next so later prompts can
        # reuse earlier outputs without tightly coupling the modules together.
        state = {
            "typed_input": (input_text or "").strip(),
            "original_input": (input_text or "").strip(),
            "input": (input_text or "").strip(),
            "speech_transcript": "",
            "image_findings": "",
            "multimodal_context": "",
            "previous_output": "",
            "retrieved_context": "",
            "step_outputs": {},
        }

        try:
            self._run_preprocessing(
                state=state,
                audio_path=audio_path,
                image_paths=image_paths or [],
            )

            for index, raw_step in enumerate(self.pipeline):
                step = self._normalize_step(raw_step, index)
                module = create_module(step["name"])

                state["retrieved_context"] = self._retrieve_context(step, state)
                output = module.run(step=step, state=state, model=step["model"])

                # The latest output becomes the next step's input, while each
                # individual step result is still preserved for prompt templating.
                state["previous_output"] = output
                state["input"] = output
                state["step_outputs"][step["id"]] = output
        except Exception:
            logger.exception("Pipeline execution failed")
            raise

        return {
            "final_output": state["previous_output"],
            "step_outputs": state["step_outputs"],
            "speech_transcript": state["speech_transcript"],
            "image_findings": state["image_findings"],
            "combined_input": state["original_input"],
        }
