import os
from distutils.core import setup

setup(name='PyDFe',
      version='1.0',
      description='Biblioteca python para manipulação de documentos fiscais eletrônicos.',
      author='Clemente Junior',
      author_email='clmnt.jr@gmail.com',
      url='https://github.com/C-Element/PyDFe.git',
      packages=['pydfe', 'pydfe.documento'],
      package_dir={'pydfe.documento': os.path.join(os.path.dirname(__file__), 'pydfe', 'documento')},
      package_data={'pydfe.documento': ['*.TTF', ]}
      )
