# -*- coding: utf-8 -*-
"""
    cilkhilite.chrtfformatter
    ~~~~~~~~~~~~~~~~~~~~~~~

    A formatter that generates RTF files from lexed codehilite inputs.

    :copyright: Copyright 2012 by Tao B. Schardl
    :license: BSD

    Based on RTF formatter from pygments.formatters.rtf.

    :copyright: Copyright 2006-2012 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.formatter import Formatter
from pygments.token import Token, STANDARD_TYPES
from pygments.util import get_bool_opt

__all__ = ['CHRtfFormatter']


class CHRtfFormatter(Formatter):
    """
    Format tokens as RTF markup.  This formatter automatically outputs
    full RTF documents with color information and other useful stuff.
    Perfect for Copy and Paste into Microsoft® Word® documents.
    Supports formatting options added with codehilite plugin.

    *New in Pygments 0.6.*

    Additional options accepted:

    `style`
        The style to use, can be a string or a Style subclass (default:
        ``'default'``).

    `fontface`
        The used font famliy, for example ``Bitstream Vera Sans``. Defaults to
        some generic font which is supposed to have fixed width.
    
    *New with codehilite plugin.*

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

    `reindent`
        If set to ``True``, reindents the visible pygmentized code such that
        the first line in each visible piece has no indentation (default:
        ``False``).
    """
    name = 'CHRTFFormatter'
    aliases = ['chrtf']
    filenames = ['*.rtf']

    unicodeoutput = False

    def __init__(self, **options):
        """
        Additional options accepted:

        ``fontface``
            Name of the font used. Could for example be ``'Courier New'``
            to further specify the default which is ``'\fmodern'``. The RTF
            specification claims that ``\fmodern`` are "Fixed-pitch serif
            and sans serif fonts". Hope every RTF implementation thinks
            the same about modern...
        """
        Formatter.__init__(self, **options)
        self.fontface = options.get('fontface') or ''
        # New options added with cilkhilite pygments plugin
        self.hidebydefault = get_bool_opt(options, 'hidebydefault', False)
        self.reindent = get_bool_opt(options, 'reindent', False)

    def _escape(self, text):
        return text.replace('\\', '\\\\') \
                   .replace('{', '\\{') \
                   .replace('}', '\\}')

    def _escape_text(self, text):
        # empty strings, should give a small performance improvment
        if not text:
            return ''

        # escape text
        text = self._escape(text)
        if self.encoding in ('utf-8', 'utf-16', 'utf-32'):
            encoding = 'iso-8859-15'
        else:
            encoding = self.encoding or 'iso-8859-15'

        buf = []
        for c in text:
            if ord(c) > 128:
                ansic = c.encode(encoding, 'ignore') or '?'
                if ord(ansic) > 128:
                    ansic = '\\\'%x' % ord(ansic)
                else:
                    ansic = c
                buf.append(r'\ud{\u%d%s}' % (ord(c), ansic))
            else:
                buf.append(str(c))

        return ''.join(buf).replace('\n', '\\par\n')

    def format_unencoded(self, tokensource, outfile):
        # rtf 1.8 header
        outfile.write(r'{\rtf1\ansi\deff0'
                      r'{\fonttbl{\f0\fmodern\fprq1\fcharset0%s;}}'
                      r'{\colortbl;' % (self.fontface and
                                        ' ' + self._escape(self.fontface) or
                                        ''))

        # convert colors and save them in a mapping to access them later.
        color_mapping = {}
        offset = 1
        for _, style in self.style:
            for color in style['color'], style['bgcolor'], style['border']:
                if color and color not in color_mapping:
                    color_mapping[color] = offset
                    outfile.write(r'\red%d\green%d\blue%d;' % (
                        int(color[0:2], 16),
                        int(color[2:4], 16),
                        int(color[4:6], 16)
                    ))
                    offset += 1
        outfile.write(r'}\f0')

        # highlight stream
        # TB 09/09/2012: Added functionality to skip invisible comments.
        skiptoken = self.hidebydefault
        initialindent = ''
        reindent = self.reindent
        find_next_indent = self.reindent
        newline = False

        for ttype, value in tokensource:
            # TB 09/09/2012: Ellide invisible comment blocks
            if ttype in Token.Comment.Invisible.End:
                skiptoken = False
                #find_next_indent = self.reindent
                continue
            if ttype in Token.Comment.Invisible.Begin:
                skiptoken = True
                continue
            if skiptoken:
                continue

            # TB 09/09/2012: Adding code to reindent input
            if reindent:
                # newline_match = re.match(r'\n', value)
                # if newline_match is not None:
                #     newline = True

                # If we entered a new visible block, get the indentation of the first line
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
                    outfile.write(self._escape_text(newline_match.group(0)))
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

            # TB 09/09/2012: These two lines to remove invisible
            # comment characters.
            if ttype in Token.Comment.Invisible:
                continue

            # TB 09/09/2012: Also ellide PureTeX comments from RTF
            # output, but keep the newlines.
            if ttype in Token.Comment.PureTeX:
                newlines = re.findall(r'\n', value)
                value = ''.join(newlines)
                newline = True

            while not self.style.styles_token(ttype) and ttype.parent:
                ttype = ttype.parent
            style = self.style.style_for_token(ttype)
            buf = []
            if style['bgcolor']:
                buf.append(r'\cb%d' % color_mapping[style['bgcolor']])
            if style['color']:
                buf.append(r'\cf%d' % color_mapping[style['color']])
            if style['bold']:
                buf.append(r'\b')
            if style['italic']:
                buf.append(r'\i')
            if style['underline']:
                buf.append(r'\ul')
            if style['border']:
                buf.append(r'\chbrdr\chcfpat%d' %
                           color_mapping[style['border']])
            start = ''.join(buf)
            if start:
                outfile.write('{%s ' % start)
            # TB 09/09/2012: Replacing previous code to write escaped line to output
            # with new code that reindents input.
            # outfile.write(self._escape_text(value))
            spl = value.split('\n')
            for line in spl[:-1]:
                if line:
                    # If we're on a new line, remove indentation
                    if reindent and newline:
                        indent_match = re.match('^(' + initialindent + ')', line)
                        if indent_match is not None:
                            line = line[indent_match.end():]
                    outfile.write(self._escape_text(line))
                newline = True
                outfile.write(self._escape_text('\n'))
            if spl[-1]:
                line = spl[-1]
                if reindent and newline:
                    indent_match = re.match('^(' + initialindent + ')', line)
                    if indent_match is not None:
                        line = line[indent_match.end():]
                outfile.write(self._escape_text(line))
                newline = False

            if start:
                outfile.write('}')

        outfile.write('}')
