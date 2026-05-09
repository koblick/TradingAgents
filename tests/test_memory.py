from tradingagents.agents.utils.memory import FinancialSituationMemory


class EmptyCollection:
    def count(self):
        return 0

    def query(self, *args, **kwargs):
        raise AssertionError("empty collections should not be queried")


class EmbeddingResponse:
    data = [type("EmbeddingData", (), {"embedding": [0.1, 0.2, 0.3]})()]


class RecordingEmbeddings:
    def __init__(self):
        self.input = None

    def create(self, *, model, input):
        self.input = input
        return EmbeddingResponse()


class RecordingClient:
    def __init__(self):
        self.embeddings = RecordingEmbeddings()


def test_get_memories_skips_embedding_when_collection_is_empty():
    memory = object.__new__(FinancialSituationMemory)
    memory.situation_collection = EmptyCollection()

    def fail_if_called(text):
        raise AssertionError("empty memory lookup should not embed current situation")

    memory.get_embedding = fail_if_called

    assert memory.get_memories("very long market report", n_matches=2) == []


def test_get_embedding_truncates_long_text_before_request():
    memory = object.__new__(FinancialSituationMemory)
    memory.embedding = "text-embedding-3-small"
    memory.client = RecordingClient()

    memory.get_embedding("x" * 50000)

    assert len(memory.client.embeddings.input) <= FinancialSituationMemory.MAX_EMBEDDING_CHARS
