# Output Format Instructions

Prompts for controlling the format and structure of AI responses.

## JSON Output Only

```
Provide the response in JSON format only.

Requirements:
- Valid JSON syntax
- No explanatory text before or after
- No markdown code blocks
- No comments
- Just the raw JSON output

[DESCRIBE WHAT DATA YOU NEED]
```

## Table Format

```
Provide the response as a markdown table:
- Use proper table syntax
- Include headers
- Align columns appropriately
- No additional text

[DESCRIBE WHAT DATA TO TABULATE]
```

## Bullet Points Only

```
Response format: Bullet points only
- One point per line
- No paragraphs
- No numbering
- No explanations
- Concise bullets

[YOUR QUESTION]
```

## Numbered List

```
Provide response as a numbered list:
1. Step-by-step format
2. Sequential order
3. No additional commentary
4. Action items only

[YOUR QUESTION]
```

## Code Block Only

```
Response format: Single code block
- No explanations
- No inline comments
- No surrounding text
- Language: [SPECIFY LANGUAGE]

[DESCRIBE WHAT CODE YOU NEED]
```

## Single Line Answer

```
One line answer only. No elaboration.

[YOUR QUESTION]
```

## YAML Format

```
Provide the configuration in YAML format:
- Valid YAML syntax
- Properly indented
- No comments
- No explanatory text

[DESCRIBE CONFIGURATION NEEDED]
```

## CSV Format

```
Provide data in CSV format:
- Include headers
- Comma-separated values
- No additional formatting
- Ready for import

[DESCRIBE DATA NEEDED]
```

## Command Sequence

```
Provide as a sequence of shell commands:
- One command per line
- No comments
- No explanations
- Executable as-is

[DESCRIBE TASK]
```

## Key-Value Pairs

```
Provide as key-value pairs:
KEY: value
KEY: value

No additional formatting or explanation.

[YOUR QUESTION]
```

## Checklist Format

```
Provide as a checklist:
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3

No descriptions, just the checklist items.

[DESCRIBE WHAT CHECKLIST YOU NEED]
```

## Diff/Patch Format

```
Show changes in diff format:
- Use standard diff syntax
- Show only what changed
- No explanations

[DESCRIBE CHANGES NEEDED]
```

## Tree Structure

```
Provide as a tree structure:
```
parent/
├── child1
├── child2
│   └── subchild
└── child3
```

No additional text.

[DESCRIBE WHAT TO SHOW]
```

## URL List Only

```
Provide URLs only:
- One URL per line
- No descriptions
- No markdown links
- Just the raw URLs

[DESCRIBE WHAT URLS YOU NEED]
```

## SQL Format

```
Provide as SQL statements:
- Valid SQL syntax
- No comments
- Executable as-is
- Database: [SPECIFY IF NEEDED]

[DESCRIBE QUERY/OPERATION]
```

## HTML Only

```
Provide as HTML:
- Valid HTML5
- No explanations
- No CSS or JavaScript (unless requested)
- Semantic markup

[DESCRIBE WHAT HTML YOU NEED]
```

## Regex Pattern Only

```
Provide the regex pattern only:
- No delimiters unless necessary
- No flags explanation
- No test examples
- Just the pattern

[DESCRIBE WHAT TO MATCH]
```

## Environment Variables

```
Provide as environment variable declarations:
export VAR_NAME=value
export VAR_NAME=value

No additional text.

[DESCRIBE CONFIGURATION]
```

## Function Signature Only

```
Provide only the function signature(s):
- No implementation
- No comments
- Type hints included
- Language: [SPECIFY]

[DESCRIBE FUNCTIONS NEEDED]
```

## Inline Response

```
Provide the entire response on a single line:
- No line breaks
- No formatting
- Continuous text
- Easy to copy-paste

[YOUR QUESTION]
```
