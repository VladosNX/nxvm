import yaml, os

def translateInit(language):
    languages = {'Русский': 'ru', 'English': 'en'}
    translateFile = f'{os.getenv("HOME")}/.nxvm/translate.{languages[language]}.yaml'
    return yaml.load(open(translateFile).read(), yaml.Loader)
