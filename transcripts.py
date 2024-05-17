"""
Transcript Class
02/24/2023
"""
from wordie import Wordie
from collections import defaultdict, Counter
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords as sw


class ZoomTranscript(Wordie):
    """
    Child class of wordie library. Specific to zoom transcripts
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def transcript_reader(filename, speaker, delimiter='user avatar'):
        """
        Zoom transcript specific reader for gathering a specific speaker's words from the meeting
        :param filename: str; file containing the transcript
        :param speaker: str; speaker to search for
        :param delimiter: str; what separates speakers
        :return: cleaned transcript
        """
        transcript = open(filename).read().lower()

        # split into sections by speaker
        sections = transcript.split(delimiter)

        cleaned = ''
        for section in sections:
            if speaker in section:
                split = section.split('\n')

                # remove timestamp
                del split[:2]

                # add only text from section to cleaned
                cleaned += ' '.join(map(str, split))

        return cleaned

    def _default_parser(self, transcript, stopfile=None, **kwargs):
        """
        Takes in user inputted file, reads and cleans text into the result dictionary
        :param transcript: str name of the transcript being read
        :param speaker: speaker being searched for
        :param stopfile: file to remove stop words by
        :return: results dict
        """
        text = self.transcript_reader(transcript, **kwargs)

        # Creating a list of sentences
        sentences = text.split('.')

        # removes all punctuation except apostrophes (for clarity with contractions)
        punc = '''!()-[]{};:"\,<>./?@#$%^&*_~'''
        text = text.translate(str.maketrans('', '', punc))

        # list of words
        words = text.split()

        # delete stopwords
        words = self.del_stopwords(words, self.load_stop_words(stopfile))

        results = {
            'plain_text': text,
            'wordcount': Counter(words),
            'numwords': len(words),
            'sentiment': SentimentIntensityAnalyzer().polarity_scores(text),
            'sentence_length': self.sen_len(sentences)
        }
        return results

    def load_text(self, transcript, label=None, parser=None, **kwargs):
        """ inherited load_text method """
        super().load_text(transcript, label, parser, **kwargs)

