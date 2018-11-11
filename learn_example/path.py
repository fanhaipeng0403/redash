import  os


def fix_assets_path(path):
    fullpath = os.path.join(os.path.dirname(__file__), "../", path)
    return fullpath

print (fix_assets_path('xxx'))
