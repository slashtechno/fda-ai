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
            uris = [
                "https://www.accessdata.fda.gov/drugsatfda_docs/nda/2018/210951orig1s000multidiscipliner.pdf"  ,
                # The protocol returns a forbidden error
                "https://www.nejm.org/doi/suppl/10.1056/NEJMoa1715546/suppl_file/nejmoa1715546_protocol.pdf"
            ]
            uri_and_content_id = {}
            for uri in uris:
                content_id = await ingest_uri(uri=uri)
                if content_id is None:
                    print(f'Failed to ingest content [{uri}].')
                    continue

                print(f'Ingested content [{content_id}].')
                uri_and_content_id[uri] = content_id

            prompt = "Give me the inclusion criteria for the study."

            print(f'User: {prompt}')

            message = await prompt_conversation(prompt, conversation_id)

            print(f'Assistant: {message.message.strip() if message is not None else None}')

            # await delete_content(
            #     [content_id for _, content_id in uri_and_content_id.items()]
            # )

            await delete_conversation(conversation_id)
        else:
            print('Failed to create conversation.')

        await delete_specification(specification_id)
    else:
        print('Failed to create specification.')

if __name__ == '__main__':
    asyncio.run(main())