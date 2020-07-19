"""Exception classes used in the package."""

__all__ = ('FTPtsGameError')


class FTPtsGameError(Exception):
    """The whole module's global error collection."""

    def __init__(self, err_no: int, hint='-'):
        """Initialization."""
        self.__err_no = err_no
        self.__hint = hint

    def __repr__(self):
        """Print out, used in print() function."""
        reference_code = {
            0x00: 'StatusError:RequireCertainStatus',
            0x01: 'ProblemGenerateError:FailedtoParse',
            0x02: 'ProblemGenerateError:NoSolution',
            0x03: 'ProblemGenerateError:MethodNotFound',
            0x10: 'FormatError:ExpressionTooLong',
            0x11: 'FormatError:FailedtoParse',
            0x12: 'FormatError:UnallowedOperator',
            0x13: 'FormatError:DivisionByZero',
            0x14: 'FormatError:NotAnInteger',
            0x20: 'AnswerError:WrongAnswer',
            0x21: 'AnswerError:UnmatchedNumber',
            0x22: 'AnswerError:RepeatedAnswer',
        }  # This table might extend as more error types are included

        message = '%s[%s]' % (
            reference_code[self.__err_no], str(self.__hint)
        ) if self.__err_no in reference_code else 'UnknownError:ErrnoNotFound'
        return message

    def __str__(self):
        """Print out, used in str() function."""
        return self.__repr__()

    def get_details(self):
        """Get details of the raised error's code and hint."""
        return (self.__err_no, self.__hint)
