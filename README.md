# Protocol 67

## Project Title

**Protocol 67: An Agent-Driven Brainrot-to-English Translation and Sentiment Analysis System**

---

## Background

Internet vernacular evolves at an extremely fast pace, causing rapid semantic drift in online communication. New slang, memes, abbreviations, and non-standard expressions often emerge from platforms such as Twitter/X, Twitch, TikTok, Reddit, and Urban Dictionary.

These expressions can be difficult for non-native speakers, older users, educators, researchers, and even NLP systems to interpret accurately. For example, phrases such as “bro is cooked fr”, “that fit ate”, or “no cap” may carry meanings that are highly contextual and culturally specific.

**Protocol 67** aims to address this challenge by translating highly contextual internet slang, commonly known as “brainrot language”, into formal English while also analyzing the sentiment behind the original input.

---

## Project Overview

**Protocol 67** is a Natural Language Processing project focused on low-resource machine translation for internet slang and informal online language.

The system uses an autonomous translation agent to map non-standard internet expressions into formal English structures. In addition to translation, the agent also performs tool-assisted sentiment analysis to determine the emotional tone or polarity of the input.

The system accepts slang-based user input and returns a structured JSON response containing:

- Formal English translation
- Sentiment polarity
- Confidence score
- Detected slang terms
- Unknown terminology, if any

---

## Objectives

The main objectives of this project are:

1. To develop an agent-driven NLP system capable of translating internet slang and brainrot language into formal English.
2. To fine-tune a causal language model using Low-Rank Adaptation (LoRA) for slang-to-English translation.
3. To integrate tool-assisted sentiment analysis for identifying the polarity of slang-based input.
4. To build a RESTful API using FastAPI that returns translation, sentiment, and confidence scores in JSON format.
5. To support an active learning loop where unknown slang terms can be corrected by users and stored for future retraining.

---

## Main Features

### 1. Brainrot-to-English Translation

The system translates informal internet expressions into formal English.

Example:

```json
{
  "input": "bro is cooked fr",
  "formal_translation": "He is in serious trouble, for real."
}
