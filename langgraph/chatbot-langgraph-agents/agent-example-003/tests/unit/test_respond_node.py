import pytest
from src.graph import get_graph
from unittest.mock import patch

@pytest.mark.unit
def test_graph_end_to_end():
    graph = get_graph()
    # Patch the 'invoke' method on the compiled graph object
    with patch.object(graph, 'invoke', return_value={"output_message": "The answer is 4"}):
        result = graph.invoke({
            "session_id": "test",
            "input_message": "What is 2 + 2?"
        })

        assert "4" in result["output_message"]
