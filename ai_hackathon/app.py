from orchestrator import Orchestrator


if __name__ == "__main__":
    input_text = """
    Example problem:
    Build an AI assistant that reviews application logs and metrics, identifies the likely bottleneck,
    and generates a short explanation with suggested next steps.
    """

    orchestrator = Orchestrator()
    result = orchestrator.run(input_text.strip())

    print(result["final_output"])
