from PyInstaller.utils.hooks import copy_metadata

datas = copy_metadata('setuptools')
hiddenimports = ['pkg_resources', 'pkg_resources.extern', 'pkg_resources.py2_warn']
