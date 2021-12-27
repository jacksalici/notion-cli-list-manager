import toml

def toml_parser():
    with open ("test/config.toml", "r") as f:
        dict = toml.load(f)
    
    return dict




toml_parser()