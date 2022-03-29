## Description

This folder contains Python code to compute, for a CSV of tweets, the following emotion word usage metrics:

1. Emotion score for each tweet, computed as a mean of the emotion scores of the constituent tokens. 
2. Ratio of number of tokens present in the lexicon. 
3. Utterance Emotion Dynamics metrics applied to tweets (Tweet Emotion Dynamics)

## Code Organization

1. `avgEmoValues.py`: This computes metrics 1 and 2 from above for a specified emotion dimension. There are four command line arguments that need to be passed:
    - **dataPath**: Path to input CSV containing tweets. The first row must be the header, and must contain a column called `text` that contains the text of the text/document.
    -  **lexPath**: Path to the lexicon CSV, with first line being the header. The CSV should contain a column called `word` and a column called `val` with the corresponding emotion score for that word. 
    - **lexName**: The name for the lexicon (the emotion dimension)
    - **savePath**: Path to the folder where the output CSV will be stored

    The output is a CSV with the following columns for each tweet:
    - `numTokens`: number of tokens in the tweet.
    - `numLexTokens`: number of tokens in the tweet that are present in the lexicon
    - `lexRatio`: `numLexTokens`/`numTokens`. This is metric 2 listed above.
    - `avgLexVal`: emotion score of the tweet. This is metric 1 listed above.

These metrics can then be aggregated at the desired level to obtain emotion word usage scores for a particular tweeter, city, country, year, etc.

2. `uedLib`: This folder contains code associated with the TED metrics. Please see the README file within this folder for a complete description.



