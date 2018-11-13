# https://blog.csdn.net/qq_17550379/article/details/79943740


import fire

def hello(name,):
  return 'Hello {name}!'.format(name=name)

if __name__ == '__main__':
  fire.Fire()

# python google_fire.py hello xxxx
# Hello xxxx

