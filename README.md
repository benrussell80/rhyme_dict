# rhyme_dict
A rhyming dictionary graphql API that I created using graphene and Flask which pulls data from a neo4j database.

## How it Works
### Quantifying Rhymes
The initial dataset of the 1000 most frequent words was scraped from online sources. Each word in this database was then
used in conjunction with the [Carnegie Mellon Pronunciation Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict) to acquire the
pronunciations. Using the [cmudict](https://github.com/prosegrinder/python-cmudict) python package I acquired each pronunciation for
each word of the dataset in the form of ARPAbet phonemes. These look something like this:

    subject:    "S AH0 B JH EH1 K T"
                "S AH1 B JH IH0 K T"

As you can see, for each pronunciation of the word we get a different representation. The first one is unstressed then stressed (subJECT), and 
the latter is stressed then unstressed (SUBject). Unstressed syllables are 0's, primary stressed syllables are 1's, and secondary stressed syllables are 2's.

With these data we can start to rhyme words. In the context of this project, rhymes are defined as words sharing identical patterns from the final
stressed phoneme to the end. What does that mean? Let's say we have the word "wrecked." This word is pronounced as "R EH1 K T." As seen below, this word
rhymes with one of the pronunciations of subject (but not the other).

    subject:    "S AH0 B JH EH1 K T" --> rhyme (both end with "EH1 K T")
    wrecked:             "R EH1 K T"

    subject:    "S AH1 B JH IH0 K T" --> don't rhyme
    wrecked:             "R EH1 K T"

From this, we can start creating rhyme patterns, like "EH1 K T" for each of these words. So if we come across a new word, we can compare its rhyme pattern to those rhyme patterns that we have already catalogued and pair them up.

### Slant Rhymes
A step beyond this quantification involves the concept of a slant rhyme. Generally, a slant rhyme consists of two words which almost rhyme but have some minor difference.
For example, the words "steak" and "lace" share a common vowel sound but miss each other on the final consonants. Looking at their pronunciations we see this explicitly:

    steak:      "S T EY1 K"
    lace:         "L EY1 S"

Their rhyme patterns ("EY1 K" and "EY1 S") are only different by one phoneme. Let's use the Levenshtein distance as a way of quantifying
slant rhymes. For those not familiar, the [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) is one of the ways of finding the "distance"
between two sequences. For our purposes, we will find the distance between rhyme patterns. In the case of steak and lace their "slant distance" is 1 (we only need to
change one part of the sequence to arrive at the other).

Now, we have a way of not only finding rhymes of a word but also slant rhymes of a word. Using some regex matching with python I created the working dataset of words
and rhyme patterns. To quickly find the Levenshtein distance I used the [editdistance](https://github.com/aflc/editdistance) python package.

### The Database
This data seems very similar to what we might find in a graph; we have words connected to rhyme patterns, and rhyme patterns connected to each other patterns with some distance value. Let's set up a database to house all of this.

[Neo4j](https://neo4j.com/) is a graph database that stores data in the form of nodes and relationships. I created a database that stores words and rhyme patterns as nodes and rhymes and slant rhymes as relationships between those nodes. 

### Interacting with the Database
Now to get data out of the neo4j database in a meaningful way, I set up an API. Our preliminary interactions with it may be something like

- find all rhymes for a word
- find all slant rhymes for a word

A REST API might be good for this but then again maybe the user doesn't want all of the information for every word that gets returned. Maybe they only want the words
and don't want to get the pronunciations too. And what if we want flexibility in the slant distance for our slant rhymes?

This can be achieved with a REST API but let's try out a GraphQL API. If you haven't seen it (I'm still pretty new to it, honestly), a [GraphQL API](https://graphql.org/) is an API in which requests are handled like queries where instead of just going to an endpoint and making a GET request like

    GET /rhyme/<word>

we would make a POST request to the single endpoint available, and the API will handle the structure of our post and return the data with the same structure. I encourage you to checkout the link to get examples.

To make the API I will use the python packages: Flask, graphene, and neo4j. [Flask](https://www.fullstackpython.com/flask.html) is a light-weight web app framework. [Graphene](https://graphene-python.org/) is a library for building GraphQL APIs with python. [Neo4j](https://neo4j.com/developer/python/) is a pythonic way to interact with a neo4j database. With all of these together, things are a breeze.

So, I created a Flask app that services a GraphQL API and has functions like `echo` for getting info about a word and all of its pronunciations, and `rhyme` and `slantRhyme` for finding out more about  similar words.

### Deployment
The production database for this project is hosted with AWS EC2. The serverless API is made available over AWS Lambda by using [Zappa](https://github.com/Miserlou/Zappa).

You can interact with the most current version via the Graph*i*QL interface [here](https://v05woe07vc.execute-api.us-west-2.amazonaws.com/dev).

Or, you can interact with it programmatically from this address https://v05woe07vc.execute-api.us-west-2.amazonaws.com/dev

Some example queries to try out include

```
{
  echo(word: "cat"){
    word
    pronunciation
    syllables
    rhymePattern
  }
}
```

```
{
  rhyme(word: "best"){
    word
    pronunciation
  }
}
```

```
{
  slantRhyme(word: "port", maxDistance: 1){
    word
  }
}
```

### Development
I like to think that this project is "intermediate-friendly." It uses a variety of technologies, but isn't too large to get lost in. A lot can be added such as:

- more words
- more resolvers
- mutations to add words
- distinguishing between consonance and assonance

So, if you want to contribute then feel free to fork it and submit a PR.

To set it up locally, make sure you have neo4j installed on your system and set environment variables for

- `NEO4J_URI` (probably `bolt://localhost:7687`)
- `NEO4J_USERNAME` (probably `neo4j`)
- `NEO4J_PASSWORD` (set this with `neo4j-admin set-initial-password <password>`)
    
Once you've done that, install the requirements and make the database at that URI:

    # optionally make a virtual environment
    pip install -r requirements.txt
    python make_graph.py  # this will take a few minutes to make the database
    flask run  # navigate to <host>:<port>/graphql

From there you can query the API and see about what you might improve.

Thanks so much for checking out my project!!
