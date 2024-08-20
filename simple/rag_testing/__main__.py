from rag_testing import load, query


def main():
    load.remove_chunks_by_filename("data\\nejmoa1715546_protocol.pdf")
    load.remove_chunks_by_filename("data\\210951Orig1s000MultidisciplineR.pdf")
    load.main()
    # query.query_rag("How many players can play Monopoly? Give me the range.")
    query.query_rag(
        "Give me the detailed inclusion and exclusion criteria"
    )
    # query.query_rag(input("Enter your query: "))


if __name__ == "__main__":
    main()
