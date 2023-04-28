from setuptools import setup, find_packages

with open('requirements.txt') as f:
    lines = f.read().split('\n')
    requirements = []
    for line in lines:
        if line.startswith('git+'):
            link, package = line.split('#egg=')
            requirements.append(f'{package} @ {link}#{package}')
        else:
            requirements.append(line)

setup(name='gama-gym',
      version='0.0.1',
      install_requires=requirements,
      extras_require={
          'examples': [
              'numpy~=1.22.3',
              'ray[rllib]~=2.0.0',
              'tensorflow==2.8.0'
          ]
      },
      packages=find_packages(),
      )
