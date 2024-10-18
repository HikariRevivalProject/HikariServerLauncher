# HSL Locale Module
from typing import Any, Union
from hsl.core.exceptions import LanguageNotSupportedException
import os
import sys
import json
from rich.console import Console
from hsl.core.config import Config
console = Console()
class Locale():
    def __init__(self):
        self.config = Config().load()
        self.language = self.config.language
        self.debug = self.config.debug
        self.language_key = {}
        self.set_language(self.language)
    def set_language(self, language: str) -> None:
        self.language = language
        self.packaged = bool(getattr(sys, '_MEIPASS', False))
        base_path = sys._MEIPASS if self.packaged else os.path.abspath(".") # type: ignore
        file_path = os.path.join(base_path, 'lang', f'{self.language}.json')
        if self.debug:
            console.log(f'Loading language file {file_path}')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.language_key = json.load(f)
        except FileNotFoundError as e:
            raise LanguageNotSupportedException(
                f'Language {self.language} is not supported.'
            ) from e
    def replace(self, text: str, replaces: dict[str, str] = {}) -> str:
        for k, v in replaces.items():
            text = text.replace(f'{{{k}}}', v)
        return text
    def trans_key(self, key: Union[str, list[str]], /, **replaces: str) -> Any: # type: ignore
        if isinstance(key, str):
            #console.log(f'Translating key {key} in {self.language} replaces: {replaces}')
            return self.replace(self.language_key.get(key, key), replaces)
        if isinstance(key, list):
            _texts = []
            for k in key:
                #console.log(f'Translating key {k} in {self.language} replaces: {replaces}')
                _texts.append(self.language_key.get(k, k))
            return [self.replace(text, replaces) for text in _texts]
        return None