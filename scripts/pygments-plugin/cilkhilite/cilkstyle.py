# -*- coding: utf-8 -*-
"""
    cilkhilite.cilkstyle
    ~~~~~~~~~~~~~~~~~~~~~

    A highlighting style for Cilk.

    :copyright: Copyright 2012 by Tao B. Schardl.
    :license: BSD.

    Based on pygments.style.emacs, the default Pygments style.

    :copyright: Copyright 2006-2012 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pygments.style import Style
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
     Number, Punctuation, Error, Literal, Generic, Whitespace, Token



class CilkBookStyle(Style):
    """
    The Cilk Book style, based on EmacsStyle.
    """

    background_color = "#ffffff"
    default_style = ""

    styles = {
        Whitespace:                "#bbbbbb",
        Comment:                   "#B22222",
        Comment.Special:           "",

        Comment.Invisible:         background_color,

        Comment.Preproc:           "#AA22CC",
        Comment.Preproc.Library:   "#CC22CC",
        Token.Preproc.Library:     "#CC22CC",

        Keyword:                   "#9900F8",
        Keyword.Pseudo:            "",
        Keyword.Type:              "#689300",
        Keyword.Declaration:       "#A020F0",
        Keyword.Cilk:              "#FF0000",
        Keyword.TypeDeclaration:   "#689300",

        Operator:                  "#404040",
        Operator.Word:             "#AA22FF",

        Punctuation:               "#632618",

        Name.Builtin:              "#AA22FF",
        Name.Class:                "#00BB00",
        Name.Namespace:            "#33CCCC",
        Name.Exception:            "#D2413A",
        Name.Variable:             "#B88600",
        Name.Constant:             "#5F9EA0",
        Name.Label:                "#A0A000",
        Name.Entity:               "#999999",
        Name.Attribute:            "#BB4444",
        Name.Tag:                  "#008000",
        Name.Decorator:            "#AA22FF",
        Name.VarDeclaration:       "#DE9C21",
        Name.Variable.Source:      "#632618",
        Name.Function:             "#0D00FF",
        Name:                      "#632618",

        String:                    "#BB4444",
        String.Doc:                "",
        String.Interpol:           "#BB6688",
        String.Escape:             "#BB6622",
        String.Regex:              "#BB6688",
        String.Symbol:             "#B8860B",
        String.Other:              "#008000",
        # Number:                    "#404040",
        Number:                    "#632618",

        Generic.Heading:           "#000080",
        Generic.Subheading:        "#800080",
        Generic.Deleted:           "#A00000",
        Generic.Inserted:          "#00A000",
        Generic.Error:             "#FF0000",
        Generic.Emph:              "",
        Generic.Strong:            "",
        Generic.Prompt:            "#000080",


        # Generic.Output:            "#888",
        # Generic.Output:            "#632618",
        Generic.Output:            "#000000",
        Generic.Traceback:         "#04D",

        Error:                     "border:#FF0000",

        Text:                      "#000000"
     }
