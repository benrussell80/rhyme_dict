import os

from flask import Flask
from flask_graphql import GraphQLView

from schema import schema

app = Flask(__name__)
app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("BIND_HOST", "localhost"),
        port=os.environ.get("BIND_PORT", 5000),
        debug=os.environ.get("DEBUG", False),
    )
