#!/usr/bin/env python

from utils import rhyme_pattern, slant_distance, n_syllables

if __name__ == "__main__":
    """
    Create neo4j database to house the words and patterns.
    """
    import os
    import cmudict
    from neo4j import GraphDatabase
    from itertools import product

    
    D = cmudict.dict()

    USERNAME = os.environ["NEO4J_USERNAME"]
    PASSWORD = os.environ["NEO4J_PASSWORD"]
    URI = os.environ["NEO4J_URI"]

    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

    with open('words.txt', 'r') as fh:
        words = fh.read().strip().split('\n')

    with driver.session() as session:
        for word in words:
            for pron_list in D[word]:
                pron_str = ' '.join(pron_list)
                rp_pron_str = rhyme_pattern(pron_str)

                params = {
                    'word': word,
                    'syllables': n_syllables(pron_str),
                    'pronunciation': pron_str,
                    'rp_pronunciation': rp_pron_str,
                }

                make_stmt = session.run(
                    """
    MERGE (p:Pattern {pronunciation: $rp_pronunciation})
    CREATE (p)<-[:RhymesWith]-(w:Word {word: $word, syllables: $syllables, pronunciation: $pronunciation})
    RETURN p;
    """, parameters=params)
                
        fetch_stmt = session.run(
            """
            MATCH (p: Pattern) RETURN p;        
            """
        )

        patterns = fetch_stmt.data()

        for p1, p2 in product(patterns, repeat=2):
            pron1 = p1['p'].get('pronunciation')
            pron2 = p2['p'].get('pronunciation')

            dist = slant_distance(pron1, pron2)
            lengths = [len(p.split(' ')) for p in (pron1, pron2)]
            if (dist == 1 and all([l > 1 for l in lengths])) or (dist == 2 and all([l > 2 for l in lengths])):
                sd_stmt = session.run(
                    """
                    MATCH (p1:Pattern {pronunciation: $p1_pronunciation})
                    MATCH (p2:Pattern {pronunciation: $p2_pronunciation})
                    CREATE (p1)-[:SlantRhymes {distance: $distance}]->(p2)                
                    """
                , parameters={
                    "p1_pronunciation": pron1,
                    "p2_pronunciation": pron2,
                    "distance": dist
                })

    driver.close()
