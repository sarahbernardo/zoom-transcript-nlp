"""
Core framework for comparative text analysis
Kate Lanman, Sarah Bernardo, Kalden Harp, Lon Pierson
Created: Tue Feb 21

TO DO (Feb 26 List)
- (in default parser): fix for case when stopfile is not none (args/kwargs? or just add param?)
- comment on transcripts
- exceptions

After Code
- 2-3 page report
- Poster
"""

from collections import defaultdict, Counter
import plotly.graph_objects as go
import plotly.express as px
import math
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords as sw
from sankey import make_sankey as make
import pandas as pd
from plotly.subplots import make_subplots
from exception import WordieError


class Wordie:

    def __init__(self):
        self.data = defaultdict(dict)

    def _default_parser(self, filename, stopfile=None):
        """
        Takes in user inputted file, reads and cleans text into the result dictionary
        :param filename: str name of the file being read
        :param reader: alternative file format reader
        :param stopfile: file to remove stop words by
        :return: results dict
        """
        # Exception handling for the file
        exception_handle = WordieError()
        exception_handle.verify_text(filename=filename)

        # read text; lower, remove punctuation
        text = open(filename).read().lower()

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

    @staticmethod
    def del_stopwords(text, sw_lst):
        """
        Removes stopwords from text
        :param text: the text we are analyzed in list format
        :param sw_lst: list of stopwords
        :return: list of words without
        """

        valid = []
        for word in text:

            # ignore if word (or first part of contraction) is a stopword
            if word.split('\'')[0] not in sw_lst:
                valid.append(word)

        return valid

    def _save_results(self, label, results):
        """ Integrate parsing results into internal state
        label: unique label for a text file that we parsed
        results: the data extracted from the file as a dictionary attribute-->raw data
        """
        for k, v in results.items():
            self.data[k][label] = v

    def load_text(self, filename, label=None, parser=None, *args, **kwargs):
        """
        Register a document with the framework
        :param filename: name of file (str)
        :param label: label for file if user wants label to be anything other than file name (str)
        :param parser: user-specified parser if user does not want to use default
        :param args: arguments
        :param kwargs: keyword arguments
        :return:
        """

        if parser is None:  # do default parsing of standard .txt file
            results = self._default_parser(filename, *args, **kwargs)
        else:
            results = parser(filename)

        if label is None:
            label = filename

        # Save / integrate the data we extracted from the file
        # into the internal state of the framework
        self._save_results(label, results)

    @staticmethod
    def load_stop_words(stopfile=None):
        """
        Load stop words to filter out of each file
        :param: stopfile: optional file with stop words to use over default
        :return: list of stop words to remove
        """
        if stopfile:
            return open(stopfile).read()

        # default list
        return sw.words('english')

    @staticmethod
    def filter_wordcount(dct, keys):
        """
        Filters a dictionary of dictionaries for given keys.
        :param dct: dictionary to filter --> {label: {key: count}}
        :param keys: keys to search for
        :return: dictionary containing only given keys {label: {key: count}}
        """
        # create new wordcount dict --> {label: {counter}}
        filtered = defaultdict(dict)

        # for each label, make new counter with only word_list words
        for label in dct:
            for key in keys:
                filtered[label][key] = dct[label][key]

        return filtered

    @staticmethod
    def sen_len(sentences):
        """
        Calculate length of each sentence from a text
        :param sentences: list of sentences from each text
        :return: list of the lengths of every sentence
        """
        # creates empty list
        sen_lens = []

        # runs through each sentence
        for i in sentences:
            # add the length of the sentence to the sen_lens list
            sen_lens.append(len(i.split(' ')))

        return sen_lens

    def wordcount_sankey(self, word_list=None, k=5):
        """
        Map each text to words using a Sankey diagram, where the thickness of the line
        is the number of times that word occurs in the text. Users can specify a particular
        set of words, or the words can be the union of the k most common words across each file
        (excluding stop words)
        :param word_list: array; user-specified set of words to map to (default None)
        :param k: int; (if not word_list) number of words to use
        :return: none. plots a sankey
        """
        wordcounts = self.data['wordcount']

        # if not word_list, aggregate to find top over all counters
        if word_list is None:
            merged = Counter()
            for label in wordcounts:
                # add each counter
                merged += wordcounts[label]

            # sort dictionary by values and get filter for top k
            word_list = [x[0] for x in sorted(merged.items(), key=lambda x: x[1], reverse=True)[:k]]

        # get filtered dict for given words
        counts = self.filter_wordcount(wordcounts, word_list)

        # creating pd dataframe with the counts dict
        # creating source column
        src = list()
        for label in counts.keys():
            src += [label] * len(counts[label])

        # creating target column
        targ = word_list * len(counts)

        # creating values column
        vals = list()
        for label in counts:
            vals += counts[label].values()

        # combining source, target and vals into dict and creating dataframe with it
        df_dict = {'src': src, 'targ': targ, 'vals': vals}
        df = pd.DataFrame.from_dict(df_dict)

        # Creating the sankey figure using the newly created df
        fig = make(df, ['src', 'targ'], vals='vals', title='Word Appearances by Text', threshold=0, prep=False)

        fig.show()

    @staticmethod
    def get_score(score_dict):
        """
        Using the positive and negative values of the sentiment score analyzer to create a overall score.
        :param score_dict: Dict with compound, positive, negative and neutral sentiment scores.
        :return: float value that is the combined sentiment score.
        """
        return score_dict['pos'] - score_dict['neg']

    def sent_over_time(self, n=10):
        """
        Create horizontal bar chart based on the sentiments
        :param n: amount of segments you want in each bar
        :return: nothing. plots a graphl
        """
        # creating a figure
        fig = go.Figure()

        # creating list of y labels for the horizontal bar
        y_labels = self.data['sentiment'].keys()

        # iterating through labels and getting the text file and step distance for each
        for label in y_labels:
            text = self.data['plain_text'][label].split()
            step = int(self.data['numwords'][label] / n)

            vals = []

            # Iterating through each text file and slicing based on step size.
            for i in range(1, n + 1):
                # Checking that
                if i < n:
                    val = self.get_score(SentimentIntensityAnalyzer().polarity_scores(
                        ' '.join(map(str, text[step * (i - 1):i * step]))
                    ))

                # if there is only one step before the end, it slices using the  rest of the list to not exclude words.
                else:
                    val = self.get_score(SentimentIntensityAnalyzer().polarity_scores(
                        ' '.join(map(str, text[step * (i - 1):]))
                    ))

                # adding the sentiment score to the list for that row
                vals.append(val)

            # creating horizontal bar for the current label, using the vals list just created
            fig.add_trace(go.Bar(x=[100 / n] * n, y=[label] * n, orientation='h',
                                 text=[str(round(val, 2)) for val in vals],
                                 marker=dict(
                                     color=vals,
                                     line=dict(color='rgb(248, 248, 249)', width=1),
                                     colorscale='fall', cmid=0, cmax=1, cmin=-1,
                                     colorbar=dict(
                                         tick0=-1,
                                         dtick=1,
                                         title="Sentiment Score"
                                     ),
                                     reversescale=True
                                 )
                                 ))

        # updating the color scale, titles, bg etc.
        fig.update_layout(
            barmode='stack',
            plot_bgcolor='darkgrey',
            title='Sentiment Scores Over Course of Text',
            xaxis_title='Position in Text (percent through)',
            yaxis_title='Text',
            showlegend=False
        )

        fig.show()

    def pie_chart(self, slices=20, file_num=0):
        """
        Creates a pie chart showing the distribution of the most common
        sentence lengths for each text
        :param slices: Number of slices on the pie chart
        :param file_num: file user want's to create pie chart from
        :return: A pie chart
        """
        # make title for the graph
        title_str = f"Distribution of {slices} most common Sentence Lengths"

        # read in the data from self
        testing = self.data
        x = list(testing['sentence_length'].values())

        # find values based on the file number given in parameter
        vals = x[file_num]

        # create dictionary for sentence lengths
        dct = {}

        # fill up dictionary with values
        for i in vals:
            if i not in dct:
                dct[i] = 1
            if i in dct:
                dct[i] += 1

        # turn dictionary into data frame
        sendf = pd.DataFrame(dct.items(), columns=["num_words", "num_sen"])

        # sort the data frame and cut off the values that aren't in the top
        # however many values that were designated by user
        sendf.sort_values('num_sen')
        top_df = sendf[0:slices].copy()

        # make figure
        fig = px.pie(top_df, values='num_sen', names='num_words', title=title_str)

        # show figure
        fig.show()

    def subplot_bar(self, max_words=75):
        """
        Creates a set of subplots for the set of texts, showing the frequency of sentence lengths
        across each text
        :param max_words: optional parameter for max sentence length
        :return:a plotly subplot
        """

        # initialize empty list to store plot titles in
        plot_titles = []

        # iterate through labels then add to plot_titles list
        for each in self.data['sentence_length']:
            plot_titles.append(each)

        # create list from sentence length dict
        testing = self.data
        x = list(testing['sentence_length'].values())

        # create subplot layout
        num_cols = math.ceil(len(x) / 2)
        fig = make_subplots(rows=2, cols=num_cols,
                            subplot_titles=(plot_titles))

        # create trace for each text
        for i in range(len(self.data['sentence_length'])):
            # set current values equal to the specific text we're looking at in this loop
            vals = x[i]

            # create dictionary for values
            dct = {}

            # fill up dictionary with values
            for j in vals:
                if j not in dct:
                    dct[j] = 1
                if j in dct:
                    dct[j] += 1
            sendf = pd.DataFrame(dct.items(), columns=["num_words", "num_sen"])
            top_df = sendf[sendf["num_words"] < max_words].copy()

            # split dictionary into lists of number of words per sentence and sentence frequency
            x_vals = list(top_df["num_words"])
            y_vals = list(top_df["num_sen"])

            # calculate row and column position within subplot
            p = i + 1
            r = 1
            if p > num_cols:
                p -= num_cols
                if r == 1:
                    r = 2

            # create trace for current text
            fig.add_trace(
                go.Bar(x=x_vals, y=y_vals),
                row=r, col=p
            )

        # add title, x-axis label, and y-axis label
        fig.update_layout(title_text="Sentence Length by Text",
                          showlegend=False)
        fig.update_xaxes(title_text="Number of Words in a Sentence")
        fig.update_yaxes(title_text="Sentence Frequency")

        # show plot
        fig.show()
