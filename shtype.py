#!/usr/bin/env python3
"""
shtype.py

This module provides a class Shtype that queries Pygments for all lexers,
extracts supported file extension patterns (in the form "*.ext"), and builds
mappings between file extensions and language names.

Methods provided:
  - is_supported_extension(extension): returns True if the extension is supported.
  - list_supported_extensions(): returns a sorted list of supported extensions.
  - get_languages_by_extension(extension): returns the list of language names for the extension.
  - get_extensions_by_language(language): returns the list of extensions for the given language name.

Note:
  File patterns that do not follow the form "*.ext" are ignored.
  The language name used is the lexer's long name.
"""

import re
from pygments.lexers import get_all_lexers

class Shtype:
    def __init__(self):
        # Mappings:
        #   ext_to_lang: key = file extension (with dot, e.g. ".py"), value = set of language names
        #   lang_to_ext: key = language name, value = set of file extensions
        self.ext_to_lang = {}
        self.lang_to_ext = {}
        self._build_mappings()

    def _build_mappings(self):
        """
        Iterate over all lexers from Pygments and build two mappings:
          - From extension to language names.
          - From language names to file extensions.
        Only patterns matching the glob format "*.ext" are considered.
        """
        for longname, aliases, filenames, mimetypes in get_all_lexers():
            language_name = longname  # Use the long language name.
            if filenames:
                for pattern in filenames:
                    # Only consider patterns like "*.ext"
                    m = re.match(r"\*\.(\w+)$", pattern)
                    if m:
                        ext = "." + m.group(1)
                        self.ext_to_lang.setdefault(ext, set()).add(language_name)
                        self.lang_to_ext.setdefault(language_name, set()).add(ext)
        # Convert sets to sorted lists
        self.ext_to_lang = {ext: sorted(langs) for ext, langs in self.ext_to_lang.items()}
        self.lang_to_ext = {lang: sorted(exts) for lang, exts in self.lang_to_ext.items()}

    def is_supported_extension(self, extension):
        """
        Returns True if the given file extension (e.g. ".py") is supported by Pygments.
        """
        return extension in self.ext_to_lang

    def list_supported_extensions(self):
        """
        Returns a sorted list of all supported file extensions.
        """
        return sorted(self.ext_to_lang.keys())

    def get_languages_by_extension(self, extension):
        """
        Given a file extension (e.g. ".py"), return a sorted list of language names that support it.
        If the extension is not found, returns an empty list.
        """
        return self.ext_to_lang.get(extension, [])

    def get_extensions_by_language(self, language):
        """
        Given a language name (as recognized by Pygments' long name, e.g. "Python"),
        returns a sorted list of file extensions associated with that language.
        If the language is not found, returns an empty list.
        """
        return self.lang_to_ext.get(language, [])

# If run as a stand-alone script, print out some sample mappings.
if __name__ == "__main__":
    shtype = Shtype()
    print("Supported Extensions:")
    for ext in shtype.list_supported_extensions():
        print(f"{ext}: {shtype.get_languages_by_extension(ext)}")
    
    # Example lookup by language.
    sample_language = "Python"
    print(f"\nExtensions for {sample_language}: {shtype.get_extensions_by_language(sample_language)}")
    
    # Example check for supported extension.
    sample_ext = ".py"
    print(f"\nIs '{sample_ext}' supported? {shtype.is_supported_extension(sample_ext)}")
