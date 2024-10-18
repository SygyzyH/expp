import line_consumer
import syntax_error

import curses
import logging

def start():
    curses.wrapper(_start)

class TextContainer:
    ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-=!@#$%^&*()_+[]\\{}|;':\",./<>? \n"
    def __init__(self) -> None:
        self._text = [""]
        self.row = 0
        self.col = 0

    def add_char(self, char: str):
        before = self._text[self.row][:self.col]
        after = self._text[self.row][self.col:] # and including
        if char == '\n':
            self.col = 0
            self._text[self.row] = before
            self.row += 1
            self._text.insert(self.row, after)
        else:
            self.col += 1
            self._text[self.row] = before + char + after

    def delete_current_char(self):
        self._text[self.row] = self._text[self.row][:self.col] + self._text[self.row][self.col + 1:]
    def delete_back_char(self):
        self._text[self.row] = self._text[self.row][:max(0, self.col - 1)] + self._text[self.row][self.col:]
        if self.col == 0:
            if self.row > 0:
                self._text.pop(self.row)
            self.move_up()
            self.move_end()
        else:
            self.move_left()

    def move_right(self):
        self.col = min(len(self._text[self.row]), self.col + 1)
    def move_left(self):
        self.col = max(0, self.col - 1)
    def move_up(self):
        self.row = max(0, self.row - 1)
        self.col = min(len(self._text[self.row]), self.col)
    def move_down(self):
        self.row += 1
        if len(self._text) == self.row:
            self._text.append("")
        self.col = min(len(self._text[self.row]), self.col)
    def move_end(self):
        self.col = len(self._text[self.row])
    def move_start(self):
        self.col = 0
    
    def getbox(self, row, col, max_row, max_col, empty_char=" "):
        final = [empty_char * max_col] * max_row
        for r in range(row, max_row):
            for c in range(col, max_col):
                try:
                    char = self._text[r][c]
                except:
                    char = empty_char
                final[r] = final[r][:c] + char + final[r][c:]
                
        return final
    
    def getlines(self):
        return self._text

def _start(stdscr: curses.window):
    container = TextContainer()

    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(2)
    # Error colors
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    rows, cols = stdscr.getmaxyx()
    stdscr.clear()

    input_window = curses.newwin(rows, cols//2, 0, 0)
    input_window.move(1, 1)
    output_window = curses.newwin(rows, cols//2, 0, cols//2)
    output_window.move(1, 1)

    stdscr.refresh()

    char = 0

    while True:
        if char == curses.KEY_RESIZE:
            rows, cols = stdscr.getmaxyx()
            logging.debug(f"updating to {rows} {cols}")
            curses.resize_term(rows, cols)
            output_window.resize(rows, cols//2)
            output_window.mvwin(0, cols//2)
            input_window.resize(rows, cols//2)
        elif char == curses.KEY_UP:
            container.move_up()
        elif char == curses.KEY_DOWN:
            container.move_down()
        elif char == curses.KEY_LEFT:
            container.move_left()
        elif char == curses.KEY_RIGHT:
            container.move_right()
        elif char == curses.KEY_DC:
            container.delete_current_char()
        elif char in (curses.KEY_BACKSPACE, ord('\b')):
            container.delete_back_char()
        elif char == curses.KEY_HOME:
            container.move_start()
        elif char == curses.KEY_END:
            container.move_end()
        elif chr(char) in TextContainer.ALLOWED_CHARS:
            container.add_char(chr(char))

        input_window.move(0, 0)
        input_window.clear()
        irows, icols = input_window.getmaxyx()
        # Need to account for borders, so actual size is smaller
        for i, line in enumerate(container.getbox(max(0, container.row - irows), 0, irows - 2, icols - 1)):
            input_window.move(i + 1, 1)
            input_window.addstr(line)
        input_window.move(container.row + 1, container.col + 1)
        input_window.border()

        #stdscr.clear()
        output_window.move(0, 0)
        output_window.clear()
        orows, ocols = output_window.getmaxyx()
        expression_history = []
        result_history = []
        i = 0
        for line_number, line in enumerate(container.getlines()):
            output_window.move(i + 1, 1)
            try:
                result = line_consumer.consume_line(line, expression_history, result_history)
                if result is not None:
                    output_window.addnstr(f"{len(result_history)} : {result}", -1)
                    if len(result) >= ocols - 1:
                        i += 1
            except (syntax_error.SyntaxError, AssertionError) as e:
                if isinstance(e, AssertionError):
                    e = e.args[0]
                output_window.addnstr(str(e), -1)
                if len(str(e)) >= ocols - 1:
                        i += 1

                last_input_cursor = input_window.getyx()
                offending_character = input_window.inch(line_number + 1, e.col + 1)
                input_window.addch(line_number + 1, e.col + 1, offending_character, curses.color_pair(1))
                input_window.move(*last_input_cursor)
            except Exception as e:
                output_window.addnstr(f"{e.__class__.__name__}: {str(e)}", -1)
                if len(f"{e.__class__.__name__}: {str(e)}") >= ocols - 1:
                        i += 1
            i += 1
        output_window.border()

        input_window.noutrefresh()
        output_window.noutrefresh()
        
        stdscr.move(*input_window.getyx())
        stdscr.refresh()

        char = stdscr.getch()
        

if __name__ == "__main__":
    start()