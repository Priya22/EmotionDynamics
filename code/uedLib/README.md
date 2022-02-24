# UED Metrics
This document details the configurations, inputs and outputs of the Tweet Emotion Dynamics framework, which adapts the Utterance Emotion Dynamics frameword of [CITE] to tweets. 

## Input
The library expects the input to be formatted as a comma-separated (CSV) file, with the first line of the file indicating the names of the columns (header). Each row should contain information relating to a single tweet (or text turn).

There are three fields that need to be present in the CSV:
- The text column: contains the text of the tweet
- The speaker column: a unique identifier indicating the speaker/tweeter
- The time column: indicates the timestamp or temporal ordering of the tweet

## Configuration file
The files in the `config/` folder enumerate the parameters that can be specified. 
- **iden**: An identifier for the input file that indicates the context (ex: "City tweets", "Pride and Prejudice").
- **data_path**: Path to the input CSV file
- **disp_length_min**: Minimum number of window steps to be considered a valid displacement.
- **emoCols**: A list of the dimensions of the emotion lexicon to be considered (ex: [valence], [valence, arousal])
- **filter**: Filter out neutral terms from the emotion lexicon. If true, all terms with emotion scores between (0.33, 0.67) will be removed.
- **idCol**: The column with the speaker identifier.
- **level**: The range of distribution values to be considered as the home base. The default value of 0.68 is mean+-std_dev for a normal distribution.
- **lex_path**: Path to the lexicon. Must be a CSV with column headers, where one column called `word` must exist, along with the dimensions listed in `emoCols`.
- **min_tokens**: Minimum number of tokens by a speaker that must be present in the lexicon to be considered.
- **min_turns**: Minimum number of tweets by a speaker that must be present to be considered.
- **rollingWindow**: Size of the window
- **save_dir**: Path to the directory where outputs will be stored
- **stopword_path**: Path to the file containing list of stopwords. File must contain one word per line, no header column.
- **stopwords**: true if stopwords should be filtered.
- **textCol**: Column containing the tweet/turn text.
- **timeCol**: Column indicating the temporal ordering (timestamp).
- **textIdCol**: A unique identifier for each tweet/turn.
- **hb_type**: Home base type. This can take two values:
    - SPK100: Mean and standard deviation used to determine home base will be calculated based on the entire speaker text. 
    - SPK10: Mean and standard deviation used to determine home base will be calculated based on the first 10\% of the speaker's tweets/turns. 

## Outputs
'tweet_info', 'narrative_info', 'displacement_info', 'overall_speaker_info'
There are four main outputs that are written by the library. The outputs are written separately for each dimension `emoDim` specified in `config.emoCols`, and stored in the folder `config.save_dir/<emoDim>`. All files are written in compressed `gz` format.

- **narrative_info**: Information on emotion state at each timestep.
- **overall_speaker_info**: Summary UED metrics for each speaker.
- **tweet_info**: Information regarding tweet at each timestep.
- **displacement_info**: Information regarding each displacement (displacement length, peak distance, rise and recovery rates).
