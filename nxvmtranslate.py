import yaml, os

def translateInit(language):
    languages = {'Русский': 'ru', 'English': 'en'}
    translateFile = f'{os.getenv("HOME")}/.nxvm/translate.{languages[language]}.yaml'
    # translateFile = 'translate.en.yaml'; print("\x1b[31;1mIGNORING LANGUAGE AND USING LOCAL!\x1b[0m")
    return yaml.load(open(translateFile).read(), yaml.Loader)
