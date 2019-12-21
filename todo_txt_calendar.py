import sys
import re
import datetime
from typing import Iterable


class Todo:

    __date_pattern = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'
    __due_pattern = r'(?:\s+|^)due:(' + __date_pattern + r')\s*'

    def __init__(self, string: str):
        priority_or_done_pattern = r'^((\([A-Z]\))|x)'
        start_pattern = (priority_or_done_pattern
                         + r'\s(' + self.__date_pattern + r'\s){1,2}')
        self.__text = re.sub(start_pattern, '', string)
        # don't remove + and @ from text since we can use them as part of
        # sentences
        self.__text = re.sub(self.__due_pattern, ' ', self.__text).strip()
        due_date_match = re.search(self.__due_pattern, string)
        self.__due_date = None
        if due_date_match:
            due_date_string = due_date_match.group(1)
            self.__due_date = datetime.date.fromisoformat(due_date_string)

    def __str__(self) -> str:
        due_text = ' due ' + str(self.__due_date) if self.__due_date else ''
        return f'{self.__text}{due_text}'


def parse_todos(string: str) -> Iterable[Todo]:
    for line in string.splitlines():
        yield Todo(line)


todo_file_content = sys.stdin.read()
todos = parse_todos(todo_file_content)
for todo in todos:
    print(todo)
