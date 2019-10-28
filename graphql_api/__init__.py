from flask import Flask
import os
from flask_graphql import GraphQLView



def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    if app.config["ENV"] == "production":
        app.config.from_object("graphql_api.config.ProductionConfig")
    elif app.config["ENV"] == "development":
        app.config.from_object("graphql_api.config.DevelopmentConfig")
    elif app.config["ENV"] == "testing":
        app.config.from_object("graphql_api.config.TestingConfig")
    else:
        app.config.from_object("graphql_api.config.DevelopmentConfig")

    
    from graphql_api.schema import schema

    app.add_url_rule('/', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))


    return app