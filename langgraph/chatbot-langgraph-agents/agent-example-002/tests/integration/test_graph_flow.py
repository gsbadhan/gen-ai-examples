import pytest
from src.graph import get_graph


@pytest.mark.integration
def test_graph_end_to_end():
    graph = get_graph()
    result = graph.invoke({
        "session_id": "user_test_001",
        "input_message": "Capital of France?"
    })
    assert "Paris" in result["output_message"]
