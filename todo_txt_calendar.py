import sys
import re
import datetime
import calendar
import operator
import cmd
from typing import Iterable, Optional, Callable


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

    @property
    def due_date(self) -> Optional[datetime.date]:
        return self.__due_date


class TodoCalendar(calendar.TextCalendar):

    def __init__(self, todos: Iterable[Todo], firstweekday: int = 0):
        super().__init__(firstweekday)
        self.__todos = todos

    def __count_todos_for_date(self, date: datetime.date) -> int:
        def predicate(todo: Todo) -> bool:
            return bool(todo.due_date) and todo.due_date == date
        return len(tuple(filter(predicate, self.__todos)))

    def formatmonth(self, year: int, month: int, width: int = 0, height=0) -> str:
        def get_abbr(n: int) -> str:
            return calendar.day_abbr[n][:-1]

        def make_week_string(week: Iterable[int]) -> str:
            return (''.join(map(lambda d: d and str(f'{str(d).ljust(2)} ({self.__count_todos_for_date(datetime.date(year, month, d))})').ljust(
                width) or ' ' * width, week)))

        month_str = calendar.month_name[month]
        min_width = 6
        width = max(width, min_width)
        weekday_abbrs = map(get_abbr, self.iterweekdays())
        week_header = (' ' * (width - 2)).join(weekday_abbrs)
        days = '\n'.join(make_week_string(week) for week in self.monthdayscalendar(year, month))
        return f'{month_str} {year}\n{week_header}\n{days}\n'


class CLI(cmd.Cmd):
    intro = 'Welcome to the todo.txt calendar. Type help or ? for help.\n'
    prompt = 'top level> '

    def do_m(self, arg: str) -> None:
        # view month (like in Google Calendar)
        TodoCalendar(todos, 6).prmonth(
            datetime.date.today().year, datetime.date.today().month, 8)

    def do_due(self, arg: str) -> None:
        def month_equal(todo: Todo) -> bool:
            return bool(todo.due_date and todo.due_date.month == 12)
        # list tasks due in the selected month in ascending due date order
        print('Due this month:')

        months_todos = filter(month_equal, todos)
        get_due_date: Callable[[Todo], datetime.date] = operator.attrgetter('due_date')
        months_todos_sorted = sorted(months_todos, key=get_due_date)
        print(*months_todos_sorted, sep='\n')


def parse_todos(string: str) -> Iterable[Todo]:
    for line in string.splitlines():
        yield Todo(line)


with open(sys.argv[1]) as file:
    todo_file_content = file.read()
todos = tuple(parse_todos(todo_file_content))

CLI().cmdloop()
