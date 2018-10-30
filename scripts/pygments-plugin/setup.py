""" 
Cilkbook code syntax highlighting plugin for Pygments. 
""" 
from setuptools import setup 
entry_points = """ 
[pygments.lexers] 
cilklexer = cilkhilite.cilklexer:CilkLexer
cilkobjdumplexer = cilkhilite.cilklexer:CilkObjdumpLexer
pythonCBlexer = cilkhilite.cilklexer:PythonCBLexer
javaCBlexer = cilkhilite.cilklexer:JavaCBLexer
gasCBlexer = cilkhilite.cilklexer:GasCBLexer
objdumpCBlecer = cilkhilite.cilklexer:ObjdumpCBLexer

[pygments.formatters]
cilkbookformatter = cilkhilite.cilkformatter:CilkBookFormatter
chrtfformatter = cilkhilite.chrtfformatter:CHRtfFormatter

[pygments.styles]
cilkbookstyle = cilkhilite.cilkstyle:CilkBookStyle
""" 
setup( 
    name         = 'pycilk',
    version      = '0.1', 
    description  = __doc__, 
    author       = "Tao B. Schardl", 
    packages     = ['cilkhilite'], 
    entry_points = entry_points 
) 
