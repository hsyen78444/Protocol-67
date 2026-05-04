# Ethical Considerations

## User-Generated Content Risks

Internet slang data often comes from user-generated content. Such data may include offensive language, stereotypes, misinformation, personal information, or unstable meanings.

## Bias in Slang Data

Slang is shaped by communities, age groups, regions, and platforms. A dictionary or social-media corpus can overrepresent some groups and underrepresent others. The dataset should not be treated as a universal map of language.

## Offensive Language Filtering

The preprocessing script includes a simple blocklist to keep the coursework dataset safe. This is not a complete moderation system. Human review is still needed before using real public data.

## Privacy

The fallback dataset is synthetic and does not contain real user identifiers. If real datasets are added later, usernames, links, IDs, and personal information should be removed unless there is a clear ethical and legal basis for retaining them.

## Platform Terms of Service

The pipeline avoids direct Twitter/X scraping and is designed for approved exports or public datasets. Future collection should follow platform terms, API rules, and institutional guidance.

## Synthetic Fallback Limitations

Synthetic fallback rows are useful for testing pipeline mechanics, but they cannot replace real linguistic diversity. They may simplify patterns and miss sarcasm, code-switching, and community-specific meanings.

## Human Review

Human review should be used for low-confidence translations, unknown terms, sensitive content, and final training examples. This is especially important because slang meanings change quickly.
