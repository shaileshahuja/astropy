#!/usr/bin/env python
from __future__ import division

#Use "distribute" - the setuptools fork that supports python 3.
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup,find_packages,Extension
from glob import glob
from warnings import warn

import astropy,os
from astropy.version import version as versionstring
from astropy.version import release

NAME = 'Astropy'

SHORT_DESCRIPTION = 'Community-developed python astronomy tools'

#Take the long description from the root package docstring
LONG_DESCRIPTION = astropy.__doc__


#use the find_packages tool to locate all packages and modules other than
#those that are in "tests" 
astropypkgs = find_packages(exclude=['tests'])

#treat everything in scripts except README.rst as a script to be installed
astropyscripts = glob('scripts/*')
astropyscripts.remove('scripts/README.rst')

#C extensions that are not Cython-based should be added here.
extensions = []

# Look for Cython files - compile with Cython if it is not a release and Cython
# is installed.  Otherwise, use the .c files that live next to the Cython files.

try:
    import Cython
    have_cython = True
except ImportEror:
    have_cython = False
    
pyxfiles = []
for  dirpath, dirnames, filenames in os.walk('astropy'):
    modbase = dirpath.replace(os.sep,'.')
    for fn in filenames:
        if fn.endswith('.pyx'):
            fullfn = os.path.join(dirpath,fn)
            extmod = modbase+'.'+fn[:-4] #package name must match file name
            pyxfiles.append((extmod,fullfn))
    
if not release and have_cython:
    #add .pyx files
    for extmod,pyxfn in pyxfiles:
        extensions.append(Extension(extmod,[pyxfn]))
else:
    #add .c files
    for extmod,pyxfn in pyxfiles:
        cfn = pyxfn[:-4]+'.c'
        if os.path.exists(cfn):
            extensions.append(Extension(extmod,[cfn]))
        else:
            warnstr = 'Could not find Cython-generated C extension ' + \
                 '{0} - The {1} module will be skipped.'.format(cfn,extmod)
            warn(warnstr)

#Implement a version of build_sphinx that automatically creates the docs/_build
#dir - this is needed because github won't create the _build dir because it has
#no tracked files
try:
    from sphinx.setup_command import BuildDoc
    
    class apy_build_sphinx(BuildDoc):
        def finalize_options(self):
            from os.path import isfile    
            from distutils.cmd import DistutilsOptionError
            
            if self.build_dir is not None:
                if isfile(self.build_dir):
                    raise DistutilsOptionError('Attempted to build_sphinx into a file '+self.build_dir)
                self.mkpath(self.build_dir)
            return BuildDoc.finalize_options(self)
            
except ImportError: #sphinx not present
    apy_build_sphinx = None
    
cmdclassd = {}
if apy_build_sphinx is not None:
    cmdclassd['build_sphinx'] = apy_build_sphinx
    
setup(name=NAME,
      version=versionstring,
      description=SHORT_DESCRIPTION,
      packages=astropypkgs,
      package_data={'astropy':['data/*']},
      ext_modules=extensions,
      scripts=astropyscripts,
      requires=['numpy','scipy'],
      install_requires=['numpy'],
      provides=['astropy'], 
      author='Astropy Team, Erik Tollerud, Thomas Robitaille, and Perry Greenfield',
      author_email='astropy.team@gmail.com',
      #license = '', #TODO: decide on a license
      url='http://astropy.org',
      long_description=LONG_DESCRIPTION,
      cmdclass = cmdclassd
)
