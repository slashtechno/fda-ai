from src.client import graphlit
from graphlit_api import input_types, enums, exceptions


async def ingest_uri(uri: str):
    try:
        response = await graphlit.client.ingest_uri(uri=uri, is_synchronous=True)

        return response.ingest_uri.id if response.ingest_uri is not None else None
    except exceptions.GraphQLClientError as e:
        print(str(e))
        return None

async def delete_content(content_id: str):
    try:
        response = await graphlit.client.delete_content(content_id)

        return response.delete_content.id if response.delete_content is not None else None
    except exceptions.GraphQLClientError as e:
        print(str(e))
        return None
async def create_specification():
    input = input_types.SpecificationInput(
        name="Completion",
        type=enums.SpecificationTypes.COMPLETION,
        serviceType=enums.ModelServiceTypes.OPEN_AI,
        openAI=input_types.OpenAIModelPropertiesInput(model=enums.OpenAIModels.GPT4O_128K),
        searchType=enums.ConversationSearchTypes.VECTOR,
        numberSimilar=25,
        systemPrompt="Answer with verbatim text",
        promptStrategy=input_types.PromptStrategyInput(
            type=enums.PromptStrategyTypes.OPTIMIZE_SEARCH
        ),
        retrievalStrategy=input_types.RetrievalStrategyInput(
            type=enums.RetrievalStrategyTypes.SECTION,
            contentLimit=10,
        ),
        rerankingStrategy=input_types.RerankingStrategyInput(
            serviceType=enums.RerankingModelServiceTypes.COHERE
        )
    )

    try:
        response = await graphlit.client.create_specification(input)

        return response.create_specification.id if response.create_specification is not None else None
    except exceptions.GraphQLClientError as e:
        print(str(e))
        return None
    
async def delete_specification(specification_id: str):
    try:
        response = await graphlit.client.delete_specification(specification_id)

        return response.delete_specification.id if response.delete_specification is not None else None
    except exceptions.GraphQLClientError as e:
        print(str(e))
        return None
