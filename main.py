from transcripts import ZoomTranscript


def main():
    ds3500 = ZoomTranscript()

    # read in text files
    ds3500.load_text('lecturetranscripts/02-14-23.txt', label='DS3500 Feb 14',
                     speaker='john rachlin')
    ds3500.load_text('lecturetranscripts/02-17-23.txt', label='DS3500 Feb 17',
                     speaker='john rachlin')
    ds3500.load_text('lecturetranscripts/02-21-23.txt', label='DS3500 Feb 21',
                     speaker='john rachlin')
    ds3500.load_text('lecturetranscripts/02-24-23.txt', label='DS3500 Feb 24',
                     speaker='john rachlin'),
    ds3500.load_text('lecturetranscripts/02-03-23.txt', label='DS3500 Feb 03',
                     speaker='john rachlin')

    # create visualizations
    ds3500.wordcount_sankey(k=15)
    ds3500.sent_over_time(n=15)
    ds3500.pie_chart(slices=20)
    ds3500.subplot_bar()


if __name__ == "__main__":
    main()
