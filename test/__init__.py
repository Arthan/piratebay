def get_fixture(file):
    from os import path
    return path.join(path.join(path.dirname(__file__), 'fixtures'), file)