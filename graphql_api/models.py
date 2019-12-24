import os
from string import Template

from neo4j import GraphDatabase
from utils import rhyme_pattern
import cmudict


URI = os.environ["NEO4J_URI"]
USERNAME = os.environ["NEO4J_USERNAME"]
PASSWORD = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


D = cmudict.dict()

def query(cypher, parameters):
    with driver.session() as session:
        return session.run(cypher, parameters=parameters)


class Word:
    def __init__(self, word=None, pronunciation=None, syllables=None):
        self.word = word
        self.pronunciation = pronunciation
        self.syllables = syllables

    # this will not be necessary once the queries for slant rhymes are fixed
    def __lt__(self, other):
        if isinstance(other, Word):
            return self.word < other.word
        
        return NotImplemented

    def __hash__(self):
        return hash((self.word, self.pronunciation, self.syllables))

    def __eq__(self, other):
        if isinstance(other, Word):
            return all([
                self.word==other.word,
                self.pronunciation==other.pronunciation,
                self.syllables==other.syllables,
            ])

        return NotImplemented

    @property
    def rhyme_pattern(self):
        return rhyme_pattern(self.pronunciation)

    def as_dict(self):
        return {
            "word": self.word,
            "pronunciation": self.pronunciation,
            "syllables": self.syllables
        }

    def get_rhymes(self):
        results = query("MATCH (w: Word {word: $word, pronunciation: $pronunciation, syllables: $syllables})-[:RhymesWith]-()-[:RhymesWith]-(w2:Word) RETURN DISTINCT w2 ORDER BY w2.word;", parameters=self.as_dict()).data()
        return [Word(**dict(r['w2'])) for r in results]

    def get_slant_rhymes(self, max_distance=1):
        results = query("MATCH (w1:Word {word: $word, pronunciation: $pronunciation, syllables: $syllables})-[:RhymesWith]-()-[sr:SlantRhymes]-()-[:RhymesWith]-(w2:Word) WHERE sr.distance <= $max_distance RETURN DISTINCT w2 ORDER BY w2.word;", parameters={**self.as_dict(), 'max_distance': max_distance}).data()
        return [Word(**dict(r['w2'])) for r in results]

    @classmethod
    def get_all_matching_words(cls, word, pronunciation=None):
        words = D.get(word, [])
        if words == []:
            return []

        if pronunciation is not None:
            words = list(filter(lambda word: word == pronunciation, words))
        
        rps = list(map(rhyme_pattern, words))

        if len(rps) > 0:
            where_string = "WHERE " + "OR ".join([Template("p.pronunciation = '$rp' ").substitute(rp=rp) for rp in rps])
        else:
            where_string = ""
        
        results = query(f"MATCH (w:Word)-[:RhymesWith]-(p:Pattern) {where_string}RETURN DISTINCT w;", {})
        
        return [cls(**dict(r['w'])) for r in results]
