import cmd
import getpass
from neo4j import GraphDatabase
from string import Template
import os
from pprint import pprint


URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def execute(query):
    with driver.session() as session:
        return session.run(query)

class Cmd(cmd.Cmd):
    intro = str(Template('Connected to $USERNAME@$URI').substitute(USERNAME=USERNAME, URI=URI))
    prompt = Template('($USERNAME) ').substitute(USERNAME=USERNAME)

    def do_run(self, query):
        "Run a query in the database."
        result = execute(query)
        pprint(result.data())
        return
        

if __name__ == "__main__":
    Cmd().cmdloop()
    