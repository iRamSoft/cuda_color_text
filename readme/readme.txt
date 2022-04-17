Plugin for CudaText.
Gives commands to colorize text fragments with several styles,
by background color and/or font style (italic/bold/strikeout).

To configure, call menu item in the "Options/ Settings-plugins / Color Text"
to edit config file. Options are boolean, values 0/1 for off/on.

- all_words: Colorize all occurrences of fragment.
     When this option is on (ie "all_words=1"), you can just click
     the word, without selecting it first.
- case_sensitive: Case-sensitive search for other occurrences.
- whole_words: Colorize only those occurrences, which are whole words.
- show_on_map: Show added colored marks also on micro-map.

Plugin saves applied attribs to the helper file (*.cuda-colortext) and 
restores attribs later on file opening. On applying attrib, plugin marks 
file as "modified", it is Ok, it's needed to save the helper file.
You can delete that helper file, to forget about all added attribs.


Authors:
- Alexey Torgashin (CudaText)
- Khomutov Roman
License: MIT
