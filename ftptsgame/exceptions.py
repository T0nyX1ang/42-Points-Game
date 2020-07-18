"""Exception classes used in the project."""


__all__ = ('UnmatchedNumberError', 'WrongAnswerError',
           'UnsupportedSyntaxError', 'RepeatedAnswerError',
           'GameStatusError')


class UnmatchedNumberError(Exception):
    """This error is raised when met an unmatched input set."""

    def __init__(self, user_input):
        """Initialization."""
        self.__user_input = str(sorted(user_input)).replace(',', '')

    def __repr__(self):
        """Print out."""
        return '你使用的数字%s与题目所给的不符' % (self.__user_input)

    def __str__(self):
        """Print out."""
        return self.__repr__()


class WrongAnswerError(Exception):
    """This error is raised when a user's answer is wrong."""

    def __init__(self, answer):
        """Initialization."""
        self.__answer = answer

    def __repr__(self):
        """Print out."""
        return '你的结果[%s]是错误的' % (self.__answer)

    def __str__(self):
        """Print out."""
        return self.__repr__()


class UnsupportedSyntaxError(Exception):
    """This error is raised when the parser can't recognize the syntax."""

    def __init__(self, info):
        """Initialization."""
        self.__info = info

    def __repr__(self):
        """Print out."""
        return '你的公式无法识别[%s]' % (self.__info)

    def __str__(self):
        """Print out."""
        return self.__repr__()


class RepeatedAnswerError(Exception):
    """This error is raised when an answer is repeated."""

    def __init__(self, repeated):
        """Initialization."""
        self.__repeated = repeated

    def __repr__(self):
        """Print out."""
        return '你的结果与解[%s]重复了' % (self.__repeated)

    def __str__(self):
        """Print out."""
        return self.__repr__()


class GameStatusError(Exception):
    """This error is raised when an answer is repeated."""

    def __init__(self, status):
        """Initialization."""
        self.__status = status

    def __repr__(self):
        """Print out."""
        ref = {True: 'PLAYING', False: 'NOT PLAYING'}
        return 'Required status: %s' % (ref[self.__status])

    def __str__(self):
        """Print out."""
        return self.__repr__()
