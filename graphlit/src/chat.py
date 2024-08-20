from src.client import graphlit
from graphlit_api import input_types, enums, exceptions



async def create_conversation(specification_id: str):
    if graphlit.client is None:
        return;

    input = input_types.ConversationInput(name="Conversation", specification=input_types.EntityReferenceInput(id=specification_id))

    try:
        response = await graphlit.client.create_conversation(input)

        return response.create_conversation.id if response.create_conversation is not None else None
    except exceptions.GraphQLClientHttpError as e:
        print(str(e))
        return None


async def delete_conversation(conversation_id: str):
    try:
        response = await graphlit.client.delete_conversation(conversation_id)

        return response.delete_conversation.id if response.delete_conversation is not None else None
    except exceptions.GraphQLClientError as e:
        print(str(e))
        return None
    

async def prompt_conversation(prompt: str, conversation_id: str):
    try:
        response = await graphlit.client.prompt_conversation(prompt, conversation_id)

        message = response.prompt_conversation.message if response.prompt_conversation is not None else None

        return message
    except exceptions.GraphQLClientHttpError as e:
        print(str(e))
    finally:
        _ = await graphlit.client.delete_conversation(conversation_id)