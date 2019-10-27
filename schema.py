from graphene import Field, Int, List, ObjectType, Schema, String

from models import Pattern, Word


class WordSchema(ObjectType):
    word = String(description="Word to fetch.")
    pronunciation = String(description="Pronunciation of word in ARPAbet form.")
    syllables = Int(description="Number of syllables in word.")
    rhyme_pattern = String(description="Syllable used to rhyme with other words.")

    @staticmethod
    def resolve_rhyme_pattern(parent, info):
        w = Word(**{
            "word": parent.word,
            "pronunciation": parent.pronunciation,
            "syllables": parent.syllables
        }).fetch()
        return w.fetch_rhyme_pattern().as_dict()['pronunciation']


class Query(ObjectType):
    echo = List(WordSchema, word=String(required=True), pronunciation=String())
    rhyme = List(WordSchema, word=String(required=True), pronunciation=String())
    slant_rhyme = List(WordSchema, word=String(required=True), max_distance=Int(required=True), pronunciation=String())

    @staticmethod
    def resolve_echo(parent, info, **kwargs):
        ws = Word(**kwargs).fetch_many()
        return [WordSchema(**w.as_dict()) for w in ws]

    @staticmethod
    def resolve_rhyme(parent, info, **kwargs):
        ws = Word(**kwargs).fetch_many()
        rps = [w.fetch_rhyme_pattern() for w in ws]
        rhymes = sorted(set([w for rp in rps for w in rp.fetch_rhymes()]))
        return [WordSchema(**w.as_dict()) for w in rhymes]

    @staticmethod
    def resolve_slant_rhyme(parent, info, word, max_distance, **kwargs):
        ws = Word(word=word, **kwargs).fetch_many()
        patterns = [w.fetch_rhyme_pattern() for w in ws]
        words = [w for p in patterns for w in p.fetch_slant_rhymes(max_distance)]
        words = list(sorted(set(words)))
        return [WordSchema(**w.as_dict()) for w in words]


schema = Schema(query=Query)
