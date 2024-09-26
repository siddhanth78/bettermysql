import msvcrt
import sys
import os
import ctypes
from ctypes import wintypes
from typing import List, Tuple

kernel32 = ctypes.windll.kernel32

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes._COORD),
        ("dwCursorPosition", wintypes._COORD),
        ("wAttributes", wintypes.WORD),
        ("srWindow", wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", wintypes._COORD),
    ]

def get_cursor_position() -> Tuple[int, int]:
    h_stdout = kernel32.GetStdHandle(-11)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(h_stdout, ctypes.byref(csbi))
    return csbi.dwCursorPosition.Y + 1, csbi.dwCursorPosition.X + 1

def get_terminal_size() -> Tuple[int, int]:
    h_stdout = kernel32.GetStdHandle(-11)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(h_stdout, ctypes.byref(csbi))
    return (
        csbi.srWindow.Bottom - csbi.srWindow.Top + 1,
        csbi.srWindow.Right - csbi.srWindow.Left + 1,
    )

def wrap_text(text: str, width: int) -> List[str]:
    if not text:
        return [""]
    return [text[i : i + width] for i in range(0, len(text), width)] or [""]

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.has_empty_string = False

    def insert(self, word):
        if word == "":
            self.has_empty_string = True
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        
    def remove(self, word):
        if word == "":
            self.has_empty_string = False
            return

        def _remove(node, word, depth):
            if depth == len(word):
                if node.is_end_of_word:
                    node.is_end_of_word = False
                return len(node.children) == 0 and not node.is_end_of_word

            char = word[depth]
            if char not in node.children:
                return False

            should_delete_current_node = _remove(node.children[char], word, depth + 1)

            if should_delete_current_node:
                del node.children[char]
                return len(node.children) == 0 and not node.is_end_of_word
            return False

        _remove(self.root, word, 0)

    def find_prefix(self, prefix):
        if prefix == "":
            return [""] if self.has_empty_string else []

        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        return self._words_with_prefix(node, prefix)

    def _words_with_prefix(self, node, prefix):
        results = []
        if node.is_end_of_word:
            results.append(prefix)
        
        for char, child_node in node.children.items():
            results.extend(self._words_with_prefix(child_node, prefix + char))
        
        return results

class Wordcompleter:
    def __init__(self, words):
        words = set(words)
        words.discard("")
        words = list(words)
        self.trie = Trie()
        for word in words:
            self.trie.insert(word)
            
    def add_word(self, word):
        word = word.strip()
        if word:
            self.trie.insert(word)
        
    def add_list(self, words):
        words = set(words)
        words.discard("")
        words = list(words)
        for word in words:
            self.trie.insert(word)
            
    def remove_word(self, word):
        word = word.strip()
        if word:
            self.trie.remove(word)
        
    def remove_list(self, words):
        words = set(words)
        words.discard("")
        words = list(words)
        for word in words:
            self.trie.remove(word)

    def find_str(self, chars):
        suggestions = self.trie.find_prefix(chars)
        suggestions.sort()
        return suggestions[:10], 0

    def prompt(self, prompt_: str = "", max_size: int = None, end: str = "\n") -> str:
        end = end.replace("\n", "\n\r")
        sys.stdout.write(prompt_)
        sys.stdout.flush()
        letters = []
        suggestions = []
        sindex = 0
        word = ""
        sflag = 0
        all_words = ""
        size = 0

        terminal_height, terminal_width = get_terminal_size()
        start_row, start_col = get_cursor_position()

        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch()

                if char in (b"\r", b"\n"):
                    sys.stdout.write(end)
                    return all_words + word

                if char == b"\t":
                    if suggestions:
                        word = suggestions[sindex]
                        letters = list(word)
                        sindex = (sindex + 1) % len(suggestions)
                        sflag = 1
                elif char in (b"\b", b"\x7f"):
                    if letters:
                        letters.pop()
                        word = "".join(letters)
                        sflag = 0
                    elif all_words:
                        all_words = all_words.rstrip()
                        if all_words:
                            all_words = all_words[:-1]
                            words_list = all_words.split()
                            if words_list:
                                word = words_list[-1]
                                all_words = " ".join(words_list[:-1])
                                if all_words:
                                    all_words += " "
                                letters = list(word)
                            else:
                                word = ""
                                letters = []
                        sflag = 0
                elif char == b"\xe0":
                    arrow = msvcrt.getch().decode("utf-8")
                    if arrow == "H":
                        sindex = (sindex - 1) % len(suggestions) if suggestions else 0
                    elif arrow == "P":
                        sindex = (sindex + 1) % len(suggestions) if suggestions else 0
                    if suggestions:
                        word = suggestions[sindex-1]
                        letters = list(word)
                        sflag = 1
                else:
                    char = char.decode()
                    if char.isalnum() or char == " " or char == "_":
                        if char == " ":
                            all_words += word + " "
                            letters = []
                            word = ""
                            sflag = 0
                            size += 1
                            if size == max_size and max_size != None:
                                sys.stdout.write(end)
                                return all_words
                        else:
                            letters.append(char)
                            word = "".join(letters)
                            sflag = 0
                    else:
                        all_words += word + char
                        letters = []
                        word = ""
                        sflag = 0

                if word.strip():
                    if sflag == 0:
                        suggestions, sindex = self.find_str(word)
                else:
                    suggestions = []

                if suggestions:
                    if sflag == 1:
                        sugstr = ' | '.join(f"[{s}]" if s == suggestions[sindex-1] else s for s in suggestions)
                    else:
                        sugstr = ' | '.join(suggestions)
                        
                    display = f"{prompt_}{all_words}{word} ( {sugstr} )"
                    if len(display)%terminal_width == 0:
                        display = f"{prompt_}{all_words}{word} ( {sugstr} ) "
                else:
                    display = f"{prompt_}{all_words}{word}"
                    if len(display)%terminal_width == 0:
                        display = f"{prompt_}{all_words}{word} "
                    
                wrapped_lines = wrap_text(display, terminal_width)

                sys.stdout.write("\u001B[s")
                sys.stdout.write("\033[J")

                for i, line in enumerate(wrapped_lines):
                    current_row = start_row + i
                    if current_row >= terminal_height:
                        sys.stdout.write(f"\033[{terminal_height};1H\n")
                        start_row -= 1
                        current_row -= 1
                    sys.stdout.write(f"\033[{current_row};1H{line}")
                sys.stdout.flush()

                cursor_row = start_row + len(wrapped_lines) - 1
                cursor_col = len(wrapped_lines[-1]) % terminal_width + 1

                sys.stdout.write(f"\033[{cursor_row};{cursor_col}H")
                
                sys.stdout.write("\u001B[s")
                sys.stdout.write("\033[J")
                sys.stdout.flush()

        return all_words + word