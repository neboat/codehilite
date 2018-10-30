# -*- coding: utf-8 -*-
"""
    cilkhilite.cilklexer
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for code in the Cilk book.

    :copyright: Copyright 2013 by Tao B. Schardl, Warut Suksompong
    :license: BSD

    Based on CppLexer from pygments.lexers.compiled,
    PythonLexer from pygments.lexers.agile, and
    JavaLexer from pygments.lexers.jvm.
    GasLexer from pygments.lexers.asm.

    :copyright: Copyright 2006-2012 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, DelegatingLexer, \
    include, bygroups, using, this, combined, inherit
from pygments.lexers.asm import GasLexer, ObjdumpLexer
from pygments.lexers.compiled import CppLexer
from pygments.lexers.jvm import JavaLexer
from pygments.lexers.agile import PythonLexer
from pygments.util import get_bool_opt, get_list_opt
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
     Number, Punctuation, Error, Literal, Token, Other

__all__ = ['CilkLexer', 'PythonCBLexer', 'JavaCBLexer', 'GasCBLexer', 'ObjdumpCBLexer', 'CilkObjdumpLexer']

class CilkLexer(CppLexer):
    """
    For Cilk source code.
    """
    name = 'Cilk'
    aliases = ['cilk']    
    filenames = ['*.c', '*.h',
                 '*.cpp', '*.hpp', '*.c++', '*.h++',
                 '*.cc', '*.hh', '*.cxx', '*.hxx']
    mimetypes = ['text/x-c++hdr', 'text/x-c++src']
    priority = 0.1

    #: optional Comment or Whitespace
    _ws = r'(?:\s|//.*?\n|/[*].*?[*]/)+'
    #: only one /* */ style comment
    _ws1 = r'\s*/[*].*?[*]/\s*'
    _ws01 = r'\s*|' + _ws1

    _custom_types = []
    _custom_keywords = []
    
    def customtypes_callback(lexer, match):
        comment_head = match.group(1)
        type_list = match.group(5)
        for new_type in type_list.strip().split(' '):
            if new_type.strip() != '' and new_type.strip() not in lexer._custom_types:
                lexer._custom_types.append(new_type.strip())
        # yield match.start(), Comment.Invisible, comment_head + type_list
        yield match.start(), Comment.Invisible, match.group(0)

    def customkeywords_callback(lexer, match):
        comment_head = match.group(1)
        keyword_list = match.group(5)
        for new_keyword in keyword_list.strip().split(' '):
            if new_keyword.strip() != '' and new_keyword.strip() not in lexer._custom_keywords:
                lexer._custom_keywords.append(new_keyword.strip())
        yield match.start(), Comment.Invisible, comment_head + keyword_list

    def typedef_callback(lexer, match):
        new_type = match.group(1)
        if new_type.strip() not in lexer._custom_types:
            lexer._custom_types.append(new_type.strip())
        yield match.start(), Keyword.Type, new_type

    def classname_callback(lexer, match):
        new_type = match.group(1)
        if new_type.strip() not in lexer._custom_types:
            lexer._custom_types.append(new_type.strip())
        yield match.start(), Name.Class, new_type

    def variable_callback(lexer, match):
        name = match.group(1)
        # print lexer._custom_types
        if name.strip() in lexer._custom_types:
            yield match.start(), Keyword.Type, name
        elif name.strip() in lexer._custom_keywords:
            yield match.start(), Keyword.Custom, name
        else:
            yield match.start(), Name.Variable, name

    def function_callback(lexer, match):
        name = match.group(1)
        # print lexer._custom_types
        if name.strip() in lexer._custom_types:
            yield match.start(), Keyword.Type, name
        elif name.strip() in lexer._custom_keywords:
            yield match.start(), Keyword.Custom, name
        else:
            yield match.start(), Name.Function, name

    def checkcustom_callback(lexer, match):
        name = match.group(1)
        if name.strip() in lexer._custom_types:
            yield match.start(), Keyword.Type, name
        elif name.strip() in lexer._custom_keywords:
            yield match.start(), Keyword.Custom, name
        else:
            yield match.start(), Name, name

    # def checknamespace_callback(lexer, match):
    #     name = match.group(1)
    #     # The following is not technically right, because of comments
    #     whitespace = match.group(2)
    #     doublecolon = match.group(3)
    #     if name.strip() in lexer._custom_types:
    #         yield match.start(1), Keyword.Type, name
    #         yield match.start(2), Text, whitespace
    #         yield match.start(3), Operator, doublecolon
    #     elif name.strip() in lexer._custom_keywords:
    #         yield match.start(1), Keyword.Custom, name
    #         yield match.start(2), Text, whitespace
    #         yield match.start(3), Operator, doublecolon
    #     else:
    #         yield match.start(1), Name.Namespace, name
    #         yield match.start(2), Text, whitespace
    #         yield match.start(3), Operator, doublecolon

    def checknamespace_callback(lexer, match):
        name = match.group(1)
        if name.strip() in lexer._custom_types:
            yield match.start(), Keyword.Type, name
        elif name.strip() in lexer._custom_keywords:
            yield match.start(), Keyword.Custom, name
        else:
            yield match.start(), Name.Namespace, name

    tokens = {
        'whitespace': [
            # TB: Make #line macros invisible.
            # A better way to do this is to mark them as #line macros
            # and then optionally render #line macros invisible.
            ('^(' + _ws + r'#line)(\s+\d\n)',
             bygroups(Comment.Invisible.Begin, Comment.Invisible.End)),

            # TB: Adding support for custom types
            (r'([ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*Types:))(.*?[^\\]\n)',
             customtypes_callback),
            (r'([ \t\f\v]*/([*][*][*])((\s*)Types:))(.*?)([*](\\\n)?[*](\\\n)?[*](\\\n)?/)',
             customtypes_callback),

            (r'([ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*Keywords:))(.*?[^\\]\n)', 
             customkeywords_callback),

            # TB: Added support to make blocks of code invisible.
            (r'[ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*<<)(\n|(.|\n)*?[^\\]\n)',Comment.Invisible.End),
            (r'[ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*>>)(\n|(.|\n)*?[^\\]\n)',Comment.Invisible.Begin),

            # TB: Added support to emphasize blocks of code.
            (r'[ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*\[\[)(\n|(.|\n)*?[^\\]\n)',Comment.Emph.Begin),
            (r'[ \t\f\v]*/(\\\n)?/(\\\n)?/(\s*\]\])(\n|(.|\n)*?[^\\]\n)',Comment.Emph.End),

            # TB: The following line plus some changes in the LaTeX
            # formatter can remove the invisible comment characters
            # entirely and render pure LaTeX in the document.  This
            # feature could be abused, but it is useful for
            # symbolically labeling lines of code while minimally
            # affecting the Pygmentized output.
            (r'[ \t\f\v]*(/(\\\n)?/(\\\n)?/)(.*?[^\\]\n)',
             bygroups(Comment.Invisible, None, None, Comment.PureTeX)),

            (r'(\\[a-zA-Z_][^\n]*?)(\n)',
             bygroups(Comment.PureTex, Text)),

            # Exclude invisible character marker inside of a single-line comment
            (r'(//)([^\n]*?)(///)([^\n]*?)(\n)',
             bygroups(Comment.Single, Comment.Single, Comment.Invisible, Comment.PureTeX, Comment.Single)),

            inherit,

            (r'^([ \t\f\v]*)(#)', bygroups(Text, Comment.Preproc), 'macro'),
            ],
        'macro': [
            # TB: Added special handling of include statements
            (r'(include)(\s*)([<])(\s*)([a-zA-Z0-9._/-]+)(\s*)([>])',
             bygroups(Comment.Preproc,
                      using(this), Comment.Preproc, using(this),
                      Token.Preproc.Library,
                      using(this), Comment.Preproc)),
            (r'(include)(\s*)(["])(\s*)([a-zA-Z0-9._/-]+)(\s*)(["])',
             bygroups(Comment.Preproc,
                      using(this), Comment.Preproc, using(this),
                      Token.Preproc.Library,
                      using(this), Comment.Preproc)),

            # TB: Added special handling of define statements
            # Function-like macros
            (r'(define)(\s+)([a-zA-Z_][a-zA-Z0-9_]*)'
             r'(\s*)(\()'
             r'(?=(\s*[a-zA-Z_][a-zA-Z0-9_]*)+(\s*[,]\s*[a-zA-Z_][a-zA-Z0-9_]*)*(\s*\)))',
             bygroups(Comment.Preproc, Text, Name.Function,
                      Text, Punctuation), ('#pop', 'macro-def-compute', 'macro-arglist')),
            # Object-like macros
            (r'(define)(\s+)([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Comment.Preproc, Text, Name.Variable),
             ('#pop', 'macro-def-compute')),

            # TB: The following line plus some changes in the LaTeX
            # formatter can remove the invisible comment characters
            # entirely and render pure LaTeX in the document.  This
            # feature could be abused, but it is useful for
            # symbolically labeling lines of code while minimally
            # affecting the Pygmentized output.
            (r'(///)(.*?\n)',
             bygroups(Comment.Invisible, Comment.PureTeX), '#pop'),

            (r'([\\][a-zA-Z_][^\n]*?)(\n)',
             bygroups(Comment.PureTex, Text)),

            inherit,
            ],
        'macro-arglist': [
            (r'(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*)',
             bygroups(using(this), Name.Variable, using(this))),

            (r'(\,)', Punctuation),
            (r'(\))', Punctuation, '#pop'),
            # TB: Argument lists on macros are weird, allowing nested parens
            (r'(\()', Punctuation, '#push'),
            ],
        'macro-def-compute': [
            (r'[#]', Operator.DEFCOMPUTE),
            (r'[(),]', Punctuation.DEFCOMPUTE),
            (r'[ \t\f\v]*(/(\\\n)?/(\\\n)?/)(.*?[^\\]\n)',
             bygroups(Comment.Invisible, None, None, Comment.PureTeX), '#pop'),
            (r'\\\s*\n', Comment.Preproc),
            (r'\s*\n', Comment.Preproc, '#pop'),
            include('whitespace'),
            include('statements'),
            include('parentheses'),
            ],
        'using': [
            include('whitespace'),
            include('namespace'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)', Name.Namespace),
            ('', Text, '#pop'),
            ],
        'keywords': [
            (r'(namespace)\b(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*)'
             r'(\s+|' + _ws1 + ')([{])',
             bygroups(Keyword, using(this), Name.Namespace, using(this), Punctuation),
             'root'),

            (r'(namespace)\b(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Keyword, using(this), Name.Namespace)),

            (r'(template)\b(\s*|' + _ws1 + ')*?([<])',
             bygroups(Keyword, using(this), Punctuation), 'template'),

            # Predicated Keywords
            (r'(switch)\b'
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Predicated,
                      using(this), Punctuation),
             'switch-pred'),

            (r'(while|if)\b'
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Predicated,
                      using(this), Punctuation),
             'block'),

            (r'(for)\b'
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Predicated,
                      using(this), Punctuation),
             'block-for'),

            (r'(pipe_while)\b'
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Predicated,
                      using(this), Punctuation),
             'block'),

            (r'(cilk_for|pipe_for)\b'
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Cilk.Predicated,
                      using(this), Punctuation),
             'block-for'),

            (r'typedef\b', Keyword, 'typedef'),

            (r'(class)'
             r'(?=(\s+|' + _ws1 + ')[a-zA-Z_][a-zA-Z0-9_]*)',
             Keyword, 'classname'),

            (r'(struct|union)(?=(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*[a-zA-Z0-9_:*,\s]*?)?[<{])',
             Keyword, 'struct'),

            (r'(struct|union)(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Keyword, using(this), Keyword.Type), 'variable'),

            (r'(enum)', Keyword, 'enum'),
             
            (r'(extern)(' + _ws01 + ')(L?")',
             bygroups(Keyword, using(this), String), 'string'),

            (r"(extern)(\s*)(L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])')",
             bygroups(Keyword, using(this), String.Char, None)),

            # TB: In C++11, auto can be used to deduce the type of something.
            (r'(auto)'
             r'(?=(?:([*&\s]+|' + _ws1 + ')?[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword, 'variable'),

            (r'(auto|break|case|const|continue|default|do|else|enum|extern|'
             r'for|goto|if|register|restricted|return|sizeof|static|struct|'
             r'switch|typedef|union|volatile|while)\b', Keyword),
            (r'(_{0,2}(inline|naked|restrict|thread|typename))\b', Keyword.Reserved),
            # Vector intrinsics
            (r'(__(m128i|m128d|m128|m64))\b', Keyword.Reserved),
            # Microsoft-isms
            (r'__(asm|int8|based|except|int16|stdcall|cdecl|fastcall|int32|'
             r'declspec|finally|int64|try|leave|wchar_t|w64|unaligned|'
             r'raise|noop|identifier|forceinline|assume)\b', Keyword.Reserved),
            (r'(asm|catch|const_cast|delete|dynamic_cast|explicit|'
             r'export|friend|mutable|namespace|new|operator|'
             r'private|protected|public|reinterpret_cast|'
             r'restrict|static_cast|template|this|throw|throws|'
             r'typeid|typename|using|virtual)\b', Keyword),
            # GCC-isms
            (r'__(attribute)__\b', Keyword),

            # TB: Added support for the Cilk keywords
            (r'(cilk_spawn|cilk_sync|cilk_for|'
             r'_Cilk_spawn|_Cilk_sync)\b', Keyword.Cilk),
            ],
        'namespace': [
            (r'(std)(::)', bygroups(Name.Namespace, Operator)),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*::)', checknamespace_callback),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=(?:\s*[<][^;{}()~!%^&+=|?/\-]+?[>])?(?:\s*::\s*)(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
            #  Name.Namespace),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(' + _ws01 + ')([<])'
             r'(?=(?:[^;{}()~!%^&+=|?/\-]+?[>])(?:(' + _ws01 + ')*?(::)(' + _ws01 + ')*?)'
             r'(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
             bygroups(Keyword.Type, using(this), Punctuation), 'type'),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(\s*)([<])'
            #  r'(?=(?:[^;{}()~!%^&+=|?/\-]+?[>])(?:\s*::\s*)(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
            #  bygroups(Keyword.Type, using(this), Punctuation), 'type'),

            (r'::', Operator),
            ],
        'typekeyword': [
            include('namespace'),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b',
             Keyword.Type),
            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?(?:[\s*]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
            #  Keyword.Type),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:(' + _ws01 + ')[<][^;{}()~!%^+=|?/\-]+?[>])?(?:[\s*&]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type),
            ],
        'switch-pred': [
            (r'(\))(.*?)({)',
              bygroups(Punctuation, using(this), Punctuation),
              ('#pop', 'switch')),
            include('block'),
            ],
        'switch': [
            # TB: Fixing handling of "default:" in switch statements,
            # which conflicts with inherited label rule from 'whitespace'.
            (r'^(\s*)(default)(\s*)(:)',
             bygroups(Text, Keyword, Text, Punctuation)),

            include('whitespace'),
            (r'\b(case)(.+?)(:)', bygroups(Keyword, using(this), Punctuation)),
            include('keywords'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:(' + _ws01 + ')*?[<][^;{}()~!%^&+=|?<>/\-]+?[>])?(?:[\s*&]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type, 'variable'),

            (r'[~!%^&*+=|?:<>/-]', Operator, ('#pop', 'switch-novardef')),

            (r'[\]]', Error),
            include('type-cast'),
            include('parentheses'),
            
            (r'[;,]', Punctuation),
 
            include('statements')
            ],
        'switch-novardef': [
            include('whitespace'),
            include('keywords'),
            include('statements'),

            ('', Text, ('#pop', 'switch'))
            ],
        'classname': [
            include('whitespace'),
            include('namespace'),

            ('(private|public|protected)', Keyword),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', classname_callback),

            (r'[<]', Punctuation, 'type'),
            (r'[>]', Error),

            (r'[{]', Punctuation, ('#pop', 'class')),
            # (r'[{]', Punctuation, 'root'),
            (r'[}]', Error),

            (r':', Operator),
            ('', Text, '#pop')
            ],
        'struct': [
            include('whitespace'),
            include('namespace'),

            ('(private|public|protected)', Keyword),
            # TB: This is C++ specific, since C++ (not C) automatically typedef's structs
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', typedef_callback),

            (r'[<]', Punctuation, 'type'),
            (r'[>]', Error),

            (r'[{]', Punctuation, ('#pop', 'class')),
            # (r'[{]', Punctuation, 'root'),
            (r'[}]', Error),

            (r':', Operator),
            ('', Text, '#pop')
            ],
        'enum': [
            include('whitespace'),
            include('namespace'),

            # TB: This is C++11 specific
            ('class', Keyword),

            # Look for a curly brace after the name to determine if
            # this is defining an enumerated type or a variable with
            # an enumerated type.
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=(\s*)[{])', typedef_callback),

            (r'[{]', Punctuation, ('#pop', 'enum-decls')),
            (r'[}]', Error),

            (r'[;]', Punctuation, '#pop'),

            include('variable'),
            
            ('', Text, '#pop')
            ],
        'enum-decls': [
            include('whitespace'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', Name.Variable),
            (r'[=]', Operator, 'assignment'),
            (r'[,]', Punctuation),
            (r'[}]', Punctuation, '#pop')
            ],
        'type': [
            include('whitespace'),
            include('namespace'),

            (r'(class|typename)', Keyword, 'typename'),

            include('keywords'),
            include('typekeyword'),

            (r'(true|false|NULL)\b', Name.Builtin),

            (r'[<]', Punctuation, '#push'),
            (r'[>]', Punctuation, '#pop'),
            (r'[*]', Operator),
            (r'[,]', Punctuation),

            # TB: Type inferencing, similar to what Emacs seems to do.
            (r'([a-zA-Z][a-zA-Z0-9_]*)(?=(?:\s*[*]))', Keyword.Type),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)', checkcustom_callback),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)', Keyword.Type),
            ],
        'typedef': [
            include('whitespace'),
            (r'(class|struct|union|typename)\b', Keyword),
            
            include('keywords'),
            include('typekeyword'),

            (r'[<]', Punctuation, 'type'),
            (r'[>]', Punctuation),
            (r'[*]', Operator),

            (r'[{]', Punctuation, 'block'),
            (r'[}]', Error),

            (r'([a-zA-Z][a-zA-Z0-9_]*)', typedef_callback),

            ('', Text, '#pop'),
            ],
        'template': [
            include('whitespace'),
            (r'(class|typename)', Keyword, 'typename'),
            (r'[>]', Punctuation, '#pop'),
            
            (r'(struct|union)(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*\b)',
             bygroups(Keyword, Text, Keyword.Type), ('#pop', 'template-args')),

            include('keywords'),

            include('namespace'),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b',
             Keyword.Type, ('#pop', 'template-args')),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>]))',
             Keyword.Type, ('#pop', 'template-args')),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', Keyword.Type, ('#pop', 'template-args')),

            (r'[*&]', Operator),
            (r'[,]', Punctuation),
            (r'[>]', Punctuation, '#pop'),

            # (r'[,]', Punctuation),
            # (r'[=]', Operator, 'assignment-type'),
            # (r'([a-zA-Z][a-zA-Z0-9_]*)', typedef_callback),
            ],
        'template-args': [
            (r'[>]', Punctuation, '#pop'),
            (r'[,]', Punctuation, ('#pop', 'template')),
            include('function-args'),
            ],
        'typename-statement': [
            include('whitespace'),

            (r'(std)(::)', bygroups(Name.Namespace, Operator)),
            (r'([<])', Punctuation, 'type'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:[<][^;{}()~!%^&+=|?/\-]+?[>])?(?:(' + _ws01 + ')*?::(' + _ws01 + ')*?))',
             Keyword.Type),
            (r'(::)', Operator),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=(?:[<][^;{}()~!%^&+=|?/\-]+?[>])?(\s|' + _ws1 +')+?([a-zA-Z_][a-zA-Z0-9_]*))',
            #  Keyword.Type, ('#pop', 'variable')),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=\s+([a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type, ('#pop', 'variable')),

            ],
        'typename-function-args': [
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:[<][^;{}()~!%^&+=|?/\-]+?[>])?([\s*&]+?)([a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type, ('#pop', 'function-args')),

            include('typename-statement'),
            ],
        'typename': [
            include('whitespace'),
            (r'(std)(::)', bygroups(Name.Namespace, Operator)),
            (r'([<])', Punctuation, 'type'),
            (r'[,]', Punctuation, '#pop'),
            (r'[=]', Operator, 'assignment-type'),
            (r'(::)', Operator),
            (r'(\s*)(?=[>)])', Text, '#pop'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', typedef_callback),
            ],
        'assignment-type': [
            (r'[<]', Punctuation, 'type'),
            (r'(\s*)(?=[>,])', Text, '#pop'),
            include('type'),
            ],
        'decl': [
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[(])\b', function_callback),
            (r'([(])', Punctuation, ('#pop', 'function-args-start')),

            include('variable'),

            # include('whitespace'),
            # (r'(struct|union)(\s+)([a-zA-Z_][a-zA-Z0-9_]*\b)',
            #  bygroups(Keyword, Text, Keyword.Type)),

            # include('keywords'),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=\s*__attribute__)', variable_callback),

            # include('typekeyword'),

            # (r'[*&]', Operator),
            # (r'[,]', Punctuation),
            # (r'[<]', Punctuation, 'type'),
            # (r'[>]', Error),

            # (r'[\[]', Operator, 'statement'),
            # (r'[\]]', Error),

            # # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[=])\b', variable_callback),
            # # # TB: Needed to handle multiple variable definitions with
            # # # assignments on the same line.  (See x264-code.cpp test.)
            # # (r'=', Operator, 'assignment'),

            # # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[:]\s*\d+[LlUu]*)\b', variable_callback),
            # # # TB: Handling bit fields
            # # (r'(:)(\s*)(\d+[LlUu]*)',
            # #  bygroups(Punctuation, Text, Number.Integer)),

            # # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[,;])\b', variable_callback),

            # ('', Text, ('#pop', 'statement')),
            ],
        'variable': [
            include('whitespace'),

            (r'(struct|union)(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*\b)',
             bygroups(Keyword, using(this), Keyword.Type)),

            include('keywords'),

            # function pointers
            (r'([(])(\s*)([*])(\s*)([a-zA-Z_][a-zA-Z0-9_]*\b)',
             bygroups(Punctuation, Text, Operator, Text, Name.Variable),
             'function-ptr'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=\s*__attribute__)', variable_callback),

            include('typekeyword'),

            (r'[*&]', Operator),
            (r'[,]', Punctuation),
            (r'[<]', Punctuation, 'type'),
            (r'[>]', Error),

            (r'[\[]', Operator, 'statement'),
            (r'[\]]', Error),

            include('parentheses'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[=])\b', variable_callback),
            # TB: Needed to handle multiple variable definitions with
            # assignments on the same line.  (See x264-code.cpp test.)
            (r'=', Operator, 'assignment'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[:]\s*\d+[LlUu]*)\b', variable_callback),
            # TB: Handling bit fields
            (r'(:)(\s*)(\d+[LlUu]*)',
             bygroups(Punctuation, Text, Number.Integer)),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(?=\s*[,;])\b', variable_callback),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', variable_callback),

            # TB: Needed to handle multiple variable definitions with
            # assignments on the same line.  (See x264-code.cpp test.)
            (r'=', Operator, 'assignment'),
            (r''
             r'(?=[;])',
             Text, '#pop'),

            ('', Text, ('#pop', 'statement')),
            ],
        'function-ptr': [
            include('whitespace'),
            (r'[(]', Punctuation, ('#pop', 'function-args-start')),
            (r'([)])(\s*)([(])',
             bygroups(Punctuation, Text, Punctuation), ('#pop', 'function-ptr-args-start')),
            ],
        'function-ptr-args-start': [
            include('whitespace'),

            (r'(struct|union)(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*\b)',
             bygroups(Keyword, Text, Keyword.Type), ('#pop', 'function-ptr-args')),

            include('keywords'),

            include('namespace'),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b',
             Keyword.Type, ('#pop', 'function-ptr-args')),
            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?(?:[\s*]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
            #  Keyword.Type),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>]))',
             Keyword.Type, ('#pop', 'function-ptr-args')),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', Keyword.Type, ('#pop', 'function-ptr-args')),

            (r'[*&]', Operator),
            (r'[,]', Punctuation),
            (r'[)]', Punctuation, ('#pop', 'function-ptr-end')),
            ],
        'function-ptr-args': [
            (r'[,]', Punctuation, ('#pop', 'function-ptr-args-start')),
            (r'[)]', Punctuation, ('#pop', 'function-ptr-end')),
            include('variable'),
            ],
        'function-ptr-end': [
            include('whitespace'),

            (r'[{]', Punctuation, ('#pop', 'block')),
            (r'[,;]', Punctuation, '#pop'),

            include('parentheses'),
            ],
        'assignment': [
            include('whitespace'),
            include('statements'),

            ('[\[]', Operator, '#push'),
            ('[\]]', Operator, '#pop'),

            include('type-cast'),
            # Early termination of an assignment
            (r'(\s*)(?=[)}>])', Text, '#pop'),
            include('parentheses'),

            ('[,]', Punctuation, '#pop'),
            (r''
             r'(?=[;])',
             Text, '#pop'),
            ('', Text, '#pop'),
            ],
        'statements': [
            ## Special constants
            (r'L?"', String, 'string'),
            (r"L?'(\\.|\\[0-7]{1,3}|\\x[a-fA-F0-9]{1,2}|[^\\\'\n])'", String.Char),
            (r'(\d+\.\d*|\.\d+|\d+)[eE][+-]?\d+[LlUu]*', Number.Float),
            (r'(\d+\.\d*|\.\d+|\d+[fF])[fF]?', Number.Float),
            (r'0x[0-9a-fA-F]+[LlUu]*', Number.Hex),
            (r'0[0-7]+[LlUu]*', Number.Oct),
            (r'\d+[LlUu]*', Number.Integer),

            (r'(using)', Keyword, 'using'),

            (r'(typename)', Keyword.Reserved, 'typename-statement'),

            ## Special keywords
            include('namespace'),
            include('keywords'),

            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b',
             Keyword.Type),

            (r'(true|false|NULL)\b', Name.Builtin),

            # (r'([a-zA-Z_][a-zA-Z0-9_*]*)\b(\s*)'
            #  r'(?=([<][[^;]*?[>])(\s*)([a-zA-Z_][a-zA-Z0-9_*]*)',
            #  bygroups(using(this), Text), 'variable'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(' + _ws01 + ')*?([<])'
             r'(?=(?:[^;{}()~!%^&+=|?/-]+?[>]))',
             bygroups(Keyword.Type, using(this), Punctuation), 'type'),

            # Calling a constructor does not color the cunstructor
            # name as a type.
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(' + _ws01 + ')(\())', Name),

            # Check if this word is a type
            (r'([a-zA-Z_][a-zA-Z0-9_]*)', checkcustom_callback),

            (r'\*/', Error),
            (r'[~!%^&*+=|?:<>/-]', Operator),
            #(r'[,]', Punctuation),

            # Neither a type nor a keyword is immediately preceded by a .
            (r'([.])([a-zA-Z_][a-zA-Z0-9_]+)\b',
             bygroups(Operator, Name)),
            (r'[.]', Operator),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(\s*)'
            #  r'(?=([<][[^;]*?[>]))',
            #  bygroups(using(this), Text)),
            # inherit,
            ],
        'root': [
            include('whitespace'),
            include('keywords'),

            # TB: More conservative type inferencing at root level

            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b'
             r'(?=(?:[*&\s]+?[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type, 'decl'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])'
             r'(?:[\s*&]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type, 'decl'),

            # # functions
            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b((?:[a-zA-Z0-9_*&<>:,\s]*?[*&\s]+?))'  # return type
            #  r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'((?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?)(\s*)(::)(\s*)'
            #  r'([a-zA-Z_][a-zA-Z0-9_]*)\b'                 # method name
            #  r'(\s*)(\()',
            #  bygroups(Keyword.Type, using(this),
            #           Name.Namespace.First, using(this),
            #           Text, Operator, Text,
            #           Name.Function,
            #           Text,
            #           Punctuation),
            #  'function-args-start'),

            # functions
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b((?:[a-zA-Z0-9_*&<>:,\s]*?[*&\s]+?))'  # return type
             r'(?=(?:(([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'((' + _ws01 + ')[<][^;{}()~!%^+=|?/\-]+?[>])?'
             r'(' + _ws01 + ')*?(::)(' + _ws01 + ')*?)'
             r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\())',
             bygroups(Keyword.Type, using(this)), 'decl'),

            # functions
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'((?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?)(' + _ws01 + ')*?(::)(' + _ws01 + ')*?'  # return type
             r'(~)?(' + _ws01 + ')*?'
             r'(\1)\b'                          # method name
             r'(' + _ws01 + ')*?(\()',
             bygroups(Keyword.Type, using(this),
                      using(this), Operator, using(this),
                      Operator, using(this), Name.Function,
                      using(this),
                      Punctuation),
             'function-args-start'),

            # # functions
            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b((?:[a-zA-Z0-9_*&<>:,\s]*?[*&\s]+?))'  # return type
            #  r'([a-zA-Z_][a-zA-Z0-9_]*)'                     # method name
            #  r'(\s*)(\()',
            #  bygroups(Keyword.Type, using(this),
            #           Name.Function,
            #           Text,
            #           Punctuation),
            #  'function-args-start'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:([*\s]|' + _ws1 + ')+?[a-zA-Z_][a-zA-Z0-9_]*)(?:' + _ws01 + ')(?:[=;]))',
             Keyword.Type, 'variable'),

            # (r'(' + '|'.join(_custom_types).encode('ascii','ignore').encode('string-escape') + r')\b'
            #  r'(?=(?:[*&\s]+?[a-zA-Z_][a-zA-Z0-9_]*))',
            #  Keyword.Type, 'variable'),

            # (r'\s*'
            #  r'(?=(?:[a-zA-Z_][a-zA-Z0-9_]*)\b(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?(?:[\s*&]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*))',
            #  Text, 'variable'),

            include('namespace'),

            ('', Text, 'statement'),
            ],
        'function-args-start':[
            include('whitespace'),

            (r'(struct|union)(\s+|' + _ws1 + ')([a-zA-Z_][a-zA-Z0-9_]*)',
             bygroups(Keyword, using(this), Keyword.Type), ('#pop', 'function-args')),

            (r'(typename)', Keyword, ('#pop', 'typename-function-args')),

            include('keywords'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:(' + _ws01 + ')[<][^;{}()~!%^+=|?/\-]+?[>]))',
             Keyword.Type, ('#pop', 'function-args')),

            include('namespace'),
            (r'(bool|int|long|float|short|double|char|unsigned|signed|void|'
             r'[a-zA-Z_][a-zA-Z0-9_]*_t)\b',
             Keyword.Type, ('#pop', 'function-args')),
            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=(?:\s*[<][^;{}()~!%^+=|?/\-]+?[>])?(?:[\s*]+?)(?:[a-zA-Z_][a-zA-Z0-9_]*\b))',
            #  Keyword.Type),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b', Keyword.Type, ('#pop', 'function-args')),

            (r'[*&]', Operator),
            (r'[,]', Punctuation),
            (r'[)]', Punctuation, ('#pop', 'function-decl-end')),

            ],
        'function-args': [
            (r'[,]', Punctuation, ('#pop', 'function-args-start')),
            (r'[)]', Punctuation, ('#pop', 'function-decl-end')),
            include('variable'),
            ],
        'function-decl-end': [
            include('whitespace'),
            (r'[:]', Punctuation),  # list of invoked default constructors

            include('statements'),

            (r'[{]', Punctuation, ('#pop', 'block')),
            (r'[;]', Punctuation, '#pop'),
            (r'[,]', Punctuation),  # list of invoked default constructors
            (r'([)])(' + _ws01 + ')([(])',
             bygroups(Punctuation, using(this), Punctuation),
             ('#pop', 'function-ptr-args-start')),

            include('parentheses'),
            ],
        'parentheses': [
            (r'[\[]', Operator, 'statement'),
            (r'[\]]', Operator, '#pop'),

            (r'[{]', Punctuation, 'block'),
            (r'[}]', Punctuation, '#pop'),

            (r'[(]', Punctuation, 'block-paren'),
            (r'[)]', Punctuation, '#pop'),
            ],
        'statement': [
            include('whitespace'),
            include('statements'),
            include('parentheses'),
            (r'[;,]', Punctuation, '#pop'),
            ],
        'block-for': [
            (r';', Punctuation.BLOCKFOR, ('#pop', 'block-novardef')),
            include('block')
            ],
        'block': [
            include('whitespace'),
            (r'return', Keyword, 'block-return'),
            (r'typename', Keyword.Reserved, 'typename-statement'),
            include('keywords'),
            include('namespace'),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)(\s*)'
            #  r'((?:\[[^;]*?\])+?)',
            #  bygroups(Name, Text, using(this))),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
            #  r'(?=([<][^;]*?[>])?(\s|[*])+[a-zA-Z_][a-zA-Z0-9_]*)',
            #  Keyword.Type, 'variable'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(?:(' + _ws01 + ')*?[<][^;{}()~!%^&+=|?<>/\-]+?[>])?(?:([\s&*]|' + _ws1 + ')+?)(?:[a-zA-Z_][a-zA-Z0-9_]*))',
             Keyword.Type.BLOCK, 'variable'),

            (r'[~!%^&*+=|?:<>/-]', Operator, ('#pop', 'block-novardef')),

            (r'[\]]', Error),
            include('type-cast'),
            (r'[}]', Punctuation, '#pop'),
            include('parentheses'),
            
            (r'[;,]', Punctuation.BLOCK),
 
            include('statements')
            ],
        'block-return': [
            (r'[;]', Punctuation, '#pop'),
            include('block-novardef'),
            ],
        'block-novardef': [
            include('whitespace'),
            include('keywords'),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b(' + _ws01 + ')*?([<])',
             bygroups(Name, using(this), Operator)),

            (r'[;]', Punctuation, ('#pop', 'block')),
            include('type-cast'),
            include('parentheses'),

            include('statements'),

            ('', Text, ('#pop', 'block'))
            ],
        'block-paren': [
            include('whitespace'),
            include('keywords'),
            include('statements'),

            (r'[,;]', Punctuation),

            ('', Text, ('#pop', 'block'))
            ],
        'type-cast': [
            # TB: Attempt to detect type casting
            (r'(\()(' + _ws01 + ')'
             r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(' + _ws01 + ')([*]+)(' + _ws01 + ')(\))',
             bygroups(Operator, using(this), Keyword.Type, using(this),
                      Operator, using(this), Operator)),

            (r'(\()(' + _ws01 + ')'
             r'(unsigned|signed)'
             r'(' + _ws01 + ')([a-zA-Z_][a-zA-Z0-9_]*)(' + _ws01 + ')(\))',
             bygroups(Operator.TYPECAST, using(this), Keyword.Type, using(this),
                      Keyword.Type, using(this), Operator)),

            (r'(\()(' + _ws01 + ')'
             r'([a-zA-Z_][a-zA-Z0-9_<>&*:,\s]*?)(' + _ws01 + ')([*]+)(' + _ws01 + ')(\))',
             bygroups(Operator, using(this), Operator, using(this), Operator)),
            ],
        'class': [
            (r'^(' + _ws01 + ')(private|public|protected)(' + _ws01 + ')(:)',
             bygroups(using(this), Keyword, using(this), Punctuation)),

            include('whitespace'),

            # overloaded operator
            (r'(operator)(' + _ws01 + ')([*/+-=&()<>!~^|?\[\]]+?)'      # operator name
             r'(' + _ws01 + ')(\()',
             bygroups(Keyword, using(this), Name.Function, using(this),
                      Punctuation),
             'function-args-start'),

            (r'(using)', Keyword, 'using'),

            (r'(typename)', Keyword.Reserved, 'typename-statement'),

            include('keywords'),
            include('namespace'),

            # member functions
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'         # method name
             r'(' + _ws01 + ')(\()',
             bygroups(Name.Function, using(this),
                      Punctuation),
             'function-args-start'),

            # (r'([a-zA-Z_][a-zA-Z0-9_]*)'
            #  r'(?=(?:(?:\s*)[<][^;~!%^&+=|?/-{}()]+?[>])?(?:[\s*])+?(?:[a-zA-Z_][a-zA-Z0-9_]*))',
            #  Keyword.Type, 'variable'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b'
             r'(?=(' + _ws01 + ')*?[a-zA-Z0-9_<>*&]+?)',
             Keyword.Type),

            (r'[<]', Punctuation, 'type'),
            (r'(:)(' + _ws01 + ')*?(\d+[LlUu]*)',
             bygroups(Operator, using(this), Number.Integer)),

            (r'[~*&]', Operator),

            (r'([a-zA-Z_][a-zA-Z0-9_]*)\b',
             Name.Variable),

            (r'[=]', Operator, 'assignment'),

            # (r'([}])(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\b',
            #  bygroups(Punctuation, Text, Name.Variable), ('#pop', 'class-end')),

            (r'[}]', Punctuation, ('#pop', 'class-end')),

            # (r'([}])(?=\s*[a-zA-Z_][a-zA-Z0-9_]*\b)',
            #  Punctuation, ('#pop', 'class-end')),

            (r'[\]]', Error),

            include('parentheses'),

            (r'[;,]', Punctuation),

            ('', Text, '#pop'),
            ],
        'class-end': [
            include('whitespace'),
            include('keywords'),

            (r'[\]]', Error),
            include('parentheses'),

            (r'[a-zA-Z_][a-zA-Z0-9_]*\b', Name.Variable),
            (r'[;]', Punctuation.CLASSEND, '#pop'),

            ('', Text, '#pop')
            ],
        }

    def analyse_text(text):
        return 0.1

class PythonCBLexer(PythonLexer):
    """
    For `Python <http://www.python.org>`_ source code.
    """

    name = 'Cilk-book Python'
    aliases = ['pythoncb', 'pycb']
    filenames = ['*.py', '*.pyw', '*.sc', 'SConstruct', 'SConscript', '*.tac']
    mimetypes = ['text/x-python', 'application/x-python']

    tokens = {
        'root': [
            (r'(##)(.*$)', bygroups(Comment.Invisible, Comment.PureTeX)),
            inherit,
            ],
        }

    def analyse_text(text):
        return 0.1

class JavaCBLexer(JavaLexer):
    """
    For `Java <http://www.sun.com/java/>`_ source code.
    """

    name = 'Cilk-book Java'
    aliases = ['javacb']
    filenames = ['*.java']
    mimetypes = ['text/x-java']

    tokens = {
        'root': [
            (r'(///)(.*?\n)', bygroups(Comment.Invisible, Comment.PureTeX)),
            inherit,
            ],
        }

    def analyse_text(text):
        return 0.1


class GasCBLexer(GasLexer):
    """
    For Gas (AT&T) assembly code.
    """

    name = 'Cilk-book GAS'
    aliases = ['gascb']
    filenames = ['*.s', '*.S']
    mimetypes = ['text/x-gas']

    char = r'[a-zA-Z$._0-9@-]'
    identifier = r'(?:[a-zA-Z$_]' + char + '*|\.' + char + '+)'
    number = r'(?:0[xX][a-zA-Z0-9]+|\d+)'

    tokens = {
        'root': [
            # TB: Special assembly instructions with no explicit
            # destination register
            (r'(j|cmp|test|call|fcom|fucom)' + identifier,
             Name.Function, 'instruction-args-source'),

            inherit,
            ],
        'directive-args': [
            # TB: Added support to make blocks of code invisible.
            (r'(##<<)(.*?$)[\n]',Comment.Invisible.End, '#pop'),
            (r'(##>>)(.*?$)[\n]',Comment.Invisible.Begin, '#pop'),

            (r'(##)(.*?$)', bygroups(Comment.Invisible, Comment.PureTeX), '#pop'),

            inherit,
            ],
        'instruction-args': [
            # # Address constants
            # (r'(' + identifier + ')'
            #  r'(?=\s*[,])', Name.Constant),
            # (identifier, Name.Constant.Destination),

            # (r'(' + number + ')'
            #  r'(?=\s*[,])', Number.Integer),
            # (number, Number.Integer.Destination),

            # Registers
            (r'(%' + identifier + ')'
             r'(?=\s*[,])', Name.Variable.Source),
            ('%' + identifier, Name.Variable.Destination),

            # Indirect memory address
            (r'([(])'
             r'(?=[^)]+?[)]\s*[,])', Punctuation, 'instruction-args-source'), 

            (r'([(])'
             r'(?=[^)]+?[)])', Punctuation, 'instruction-args-destination'), 

            # TB: Added support to make blocks of code invisible.
            (r'(##<<)(.*?$)[\n]',Comment.Invisible.End, '#pop'),
            (r'(##>>)(.*?$)[\n]',Comment.Invisible.Begin, '#pop'),

            (r'(##)(.*?$)', bygroups(Comment.Invisible, Comment.PureTeX), '#pop'),

            inherit,
            ],
        'instruction-args-source': [
            ('%' + identifier, Name.Variable.Source),

            (r'[)]', Punctuation, '#pop'),

            include('instruction-args'),
            ],
        'instruction-args-destination': [
            ('%' + identifier, Name.Variable.Destination),

            (r'[)]', Punctuation, '#pop'),

            include('instruction-args'),
            ],
        'whitespace': [
            # TB: Added support to make blocks of code invisible.
            (r'(##<<)(.*?$)[\n]',Comment.Invisible.End),
            (r'(##>>)(.*?$)[\n]',Comment.Invisible.Begin),

            (r'(##)(.*?)', bygroups(Comment.Invisible, Comment.PureTeX)),

            inherit,
            ],
        }


class ObjdumpCBLexer(ObjdumpLexer):
    """
    For the output of 'objdump -dr'
    """
    name = 'objdump'
    aliases = ['objdump']
    filenames = ['*.objdump']
    mimetypes = ['text/x-objdump']

    hex = r'[0-9A-Za-z]'

    tokens = {
        'root': [
            # Code line with disassembled instructions
            ('( *)('+hex+r'+:)(\t)((?:'+hex+hex+' )+)( *\t)([a-zA-Z].*?)$',
                bygroups(Text, Name.Label, Text, Number.Hex, Text,
                         using(GasCBLexer))),
            inherit,
            ],
        }


class CilkObjdumpLexer(DelegatingLexer):
    """
    For the output of 'objdump -Sr on compiled Cilk files'
    """
    name = 'Cilk-objdump'
    aliases = ['c-objdump', 'cpp-objdump', 'cilk-objdump']
    filenames = ['*.c-objdump', '*.cpp-objdump', '*.cilk-objdump']
    mimetypes = ['text/x-c-objdump']

    def __init__(self, **options):
        super(CilkObjdumpLexer, self).__init__(CilkLexer, ObjdumpCBLexer, **options)
