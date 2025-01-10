# Copyright (c) 2021 rdbende <rdbende@gmail.com>

# Arcade is a theme for OpenMicroWind Arcade. Only features a few used widgets.
# Code is based on Azure theme from rdbende
# Images: Copyright (c) 2024 LUH Institute for Wind Energy Systems

package require Tk 8.6

namespace eval ttk::theme::arcade {

    variable version 0.1
    package provide ttk::theme::arcade $version
    variable colors
    array set colors {
        -fg             "#000000"
        -bg             "#ffffff"
        -disabledfg     "#737373"
        -disabledbg     "#ffffff"
        -selectfg       "#000000"
        -selectbg       "#cccccc"
    }

    # I took this function from the arc theme of the Sergei Golovan.
    proc LoadImages {imgdir} {
        variable I
        foreach file [glob -directory $imgdir *.png] {
            set img [file tail [file rootname $file]]
            set I($img) [image create photo -file $file -format png]
        }
    }

    LoadImages [file join [file dirname [info script]]]

    ttk::style theme create arcade -parent default -settings {
        ttk::style configure . \
            -background $colors(-bg) \
            -foreground $colors(-fg) \
            -troughcolor $colors(-bg) \
            -focuscolor $colors(-selectbg) \
            -selectbackground $colors(-selectbg) \
            -selectforeground $colors(-selectfg) \
            -fieldbackground $colors(-selectbg) \
            -font TkDefaultFont \
            -borderwidth 1 \
            -relief flat

        ttk::style map . -foreground [list disabled $colors(-disabledfg)]


        # Layouts

        ttk::style layout TButton {
            Button.button -children {
                Button.padding -children {
                    Button.label -side left -expand true
                } 
            }
        }

        ttk::style layout TLabelframe {
            Labelframe.border {
                Labelframe.padding -expand 1 -children {
                    Labelframe.label -side right
                }
            }
        }

        # Create widgets

        # Button
        ttk::style configure TButton -padding {8 4 8 4} -width -10 -anchor center

        ttk::style element create Button.button image \
            [list $I(button-basic) \
                {disabled pressed} $I(button-pressed) \
                {focus active} $I(button-basic) \
                disabled $I(button-pressed) \
                pressed $I(button-pressed) \
                active $I(button-basic) \
                focus $I(button-basic) \
            ] -border 4 -sticky ewns

        # Entry
        ttk::style element create Entry.field \
            image [list $I(entry) \
                {focus hover}    $I(entry) \
                invalid $I(entry) \
                disabled $I(entry) \
                focus    $I(entry) \
                hover    $I(entry)] \
            -border 5 -padding {6 8} -sticky news

        # Labelframe
        ttk::style element create Labelframe.border image $I(labelframe) \
            -border 8 -padding 4 -sticky news

        # Treeview
        #ttk::style element create Treeview.field \
        #    image $I(labelframe) -border -0

        #ttk::style element create Treeheading.cell \
        #    image [list $I(tree-basic) \
        #        active $I(tree-hover)
        #    ] -border 5 -padding 4 -sticky ewns

        ttk::style configure Treeview -background white
        ttk::style configure Treeview.Item -padding {2 0 0 0}
        ttk::style map Treeview \
            -background [list selected $colors(-selectbg)] \
            -foreground [list selected $colors(-selectfg)]

        # Sashes
        
        ttk::style configure TPanedwindow -width 1 -padding 0
        ttk::style map TPanedwindow -background \
            [list hover $colors(-bg)]
        
        # Set colors for other widgets
        tk_setPalette background [ttk::style lookup . -background] \
            foreground [ttk::style lookup . -foreground] \
            highlightColor [ttk::style lookup . -focuscolor] \
            selectBackground [ttk::style lookup . -selectbackground] \
            selectForeground [ttk::style lookup . -selectforeground] \
            activeBackground [ttk::style lookup . -selectbackground] \
            activeForeground [ttk::style lookup . -selectforeground]
        option add *font [ttk::style lookup . -font]
    }
}
