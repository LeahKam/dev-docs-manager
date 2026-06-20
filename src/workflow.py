from llama_index.core.workflow import Workflow, StartEvent, StopEvent, step, Context, Event


class RetrievalDoneEvent(Event):
    nodes: list
    query: str


class RAGWorkflow(Workflow):
    def __init__(self, retriever, response_synthesizer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retriever = retriever
        self.response_synthesizer = response_synthesizer

    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> RetrievalDoneEvent:
        query = ev.get("query")
        nodes = self.retriever.retrieve(query)
        return RetrievalDoneEvent(nodes=nodes, query=query)

    @step
    async def synthesize(self, ctx: Context, ev: RetrievalDoneEvent) -> StopEvent:
        if not ev.nodes:
            return StopEvent(result="No relevant context found.")

        response = self.response_synthesizer.synthesize(ev.query, nodes=ev.nodes)
        return StopEvent(result=str(response))
