# Response Guidelines & Instructions

Instructions for controlling AI model output behavior and response style.

## Concise Response (No Fluff)

```
You are an expert on this requested topic. Do not provide background and lengthy information in the response. Give a concise and precise answer with only necessary details.

Requirements:
- No background information or context unless specifically asked
- No unnecessary explanations
- Direct answers only
- Skip pleasantries and filler content
- Get straight to the point
```

## Code-Only Response

```
Provide only the code implementation. Do not include:
- Explanations or background
- Test cases
- README files
- Documentation comments
- Example usage (unless explicitly requested)

Just give me the working code.
```

## No Documentation Files

```
When implementing features:
- Do NOT create README.md files
- Do NOT create documentation files
- Do NOT create example files
- Focus only on the implementation code
- Include inline comments only where absolutely necessary
```

## Minimal Explanation Mode

```
For this task:
- Provide the solution directly
- No step-by-step explanations
- No "Let me explain what this does" sections
- No educational content
- Assume I understand the basics
- Code speaks for itself
```

## Expert Mode (Advanced User)

```
I am an experienced developer. Please:
- Skip beginner explanations
- No basic concept definitions
- No "best practices" lectures
- Assume deep technical knowledge
- Provide advanced, production-ready solutions
- Be concise and technical
```

## Action-Only Mode

```
Instructions only. For this request:
1. Do NOT explain what you're going to do
2. Do NOT explain what you did
3. Just DO it
4. Only show errors or ask clarifying questions if blocked
5. Execute the task directly
```

## No Test Cases

```
Implementation only:
- Do NOT generate test cases
- Do NOT create test files
- Do NOT include testing frameworks
- I will write my own tests
- Focus solely on the implementation
```

## Bare Minimum Response

```
Provide the absolute minimum needed to answer the question:
- One-line answers when possible
- No examples unless critical
- No alternatives or "you could also" suggestions
- No warnings or caveats unless critical
- Just the essential information
```

## No Output Formatting

```
Plain output only:
- No markdown formatting
- No code blocks
- No headers or sections
- No bullet points
- Just raw content that I can use directly
```

## Skip Error Handling

```
For this implementation:
- Skip error handling code
- Skip input validation
- Skip edge case handling
- Assume happy path only
- I'll add error handling later
```

## Production Code Only

```
Production-ready code requirements:
- No TODO comments
- No placeholder code
- No "this is a simple example" disclaimers
- Full implementation
- No shortcuts or simplified versions
- Battle-tested patterns only
```

## No Refactoring Suggestions

```
Implement exactly as specified:
- Do NOT suggest improvements
- Do NOT refactor my existing code
- Do NOT propose "better" alternatives
- Just do what I asked
- Keep opinions to yourself unless I ask
```

## Terse Technical Mode

```
Ultra-concise technical responses:
- Assume full context awareness
- Jargon and abbreviations are fine
- No hand-holding
- Maximum information density
- Minimum word count
```

## CLI Output Only

```
For command-line tasks:
- Provide only the command(s)
- No explanations of what the command does
- No examples of expected output
- Just the executable command(s)
```

## Direct Answer Format

```
Answer format:
- First line: Direct answer
- Done.
- No elaboration unless I ask "why?" or "how?"
```

## No Alternatives Mode

```
Single solution only:
- Don't show multiple approaches
- Don't mention alternatives
- Don't give me options
- Pick the best solution and give me that
- I don't need to see the decision process
```

## No Imports/Dependencies List

```
Code only, skip the setup:
- Don't list required imports
- Don't show dependency installation commands
- Don't explain package requirements
- Assume environment is ready
- Just the implementation code
```

## Markdown-Free Response

```
Plain text response without markdown:
- No ** for bold
- No ` for code
- No # for headers
- No formatting at all
- Just plain text content
```

## Advanced-Only Solutions

```
Advanced implementations only:
- Skip the simple/basic approach
- Go straight to the advanced solution
- Use latest features and best practices
- Optimize for performance and scalability
- Professional-grade code only
```

## Strict Scope Adherence

```
Stay strictly within scope:
- Answer ONLY what was asked
- Don't add "bonus" features
- Don't suggest enhancements
- Don't go beyond the requirements
- Laser-focused on the exact request
```
