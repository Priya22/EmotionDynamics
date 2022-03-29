Data and Code for the paper XXXXX.

## What does this repository provide?

This repository is intended as a companion to the paper XXX, and consists of two main submodules:
1. The TUSC tweet dataset described in the paper 
2. Code to run the Tweet Emotion Dynamics (TED) analyses described in the paper. The code has been designed to work with any temporally-ordered text data, including but not limited to tweets. See the Readme within the `code` folder for further instructions.
## What is Tweet Emotion Dynamics?

Tweet Emotion Dynamics, or TED, is a set of metrics that quantify the emotional characteristics of a set of tweets and tweeters. A large portion of the metrics are directly adapted from the Utterance Emotion Dynamics (UED) framework of {CITE}. 

These metrics can be broadly described by the following three questions:
1. On average, what is the emotion score of the tweets for a particular tweeter? (Section 4.1)
2. On average, how many tweets of a particular tweeter contain emotion-indicating words? (Section 4.2)
3. How can we quantify how the average emotionality of tweets varies over time, for a particular tweeter? (Utterance Emotion Dynamics; Section 5)

## Folder Structure

- `data/`: Tweet IDs for `tusc-city` and `tusc-country` subsets. Each folder is split by city/country, and further by month. Each file contains the ID of the tweet. 
- `code/`: Code for running the emotion dynamics and emotion word usage analyses.
    - `clean_data.py`: functions to tokenize tweets and identify URLs.
    - `avgEmoValues.py`: functions to obtain number of tokens per tweet, number of lexicon tokens per tweet, and the average emotion value of words in that tweet, given an emotion lexicon.
    - `uedLib`/: code to run emotion dynamics on tweet data. 
        - `run_ued.py`: sample call to the main UED library.
        - `lib/ued.py`: main UED module that takes a config file as input and outputs emotion dynamic metrics.
        - `config/`: sample config files for running UED on (a) a single file; (b) a folder with multiple CSV files.

- `lexicons/`: Files with words and associated values for different emotion dimensions. 

    **Note**: Please see terms of use for these lexicons from their **original source** at http://saifmohammad.com/WebPages/lexicons.html. If you wish to run the emotion dynamics code with any of these lexicons, please download from [the original source](http://saifmohammad.com/WebPages/lexicons.html]). The complete list of lexicons and their sources is described in the next section.

    This folder contains three main categories of lexicons for each of the valence-arousal-dominance dimensions:

    - `<dim>.csv`: The complete lexicon
    - `<dim>_polar.csv`: Does not contain words with a score between (0.33, 0.67).
    - `<dim>_low.csv`: Terms with scores <=0.33
    - `<dim>_high.csv`: Terms with scores >=0.67

    All lexicon files have two columns: `word` and `val`.

## Lexicons

The following lexicons are provided for ease of running the code in the `lexicons/` folder, but must be downloaded directly from the associated sources:
1. The `valence`, `arousal`, and `dominance` lexicons

    These are sourced from the [NRC-VAD Lexicon](http://saifmohammad.com/WebPages/nrc-vad.html). See terms of use at the bottom of the linked page. Cite the following work if you use these lexicons:

        @inproceedings{vad-acl2018,
        title={Obtaining Reliable Human Ratings of Valence, Arousal, and Dominance for 20,000 English Words},
        author={Mohammad, Saif M.},
        booktitle={Proceedings of The Annual Conference of the Association for Computational Linguistics (ACL)},
        year={2018},
        address={Melbourne, Australia}
        }

2. Lexicons for the eight basic emotions (`anger`, `fear`, `anticipation`, `trust`, `surprise`, `sadness`, `joy`, `disgust`) and two sentiments (`negative` and `positive`)

    These are sourced from the [NRC Word-Emotion Association Lexicon, or EmoLex](http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm). Download the lexicons by going to the linked page and selecting the appropriate usage license. Cite the following works if you use these lexicons:

        @article{Mohammad13,
        Author = {Mohammad, Saif M. and Turney, Peter D.},
        Journal = {Computational Intelligence},
        Number = {3},
        Pages = {436--465},
        Title = {Crowdsourcing a Word-Emotion Association Lexicon},
        Volume = {29},
        Year = {2013}
        }

        @inproceedings{mohammad-turney-2010-emotions,
        title = "Emotions Evoked by Common Words and Phrases: Using {M}echanical {T}urk to Create an Emotion Lexicon",
        author = "Mohammad, Saif  and
        Turney, Peter",
        booktitle = "Proceedings of the {NAACL} {HLT} 2010 Workshop on Computational Approaches to Analysis and Generation of Emotion in Text",
        month = jun,
        year = "2010",
        address = "Los Angeles, CA",
        publisher = "Association for Computational Linguistics",
        url = "https://aclanthology.org/W10-0204",
        pages = "26--34",
        }

## Ethical Considerations

Any analysis involving the use of emotion and sentiment lexicons must be preceded by a consideration of the ethical ramifications of doing the same, and the intended as well as potential uses of the associated results and tools. 
1. This [Ethics Sheet for Automatic Emotion Recognition and Sentiment Analysis](https://arxiv.org/abs/2109.08256) presents fifty ethical considerations relevant to the use of Automatic Emotion Recognition (AER) systems.

2. This [Ethics Sheets for AI Tasks](https://arxiv.org/abs/2107.01183) presents a more general framework, and ethics sheet, for thinking about the ethical consideratios involved in any AI task.





