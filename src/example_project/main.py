from example_project.composition.context import Context
from example_project.composition.frames import ingest_frames_from_api_into_landing_layer
# i want to download data from an api and store it into a storage location
# 1. i need to know where that storage location is
# 1.1 i need to be able to switch between storage location without changing the code

# 2. i need to know what the api is that i need to use
# 2.1 i need to be able to switch between api without changing the code

# 3. i need to know how to parse the data because the api will only give me a json response
# 3.1 i need to be able to switch between parsing without changing the code

# layers needed to build (from inside out):
# 1. entities (domain layer)
# 2. use cases / services (application layer)
# 3. interface adapters (interface layer)
# 4. infrastructure / composition / framework (infrastructure layer)


def main() -> None:
    # This function knows the context in which we are running so it is able to set things up for us
    context = Context.default()
    ingest_frames_from_api_into_landing_layer(context=context)