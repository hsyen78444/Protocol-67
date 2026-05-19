# Data Source Strategy

## Urban Dictionary-Style Data

Urban Dictionary-style data is useful because it provides community definitions and usage examples for slang. However, it is noisy, subjective, inconsistent, and sometimes unsafe. The pipeline first attempts a local compatible API clone at `http://localhost:8080/api/search`, then uses a curated local fallback if API collection is unavailable or returns too little usable data. The pipeline treats this source as weak data that requires filtering and human review.

## File-Based Design

The pipeline uses local files instead of scraping live platforms or downloading remote datasets at runtime. This makes runs reproducible and avoids committing large source datasets into Git.

## Twitch-Style Data

Twitch-style data is useful for short-form conversational slang, gaming terms, memes, and fast-moving chat patterns. It helps the dataset capture forms of internet language that are not always present in dictionary definitions.

The current Twitch datasource is a manually downloaded local Parquet file, `train-00000-of-00001.parquet`. The importer reads the `Message` column and limits imported rows by default so development runs stay manageable. The source dataset license and attribution requirements should be followed when using it in coursework or publication.

## Future Work

Future iterations can use approved APIs, public research datasets, and human annotation rounds. Additional metadata such as timestamp, platform, topic, or region can support diachronic analysis if collected ethically and legally.
