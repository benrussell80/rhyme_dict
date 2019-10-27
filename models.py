import os

from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedFrom, RelatedTo


graph = Graph(
    host=os.environ["NEO4J_HOST"],
    port=os.environ["NEO4J_PORT"],
    user=os.environ["NEO4J_USERNAME"],
    password=os.environ["NEO4J_PASSWORD"]
)


class BaseModel(GraphObject):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def fetch_all(cls):
        return cls.match(graph)


class Word(BaseModel):
    word = Property()
    pronunciation = Property()
    syllables = Property()

    rhymes_with = RelatedTo("Pattern", "RhymesWith")

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

    def as_dict(self):
        return {
                attr: getattr(self, attr)
                for attr in ['word', 'pronunciation', 'syllables']
                if hasattr(self, attr) and getattr(self, attr) is not None
            }

    def fetch(self):
        for w in self.fetch_many():
            if all([
                w.word == self.word or not hasattr(self, 'word'),
                w.pronunciation == self.pronunciation or not hasattr(self, 'pronunciation'),
                w.syllables == self.syllables or not hasattr(self, 'syllables')
            ]): return w

    def fetch_many(self):
        return [w for w in Word.fetch_all().where(**self.as_dict())]

    def fetch_rhyme_pattern(self):
        pattern = Word.fetch_all().where(**self.as_dict()).first().rhymes_with._related_objects[0][0]
        return pattern


class Pattern(BaseModel):
    pronunciation = Property()

    slant_rhymes = RelatedTo("Pattern", "SlantRhymes")
    rhymes_with = RelatedFrom("Word", "RhymesWith")

    def as_dict(self):
        return {
            'pronunciation': self.pronunciation
        }

    def fetch_rhymes(self):
        return [w for w, _ in Pattern.fetch_all().where(pronunciation=self.pronunciation).first().rhymes_with._related_objects]

    def fetch_slant_rhymes(self, max_distance, limit=None):
        patterns = Pattern.fetch_all().where(pronunciation=self.pronunciation).first().slant_rhymes._related_objects
        ans = list(set([w[0] for p in patterns for w in p[0].rhymes_with._related_objects if p[1]['distance'] <= max_distance]))
        return ans
