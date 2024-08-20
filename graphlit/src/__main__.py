from src.chat import create_conversation, delete_conversation, prompt_conversation
from src.ingest import create_specification, delete_specification, ingest_uri, delete_content
import asyncio


async def main(): 
    specification_id = await create_specification()

    if specification_id is not None:
        print(f'Created specification [{specification_id}].')

        conversation_id = await create_conversation(specification_id)

        if conversation_id is not None:
            print(f'Created conversation [{conversation_id}].')

            content_id = await ingest_uri(uri="https://www.accessdata.fda.gov/drugsatfda_docs/nda/2018/210951orig1s000multidiscipliner.pdf")

            if content_id is not None:
                print(f'Ingested content [{content_id}].')

                prompt = "Who was the Clinical Team Leader?"

                print(f'User: {prompt}')

                message = await prompt_conversation(prompt, conversation_id)

                print(f'Assistant: {message.message.strip() if message is not None else None}')

                await delete_content(content_id)
            else:
                print('Failed to ingest content.')

            await delete_conversation(conversation_id)
        else:
            print('Failed to create conversation.')

        await delete_specification(specification_id)
    else:
        print('Failed to create specification.')

if __name__ == '__main__':
    asyncio.run(main())