"""
Exception Class
"""


class WordieError(Exception):
    def __init__(self):
        super().__init__("Error parsing file")

    def verify_text(self, filename):
        """
        exception testing for the inputted read files
        :param filename:
        :return:
        """
        try:
            assert (filename[-4:] == '.txt'), 'Need a txt file to run the parser'

            text = open(filename).read().lower()
            assert text != '', 'File is empty!'

        finally:
            pass
