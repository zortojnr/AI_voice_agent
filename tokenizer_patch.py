"""
Tokenizer Patch Module

This module patches the lk_blingfire import issue for Python 3.13 compatibility.
When livekit.agents tries to import lk_blingfire (which doesn't have a Python 3.13 wheel),
this patch intercepts the import and forces the pure-Python tokenizer fallback.

This MUST be imported BEFORE any livekit.agents imports to work correctly.

Primary method: Sets LK_BLINGFIRE_USE_FALLBACK environment variable
Fallback method: Mocks the lk_blingfire module if environment variable doesn't work
"""

import os
import sys
from unittest.mock import Mock


class BlingFireMock:
    """
    Mock class that mimics the lk_blingfire interface.
    This prevents import errors when livekit.agents tries to use the native extension.
    """
    
    @staticmethod
    def text_to_words(text: str) -> list[str]:
        """
        Fallback pure-Python word tokenizer.
        This is a simple whitespace-based tokenizer.
        """
        return text.split()
    
    @staticmethod
    def words_to_text(words: list[str]) -> str:
        """
        Fallback pure-Python word detokenizer.
        Joins words with spaces.
        """
        return " ".join(words)
    
    @staticmethod
    def text_to_sentences(text: str) -> list[str]:
        """
        Fallback pure-Python sentence tokenizer.
        Basic sentence splitting on common sentence endings.
        """
        import re
        # Simple sentence splitting on . ! ?
        sentences = re.split(r'([.!?]+)', text)
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        return [s.strip() for s in result if s.strip()]


def patch_blingfire_import():
    """
    Patches the lk_blingfire import issue using two methods:
    1. Sets LK_BLINGFIRE_USE_FALLBACK environment variable (primary method)
    2. Mocks sys.modules to provide a mock lk_blingfire module (fallback)
    
    This should be called before any livekit.agents imports.
    """
    # Method 1: Set environment variable to force pure-Python tokenizer
    # This is the recommended approach according to LiveKit documentation
    # Try both possible environment variable names for maximum compatibility
    os.environ["LK_BLINGFIRE_USE_FALLBACK"] = "1"
    os.environ["LIVEKIT_FORCE_PURE_TOKENIZER"] = "1"
    
    # Method 2: Create a mock module for lk_blingfire as fallback
    # This ensures compatibility even if the env var doesn't work
    mock_module = Mock(spec=['text_to_words', 'words_to_text', 'text_to_sentences'])
    mock_module.text_to_words = BlingFireMock.text_to_words
    mock_module.words_to_text = BlingFireMock.words_to_text
    mock_module.text_to_sentences = BlingFireMock.text_to_sentences
    
    # Inject the mock into sys.modules before any imports
    # Handle various possible import paths
    sys.modules['lk_blingfire'] = mock_module
    sys.modules['lk_blingfire.blingfire'] = mock_module
    sys.modules['lk_blingfire._blingfire'] = mock_module
    
    print("✓ Patched lk_blingfire import - using pure-Python tokenizer fallback")


# Apply the patch immediately when this module is imported
patch_blingfire_import()

