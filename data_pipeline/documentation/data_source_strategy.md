# Data Source Strategy

## Urban Dictionary-Style Data

Urban Dictionary-style data is useful because it provides community definitions and usage examples for slang. However, it is noisy, subjective, inconsistent, and sometimes unsafe. The pipeline first attempts a local compatible API clone at `http://localhost:8080/api/search`, then uses a curated local fallback if API collection is unavailable or returns too little usable data. The pipeline treats this source as weak data that requires filtering and human review.

## Twitter/X Access

The project avoids direct Twitter/X scraping. Direct scraping can violate platform terms and the official API may require authentication, paid access, and strict compliance. The ingestion script instead accepts approved CSV, JSONL, or Parquet exports.

## Connector-Ready Design

The pipeline is built so real datasets can replace fallback data without changing downstream scripts. If future approved public datasets are available, they can be imported through the same file-based connector pattern. Hugging Face Parquet paths can also be used when the required optional dependencies are installed.

## Twitch-Style Data

Twitch-style data is useful for short-form conversational slang, gaming terms, memes, and fast-moving chat patterns. It helps the dataset capture forms of internet language that are not always present in dictionary definitions.

The default Twitter/X-style and Twitch-style rows are synthetic fallback examples for testing the pipeline. They should be replaced with approved real exports before making claims about real platform behavior. The public Hugging Face dataset `lparkourer10/twitch_chat` can be used as a Twitch source if its CC BY-SA 4.0 license terms are followed.

## Future Work

Future iterations can use approved APIs, public research datasets, and human annotation rounds. Additional metadata such as timestamp, platform, topic, or region can support diachronic analysis if collected ethically and legally.
