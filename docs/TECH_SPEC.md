# Technical Specification

## LLM Strategy
- Temperature = 0
- Structured SQL output
- Prompt templates

## Query Engine
- SQL execution layer
- Error handling

## Tool Interface
class Tool:
    name: str
    def run(self, input): pass

## Connectors
- IngestFlow connector
- SentinelDQ connector
