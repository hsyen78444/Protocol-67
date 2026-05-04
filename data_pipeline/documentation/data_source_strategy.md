# Data Source Strategy

## Urban Dictionary-Style Data

Urban Dictionary-style data is useful because it provides community definitions and usage examples for slang. However, it is noisy, subjective, inconsistent, and sometimes unsafe. The pipeline treats it as a weak source that requires filtering and human review.

## Twitter/X Access

The project avoids direct Twitter/X scraping. Direct scraping can violate platform terms and the official API may require authentication, paid access, and strict compliance. The ingestion script instead accepts approved local CSV or JSONL exports.

## Connector-Ready Design

The pipeline is built so real datasets can replace fallback data without changing downstream scripts. If future approved public datasets are available, they can be imported through the same file-based connector pattern.

## Twitch-Style Data

Twitch-style data is useful for short-form conversational slang, gaming terms, memes, and fast-moving chat patterns. It helps the dataset capture forms of internet language that are not always present in dictionary definitions.

## Future Work

Future iterations can use approved APIs, public research datasets, and human annotation rounds. Additional metadata such as timestamp, platform, topic, or region can support diachronic analysis if collected ethically and legally.
