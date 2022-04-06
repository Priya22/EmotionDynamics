# Emotion Dynamics

Emotion dynamics is a framework for measuring how an individual’s emotions change over time. [Hipson and Mohammad](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256153) first introduced the framework and applied it to a dataset of movie dialogues. Their Utterance Emotion Dynamics (UED) framework quantifies emotion state in a 2-dimensional elliptical space of valence--arousal. Their R code can be found at https://github.com/whipson/edyn. 

Here, we re-formulate the emotion dynamics framework along uni-dimensional axes of valence, arousal, and dominance, and provide Python scripts that can be used to appy the analysis to any temporally-ordered text.

If you use any of the resources provided in this repository, cite the following work:

        TBD

If you the emotion dynamics framework for your dataset, also cite the following work:

    @article{hipson2021emotion,
    doi = {10.1371/journal.pone.0256153},
    author = {Hipson, Will E. AND Mohammad, Saif M.},
    journal = {PLOS ONE},
    publisher = {Public Library of Science},
    title = {Emotion dynamics in movie dialogues},
    year = {2021},
    month = {09},
    volume = {16},
    url = {https://doi.org/10.1371/journal.pone.0256153},
    pages = {1-19}
}
## What does this repository provide?

This repository consists of two main submodules:

1. Code to run the Emotion Dynamics framework. The code has been designed to work with any temporally-ordered text data, including but not limited to tweets. See the Readme within the [`code`](https://github.com/Priya22/TweetDynamics/tree/master/code) folder for further instructions.

2. The TUSC tweet dataset described in the paper [Tweet Emotion Dynamics:
Emotion Word Usage in Tweets from US and Canada]().

## Where can you use the Emotion Dynamics framework?
The framework can be used to characterize the emotional state and trajectory of a speaker via their textual utterances over a period of time. [Hipson and Mohammad](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256153) apply it to analyze characters in a corpus of movie dialogues. The `code` folder of this repository shows a sample usage on character dialogue in literary novels. Our Tweet Dyanmics work applies it to individual tweeters -- one can do so with data other social media platforms as well (Reddit, for example).

## What is Tweet Emotion Dynamics?

Tweet Emotion Dynamics, or TED, is a set of metrics that quantify the emotional characteristics of a set of tweets and tweeters. A large portion of the metrics are directly adapted from the Utterance Emotion Dynamics (UED) framework of [Hipson and Mohammad](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0256153). 

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

3. [This paper](https://arxiv.org/abs/2011.03492) details ethical considerations involved in the use of emotion lexicons in general.

## Authors
For any queries, you can contact the authors:
- [Krishnapriya Vishnubhotla](https://priya22.github.io/) (University of Toronto)
- [Saif M. Mohammad](http://saifmohammad.com/) (National Research Council Canada)

**Contact:** vkpriya@cs.toronto.edu, saif.mohammad@nrc-cnrc.gc.ca




