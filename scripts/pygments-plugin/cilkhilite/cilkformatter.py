# -*- coding: utf-8 -*-
"""
    cilkhilite.cilkformatter
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Formatter for Cilk Book (LaTeX fancyvrb output).

    :copyright: Copyright 2012 by Tao B. Schardl
    :license: BSD

    Based on LaTeX formatter from pygments.formatters.latex.

    :copyright: Copyright 2006-2012 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.formatter import Formatter
from pygments.token import Token, STANDARD_TYPES
from pygments.util import get_bool_opt, get_int_opt, StringIO


__all__ = ['CilkBookFormatter']


def escape_tex(text, commandprefix):
    return text.replace('\\', '\x00'). \
                replace('{', '\x01'). \
                replace('}', '\x02'). \
                replace('\x00', r'\%sZbs{}' % commandprefix). \
                replace('\x01', r'\%sZob{}' % commandprefix). \
                replace('\x02', r'\%sZcb{}' % commandprefix). \
                replace('^', r'\%sZca{}' % commandprefix). \
                replace('_', r'\%sZus{}' % commandprefix). \
                replace('&', r'\%sZam{}' % commandprefix). \
                replace('<', r'\%sZlt{}' % commandprefix). \
                replace('>', r'\%sZgt{}' % commandprefix). \
                replace('#', r'\%sZsh{}' % commandprefix). \
                replace('%', r'\%sZpc{}' % commandprefix). \
                replace('$', r'\%sZdl{}' % commandprefix). \
                replace('-', r'\%sZhy{}' % commandprefix). \
                replace("'", r'\%sZsq{}' % commandprefix). \
                replace('"', r'\%sZdq{}' % commandprefix). \
                replace('~', r'\%sZti{}' % commandprefix)


DOC_TEMPLATE = r'''
\documentclass{%(docclass)s}
\usepackage{fancyvrb}
\usepackage{color}
\usepackage[%(encoding)s]{inputenc}
%(preamble)s

%(styledefs)s

\begin{document}

\section*{%(title)s}

%(code)s
\end{document}
'''

## Small explanation of the mess below :)
#
# The previous version of the LaTeX formatter just assigned a command to
# each token type defined in the current style.  That obviously is
# problematic if the highlighted code is produced for a different style
# than the style commands themselves.
#
# This version works much like the HTML formatter which assigns multiple
# CSS classes to each <span> tag, from the most specific to the least
# specific token type, thus falling back to the parent token type if one
# is not defined.  Here, the classes are there too and use the same short
# forms given in token.STANDARD_TYPES.
#
# Highlighted code now only uses one custom command, which by default is
# \PY and selectable by the commandprefix option (and in addition the
# escapes \PYZat, \PYZlb and \PYZrb which haven't been renamed for
# backwards compatibility purposes).
#
# \PY has two arguments: the classes, separated by +, and the text to
# render in that style.  The classes are resolved into the respective
# style commands by magic, which serves to ignore unknown classes.
#
# The magic macros are:
# * \PY@it, \PY@bf, etc. are unconditionally wrapped around the text
#   to render in \PY@do.  Their definition determines the style.
# * \PY@reset resets \PY@it etc. to do nothing.
# * \PY@toks parses the list of classes, using magic inspired by the
#   keyval package (but modified to use plusses instead of commas
#   because fancyvrb redefines commas inside its environments).
# * \PY@tok processes one class, calling the \PY@tok@classname command
#   if it exists.
# * \PY@tok@classname sets the \PY@it etc. to reflect the chosen style
#   for its class.
# * \PY resets the style, parses the classnames and then calls \PY@do.
#
# Tip: to read this code, print it out in substituted form using e.g.
# >>> print STYLE_TEMPLATE % {'cp': 'PY'}

STYLE_TEMPLATE = r'''
\makeatletter
\def\%(cp)s@reset{\let\%(cp)s@it=\relax \let\%(cp)s@bf=\relax%%
    \let\%(cp)s@ul=\relax \let\%(cp)s@tc=\relax%%
    \let\%(cp)s@bc=\relax \let\%(cp)s@ff=\relax}
\def\%(cp)s@tok#1{\csname %(cp)s@tok@#1\endcsname}
\def\%(cp)s@toks#1+{\ifx\relax#1\empty\else%%
    \%(cp)s@tok{#1}\expandafter\%(cp)s@toks\fi}
\def\%(cp)s@do#1{\%(cp)s@bc{\%(cp)s@tc{\%(cp)s@ul{%%
    \%(cp)s@it{\%(cp)s@bf{\%(cp)s@ff{#1}}}}}}}
\def\%(cp)s#1#2{\%(cp)s@reset\%(cp)s@toks#1+\relax+\%(cp)s@do{#2}}

%(styles)s

\def\%(cp)sZbs{\char`\\}
\def\%(cp)sZus{\char`\_}
\def\%(cp)sZob{\char`\{}
\def\%(cp)sZcb{\char`\}}
\def\%(cp)sZca{\char`\^}
\def\%(cp)sZam{\char`\&}
\def\%(cp)sZlt{\char`\<}
\def\%(cp)sZgt{\char`\>}
\def\%(cp)sZsh{\char`\#}
\def\%(cp)sZpc{\char`\%%}
\def\%(cp)sZdl{\char`\$}
\def\%(cp)sZhy{\char`\-}
\def\%(cp)sZsq{\char`\'}
\def\%(cp)sZdq{\char`\"}
\def\%(cp)sZti{\char`\~}
%% for compatibility with earlier versions
\def\%(cp)sZat{@}
\def\%(cp)sZlb{[}
\def\%(cp)sZrb{]}
\makeatother
'''


def _get_ttype_name(ttype):
    fname = STANDARD_TYPES.get(ttype)
    if fname:
        return fname
    aname = ''
    while fname is None:
        aname = ttype[-1] + aname
        ttype = ttype.parent
        fname = STANDARD_TYPES.get(ttype)
    return fname + aname


class CilkBookFormatter(Formatter):
    r"""
    Format tokens as LaTeX code for Cilk book. This needs the
    `fancyvrb` and `color` standard packages.

    Without the `full` option, code is formatted as one ``Verbatim``
    environment, like this:

    .. sourcecode:: latex

        \begin{Verbatim}[commandchars=\\{\}]
        \PY{k}{def }\PY{n+nf}{foo}(\PY{n}{bar}):
            \PY{k}{pass}
        \end{Verbatim}

    The special command used here (``\PY``) and all the other macros it needs
    are output by the `get_style_defs` method.

    With the `full` option, a complete LaTeX document is output, including
    the command definitions in the preamble.

    The `get_style_defs()` method of a `LatexFormatter` returns a string
    containing ``\def`` commands defining the macros needed inside the
    ``Verbatim`` environments.

    Additional options accepted:

    `style`
        The style to use, can be a string or a Style subclass (default:
        ``'default'``).

    `full`
        Tells the formatter to output a "full" document, i.e. a complete
        self-contained document (default: ``False``).

    `title`
        If `full` is true, the title that should be used to caption the
        document (default: ``''``).

    `docclass`
        If the `full` option is enabled, this is the document class to use
        (default: ``'article'``).

    `preamble`
        If the `full` option is enabled, this can be further preamble commands,
        e.g. ``\usepackage`` (default: ``''``).

    `linenos`
        If set to ``True``, output line numbers (default: ``False``).

    `linenostart`
        The line number for the first line (default: ``1``).

    `linenostep`
        If set to a number n > 1, only every nth line number is printed.

    `verbenvironment`
        The variant of the Verbatim environment to use (see the *fancyvrb* docs
        for available variants to Verbatim and guides on defining your own)
        (default: ``'Verbatim'``).  *Added in cilkhilite pygments plugin.*

    `saveverbatimname`
        The name into which the generated Verbatim environment will be
        saved, assuming that `verbenvironment` is a variant of
        SaveVerbatim (default: ``'').  This should not be specified
        unless `verbenvironment` is specified to be a variant of
        SaveVerbatim.  *Added in cilkhilite pygments plugin.*

    `verboptions`
        Additional options given to the Verbatim environment (see the *fancyvrb*
        docs for possible values) (default: ``''``).

    `commandprefix`
        The LaTeX commands used to produce colored output are constructed
        using this prefix and some letters (default: ``'PY'``).
        *New in Pygments 0.7.*

        *New in Pygments 0.10:* the default is now ``'PY'`` instead of ``'C'``.

    `texcomments`
        If set to ``True``, enables LaTeX comment lines.  That is, LaTex markup
        in comment tokens is not escaped so that LaTeX can render it (default:
        ``False``).  *New in Pygments 1.2.*

    `mathescape`
        If set to ``True``, enables LaTeX math mode escape in comments. That
        is, ``'$...$'`` inside a comment will trigger math mode (default:
        ``False``).  *New in Pygments 1.2.*

    `inline`
        If set to ``True``, elides the initial line

            \begin{Verbatim}[commandchars=\\{\}]

        and the final line

            \end{Verbatim}
        
        from the LaTeX output.  This is useful for inserting pygmentized code
        in line with text using an inlined verbatim command like  ``'\verb'``
        (default: ``False``).  *Added in cilkhilite pygments plugin.*

    `hidebydefault`
        If set to ``True``, assumes that code in the file should not be
        pygmentized by default unless it is explicitly made visible.  In Cilk
        code, the lines

            ///<<

        and
        
            ///>>
        
        will make an enclosed region of code in the document visible in the
        pygmentized output.  The ``'/** END HIDDEN **/'`` and
        ``'/** BEGIN HIDDEN **/'`` lines will also render the intervening
        lines of code visible in the pygmentized output (default: ``False``).
        *Added in cilkhilite pygments plugin.*

    `reindent`
        If set to ``True``, reindents the visible pygmentized code such that
        the first line in each visible piece has no indentation (default:
        ``False``).  *Added in cilkhilite pygments plugin.*
    """
    name = 'CilkBookFormatter'
    aliases = ['cilkbook']
    filenames = ['*.tex']

    def __init__(self, **options):
        Formatter.__init__(self, **options)
        self.docclass = options.get('docclass', 'article')
        self.preamble = options.get('preamble', '')
        self.linenos = get_bool_opt(options, 'linenos', False)
        self.linenostart = abs(get_int_opt(options, 'linenostart', 1))
        self.linenostep = abs(get_int_opt(options, 'linenostep', 1))
        self.verbenvironment = options.get('verbenvironment', 'Verbatim')
        self.saveverbatimname = options.get('saveverbatimname', '')
        self.verboptions = options.get('verboptions', '')
        self.nobackground = get_bool_opt(options, 'nobackground', False)
        self.commandprefix = options.get('commandprefix', 'PY')
        self.texcomments = get_bool_opt(options, 'texcomments', False)
        self.mathescape = get_bool_opt(options, 'mathescape', False)
        # New options added with cilkhilite pygments plugin
        self.inline = get_bool_opt(options, 'inline', False)
        self.hidebydefault = get_bool_opt(options, 'hidebydefault', False)
        self.reindent = get_bool_opt(options, 'reindent', False)

        self._create_stylesheet()


    def _create_stylesheet(self):
        t2n = self.ttype2name = {Token: ''}
        c2d = self.cmd2def = {}
        cp = self.commandprefix

        def rgbcolor(col):
            if col:
                return ','.join(['%.2f' %(int(col[i] + col[i + 1], 16) / 255.0)
                                 for i in (0, 2, 4)])
            else:
                return '1,1,1'

        for ttype, ndef in self.style:
            name = _get_ttype_name(ttype)
            cmndef = ''
            if ndef['bold']:
                cmndef += r'\let\$$@bf=\textbf'
            if ndef['italic']:
                cmndef += r'\let\$$@it=\textit'
            if ndef['underline']:
                cmndef += r'\let\$$@ul=\underline'
            if ndef['roman']:
                cmndef += r'\let\$$@ff=\textrm'
            if ndef['sans']:
                cmndef += r'\let\$$@ff=\textsf'
            if ndef['mono']:
                cmndef += r'\let\$$@ff=\textsf'
            if ndef['color']:
                cmndef += (r'\def\$$@tc##1{\textcolor[rgb]{%s}{##1}}' %
                           rgbcolor(ndef['color']))
            if ndef['border']:
                cmndef += (r'\def\$$@bc##1{\setlength{\fboxsep}{0pt}'
                           r'\fcolorbox[rgb]{%s}{%s}{\strut ##1}}' %
                           (rgbcolor(ndef['border']),
                            rgbcolor(ndef['bgcolor'])))
            elif ndef['bgcolor']:
                cmndef += (r'\def\$$@bc##1{\setlength{\fboxsep}{0pt}'
                           r'\colorbox[rgb]{%s}{\strut ##1}}' %
                           rgbcolor(ndef['bgcolor']))
            if cmndef == '':
                continue
            cmndef = cmndef.replace('$$', cp)
            t2n[ttype] = name
            c2d[name] = cmndef

    def get_style_defs(self, arg=''):
        """
        Return the command sequences needed to define the commands
        used to format text in the verbatim environment. ``arg`` is ignored.
        """
        cp = self.commandprefix
        styles = []
        for name, definition in self.cmd2def.iteritems():
            styles.append(r'\expandafter\def\csname %s@tok@%s\endcsname{%s}' %
                          (cp, name, definition))
        return STYLE_TEMPLATE % {'cp': self.commandprefix,
                                 'styles': '\n'.join(styles)}

    def format_unencoded(self, tokensource, outfile):
        # TODO: add support for background colors
        t2n = self.ttype2name
        cp = self.commandprefix

        if self.full:
            realoutfile = outfile
            outfile = StringIO()

        # TB: Added support for "inline" feature
        if not self.inline:
            # TB: Added support for custom Verbatim environment definition.
            # outfile.write(r'\begin{Verbatim}[commandchars=\\\{\}')
            outfile.write(r'\begin{' + self.verbenvironment + r'}[commandchars=\\\{\}')

            if self.linenos:
                start, step = self.linenostart, self.linenostep
                outfile.write(',numbers=left' +
                              (start and ',firstnumber=%d' % start or '') +
                              (step and ',stepnumber=%d' % step or ''))
            if self.mathescape or self.texcomments:
                outfile.write(r',codes={\catcode`\$=3\catcode`\^=7\catcode`\_=8}')
            if self.verboptions:
                outfile.write(',' + self.verboptions)
            outfile.write(']')
            if self.saveverbatimname != "":
                outfile.write('{' + self.saveverbatimname + '}')
            outfile.write('\n')

        # TB: Added functionality to skip formatting content between
        # Comment.Invisible.Begin and Comment.Invisible.End tokens.
        # If self.hidebydefault, then assume the file begins with a
        # Comment.Invisible.Begin token.
        skiptoken = self.hidebydefault
        # TB: Added functionality to reindent the output such that the
        # first line has no indentation.  The way this works is that
        # we measure the whitespace prefix on the first line we output
        # and store it in 'initialindent'.  On all subsequent lines,
        # we try to find 'initialindent' at the start of the line and
        # remove it.  If we can't find 'initialindent' at the start of
        # the line, we simply output the line as is.
        reindent = self.reindent
        initialindent = ''
        find_next_indent = self.reindent
        newline = False
        # TB: Boolean flag to track whether or not we've produced any
        # lines of output.  The Verbatim environment gets unhappy if
        # it has no contents, so if we don't output anything else,
        # output a newline.
        wrotelines = False

        for ttype, value in tokensource:
            if ttype in Token.Comment.Invisible.End:
                skiptoken = False
                continue
            if ttype in Token.Comment.Invisible.Begin:
                skiptoken = True
                continue
            if skiptoken:
                continue

            if reindent:
                # Get the indentation of the first line
                if find_next_indent:
                    if ttype is Token.Text:
                        indent_match = re.match(r'^[ \t\f\v]+', value) # Ignore newlines
                        if indent_match is not None:
                            initialindent = indent_match.group(0)
                            value = value[indent_match.end():]
                    find_next_indent = False
                    newline = False

                # Insert any newlines at beginning of value
                newline_match = re.match(r'^\n+', value)
                if newline_match is not None:
                    outfile.write(newline_match.group(0))
                    newline = True
                    value = value[newline_match.end():]

                # If we're on a new line, remove indentation
                elif newline:
                    if ttype is Token.Text:
                        indent_match = re.match('^(' + initialindent + ')', value)
                        if indent_match is not None:
                            value = value[indent_match.end():]
                    # Indentation does not contain newlines, so we're not on a new line anymore
                    newline = False

            if ttype in Token.Comment and ttype not in Token.Comment.PureTeX:

                # TB: These two lines to remove invisible comment
                # characters.
                if ttype in Token.Comment.Invisible:
                    continue

                elif self.texcomments:
                    # # TB: The following code formats "Pure TeX"
                    # # comments correctly.
                    # if ttype not in Token.Comment.PureTeX:
                        
                    #     # Try to guess comment starting lexeme and escape it ...
                    #     start = value[0:1]
                    #     for i in xrange(1, len(value)):
                    #         if start[0] != value[i]:
                    #             break
                    #         start += value[i]

                    #     value = value[len(start):]
                    #     start = escape_tex(start, self.commandprefix)

                    #     # ... but do not escape inside comment.
                    #     value = start + value

                    # Try to guess comment starting lexeme and escape it ...
                    start = value[0:1]
                    for i in xrange(1, len(value)):
                        if start[0] != value[i]:
                            break
                        start += value[i]

                    value = value[len(start):]
                    start = escape_tex(start, self.commandprefix)

                    # ... but do not escape inside comment.
                    value = start + value
                elif self.mathescape:
                    # Only escape parts not inside a math environment.
                    parts = value.split('$')
                    in_math = False
                    for i, part in enumerate(parts):
                        if not in_math:
                            parts[i] = escape_tex(part, self.commandprefix)
                        in_math = not in_math
                    value = '$'.join(parts)
                else:
                    value = escape_tex(value, self.commandprefix)
            elif ttype not in Token.Comment.PureTeX:
                value = escape_tex(value, self.commandprefix)
            styles = []
            while ttype is not Token:
                try:
                    styles.append(t2n[ttype])
                except KeyError:
                    # not in current style
                    styles.append(_get_ttype_name(ttype))
                ttype = ttype.parent
            styleval = '+'.join(reversed(styles))
            if styleval:
                spl = value.split('\n')
                for line in spl[:-1]:
                    if line:
                        outfile.write("\\%s{%s}{%s}" % (cp, styleval, line))
                    newline = True
                    outfile.write('\n')
                    wrotelines = True
                if spl[-1]:
                    outfile.write("\\%s{%s}{%s}" % (cp, styleval, spl[-1]))
                    wrotelines = True

            else:
                spl = value.split('\n')
                for line in spl[:-1]:
                    if line:
                        # Attempt to remove indentation
                        if reindent and newline:
                            indent_match = re.match('^(' + initialindent + ')', line)
                            if indent_match is not None:
                                line = line[indent_match.end():]
                        outfile.write(line)
                    newline = True
                    outfile.write('\n')
                    wrotelines = True
                if spl[-1]:
                    line = spl[-1]
                    # Attempt to remove indentation
                    if reindent and newline:
                        indent_match = re.match('^(' + initialindent + ')', line)
                        if indent_match is not None:
                            line = line[indent_match.end():]
                    outfile.write(line)
                    wrotelines = True
                    newline = False

        if not self.inline:
            if not wrotelines:
                outfile.write('\n')
            # TB: Adding support for custom Verbatim environments
            # outfile.write('\\end{Verbatim}\n')
            outfile.write('\\end{' + self.verbenvironment + '}\n')

        if self.full:
            realoutfile.write(DOC_TEMPLATE %
                dict(docclass  = self.docclass,
                     preamble  = self.preamble,
                     title     = self.title,
                     encoding  = self.encoding or 'latin1',
                     styledefs = self.get_style_defs(),
                     code      = outfile.getvalue()))
