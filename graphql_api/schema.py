from graphene import Field, Int, List, ObjectType, Schema, String

from .models import Word


class WordSchema(ObjectType):
    word = String(description="Word to fetch.")
    pronunciation = String(description="Pronunciation of word in ARPAbet form.")
    syllables = Int(description="Number of syllables in word.")
    rhyme_pattern = String(description="Syllable used to rhyme with other words.")


class Query(ObjectType):
    echo = List(WordSchema, word=String(required=True), pronunciation=String())
    rhyme = List(WordSchema, word=String(required=True), pronunciation=String())
    slant_rhyme = List(WordSchema, word=String(required=True), max_distance=Int(required=True), pronunciation=String())

    @staticmethod
    def resolve_echo(parent, info, word, pronunciation=None):
        ws = Word.get_all_matching_words(word, pronunciation=pronunciation)
        
        return [WordSchema(**w.as_dict(), rhyme_pattern=w.rhyme_pattern) for w in ws]

    @staticmethod
    def resolve_rhyme(parent, info, word, pronunciation=None):
        ws = Word.get_all_matching_words(word, pronunciation=pronunciation)

        rs = [r for w in ws for r in w.get_rhymes()]
        
        return [WordSchema(**r.as_dict(), rhyme_pattern=r.rhyme_pattern) for r in rs]

    @staticmethod
    def resolve_slant_rhyme(parent, info, word, max_distance, pronunciation=None):
        ws = Word.get_all_matching_words(word, pronunciation=pronunciation)

        # this is not returning distinct words;
        # for now I am going to use hashing on the Word objects but
        # in the future I need to fix the query so that it can take
        # in all pronunciations of the words and return the distinct ones
        srs = sorted(list(set([sr for w in ws for sr in w.get_slant_rhymes(max_distance=max_distance)])))

        return [WordSchema(**sr.as_dict(), rhyme_pattern=sr.rhyme_pattern) for sr in srs]


schema = Schema(query=Query)
