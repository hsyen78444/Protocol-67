# Ethical Considerations

## User-Generated Content Risks

Internet slang data often comes from user-generated content. Such data may include offensive language, stereotypes, misinformation, personal information, or unstable meanings.

## Bias in Slang Data

Slang is shaped by communities, age groups, regions, and platforms. A dictionary or social-media corpus can overrepresent some groups and underrepresent others. The dataset should not be treated as a universal map of language.

## Offensive Language Filtering

The preprocessing script includes a simple blocklist to keep the coursework dataset safe. This is not a complete moderation system. Human review is still needed before using real public data.

## Privacy

The Twitch datasource is user-generated chat text. Usernames, links, IDs, and personal information should be removed unless there is a clear ethical and legal basis for retaining them.

## Platform Terms of Service

The pipeline avoids direct live-platform scraping and uses local approved dataset files. Future collection should follow platform terms, API rules, dataset licenses, and institutional guidance.

## Dataset Limitations

A single Twitch chat dataset cannot represent all internet slang communities. It may overrepresent gaming and livestream culture, and it may miss sarcasm, code-switching, and community-specific meanings from other platforms.

## Human Review

Human review should be used for low-confidence translations, unknown terms, sensitive content, and final training examples. This is especially important because slang meanings change quickly.
