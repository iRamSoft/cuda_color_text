Plugin for CudaText.
Gives commands to colorize text fragments with several styles
(background color + font style: italic/bold/strikeout).
It is like function "Style token" in Notepad++.
Uses selected text, without selection uses word under first caret.

Gives menu item in "Options/ Settings-plugins" to edit config file.
Options:
- all_words: Colorize all occurrences of fragment
- case_sensitive: Case sensitive search for other occurrences
- whole_words: Colorize only those occurrences, which are whole words
- show_on_map: Show added colored marks also on micro-map.

Plugin also saves applied attribs to helper file (*.cuda-colortext) and 
restores attribs later on file opening. On applying attrib, plugin marks 
file as "modified", it is Ok, it's needed to save helper file.


Authors:
- Alexey Torgashin (CudaText)
- Khomutov Roman
License: MIT
