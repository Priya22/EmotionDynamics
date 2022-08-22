# Utterance Emotion Dynamics Metrics
This document details the configurations, inputs and outputs needed to run the utterance emotion dynamics scripts on your a dataset of speaker text utterances. 
## What do the metrics tell us?
Utterance Emotion Dynamics metrics quantify how emotions associated with an individual speaker's utterances change over time. Section 5 of our paper describes briefly the original UED framework, and how we adapted it to analyze tweets (Tweet Emotion Dynamics, or TED).

## Input
The library expects the input to be formatted as a comma-separated (CSV) file, with the first line of the file indicating the names of the columns (header). Each row should contain information relating to a single tweet (or text turn). 

There are three fields that need to be present in the CSV:
- The text column: contains the text of the tweet
- The speaker column: a unique identifier indicating the speaker/tweeter
- The time column: indicates the timestamp or temporal ordering of the tweet

**Note**: You can specify the input path to be a *folder*, in which case all files in that folder will be concantenated into a single CSV file by the pre-processing code. If you use this option, please ensure that all the contained files in the folder are in the CSV format specified above, with the same column names.

## Configuration file
Various hyperparamters need be set before running the utterance emotion dynamics code. These should be specified in a YAML-formatted file. The files in the `sample_data/` folder, `config_novel.yaml` and `config_speaker.yaml` demonstrate two sample configurations.

**List of paramters**:

- **iden**: An identifier for the input file that indicates the context (ex: "Boston tweets", "Pride and Prejudice").
- **data_path**: Path to the input CSV file of utterances.
- **disp_length_min**: Minimum number of window steps to be considered a valid displacement.
- **emoCols**: A list of the dimensions of the emotion lexicon to be considered (ex: [valence], [valence, arousal]).
- **filter**: Filter out neutral terms from the emotion lexicon. If true, all terms with emotion scores between (0.33, 0.67) will be removed.
- **idCol**: The column(s) with the speaker identifier. This can either be a single column name, or a list of columns that uniquely identify a speaker (ex: `userID`, `[city, month]`).
- **level**: The range of distribution values to be considered as the home base. The default value of 0.68 is `mean`+/-`std_dev` for a normal distribution.
- **lex_path**: Path to the lexicon. Must be a CSV with column headers, where one column called `word` must exist, along with the dimensions listed in `emoCols`. 

    The file `lexicons/NRC-VAD-Lexicon.csv` demonstrates the required format -- **please download your required lexicons from the original source and read the associated terms of use**. The homepage for this particular lexicon is at http://saifmohammad.com/WebPages/nrc-vad.html.
- **min_tokens**: Minimum number of tokens by a speaker that must be present in the lexicon to be considered. Set to false if you do not want this filter.
- **min_turns**: Minimum number of utterances by a speaker that must be present to be considered. Set to false if you do not want this filter.
- **rollingWindow**: Size of the rolling window, in number of tokens
- **save_dir**: Path to the directory where outputs will be stored
- **stopword_path**: Path to the file containing list of stopwords. File must contain one word per line, no header column.
- **stopwords**: true if stopwords should be filtered.
- **textCol**: The name of the column in your utterances file (the `data_path` parameter) containing the text of the utterance.
- **timeCol**: The name of the column in your utterances file indicating the temporal ordering (timestamp) of the utterances.
- **textIdCol**: A unique identifier for each row of the utterances file. This parameter is optional. If not present, a default column indexing the utterances with a integer counter will be created by the preprocessing code.
- **hb_type**: Home base type. This can take two values:
    - SPK100: Mean and standard deviation used to determine home base will be calculated based on all the speaker's utterances ((utterances without any terms from the emotion lexicon will not be considered). 
    - SPK10: Mean and standard deviation used to determine home base will be calculated based on the first 10\% of the speaker's utterances (utterances without any terms from the emotion lexicon will not be considered). 
- **compress**: Set to `true` if the outputs should be written in compressed `gzip` format, else false.

## How to Run
Once you have the utterances, emotion lexicon, and the configuration files ready, run the following command:

    python lib/ued.py --config \<path-to-config-file\> --pre_process true --post_process true

It is recommended to set both the pre_process and post_process flags to true, unless you are familiar with the inner workings of the code. It formats the input file and outputs in a readable format.

## Outputs

A detailed list of the columns in each output file, with a brief description of what each metric is, is provided in this [codebook](https://docs.google.com/spreadsheets/d/1iyFB_FmXjFLB73wYJEFbhb3hXRmWivoKZzEOZMKo1rk/edit?usp=sharing). 

There are four main outputs that are written by the library. The outputs are written separately for each dimension `emoDim` specified in `config.emoCols`, and stored in the folder `config.save_dir/<emoDim>`. All files are written in the CSV format, and compressed in the `gzip` format if config.compress is `true`.

- **narrative_info**: Information on emotion state at each timestep.
- **overall_speaker_info**: Summary UED metrics for each speaker.
- **utterance_info**: Information regarding utterances.
- **displacement_info**: Information regarding each displacement (displacement length, peak distance, rise and recovery rates).

## Sample Data
In the `sample_data` folder, we have included a file with sample data from a corpus of character dialogue in novels. Each row contains dialogue from a character, from one of 3 different novels. In the same folder, there are two config files:
1. `config_speaker.yaml` provides parameters to compute UED metrics for each individual character as a speaker. Note that the data contains two speakers named "Elizabeth", one from the novel Pride and Prejudice, and another from the novel Persuasion. We therefore specify two columns as uniquely identifying the speaker in the config: `idCol` is set to `[speaker, novel]`. 
2. `config_novel.yaml` provides parameters to compute UED metrics where each novel is considered a "speaker". 

Run the following commands from the `uedLib` folder:

    python3.7 lib/ued.py --config sample_data/config_speaker.yaml

    python3.7 lib/ued.py --config sample_data/config_novel.yaml

The outputs will be written to the `sample_data/speaker_outputs` and `sample_data/novel_outputs` folders respectively.
