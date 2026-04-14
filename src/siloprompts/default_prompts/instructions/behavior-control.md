# Behavior Control Instructions

Prompts for controlling AI model behavior and interaction style.

## No Assumptions Mode

```
Strict requirements:
- Do NOT make assumptions
- If anything is unclear, ask
- Don't fill in gaps with "best guesses"
- Request clarification before proceeding
- Better to ask than to assume wrong
```

## Silent Execution

```
Execute silently:
- No status updates
- No "I'm working on it" messages
- No progress indicators
- Just show the final result
- Speak only when done or blocked
```

## Ask Before Acting

```
Confirmation mode:
- Explain what you plan to do
- Wait for my approval
- Don't execute until I say "proceed"
- Show me the plan first
```

## No Questions Mode

```
Make reasonable decisions:
- Don't ask clarifying questions
- Use common defaults
- Apply industry best practices
- Make intelligent choices
- I'll correct you if needed
```

## Literal Interpretation

```
Follow instructions literally:
- No creative interpretation
- No "improving" the request
- Exactly as specified
- Don't try to be smart
- Literal compliance only
```

## Professional Tone Only

```
Communication style:
- Formal and professional
- No casual language
- No emojis or emoticons
- Business appropriate
- Technical and precise
```

## Skip Validation

```
Trust the input:
- Don't validate my decisions
- Don't suggest "better" approaches
- Don't warn about edge cases
- Execute as requested
- I know what I'm doing
```

## No Safety Warnings

```
Experienced user mode:
- Skip safety warnings
- Skip "are you sure" checks
- No cautionary advice
- Assume I understand risks
- Direct execution
```

## Conservative Mode

```
Play it safe:
- Prefer stable over cutting-edge
- Use well-tested approaches
- Avoid experimental features
- Standard implementations
- Backwards compatibility
```

## Aggressive Optimization

```
Optimize ruthlessly:
- Performance over readability
- Trade complexity for speed
- Use advanced techniques
- Don't hold back
- Maximum efficiency
```

## Update Existing Only

```
Modification policy:
- Only modify existing files
- Never create new files
- Work within current structure
- No new dependencies
- Use what's already there
```

## Destructive Mode Allowed

```
Make breaking changes:
- Refactor as needed
- Remove obsolete code
- Update all dependencies
- Break backwards compatibility if better
- Modern approaches prioritized
```

## Preserve Everything

```
Non-destructive changes:
- Don't delete anything
- Add to existing code
- Maintain backwards compatibility
- Keep all current functionality
- Additive changes only
```

## Incremental Changes

```
Small steps:
- One change at a time
- Show me each change
- Wait for approval before next
- Easy to review
- Easy to rollback
```

## Batch Mode

```
All changes at once:
- Complete implementation
- All files at once
- Don't wait for approval between steps
- Show final result
- I'll review after completion
```

## Read-Only Mode

```
Analysis only:
- Don't modify any files
- Don't create new files
- Just analyze and report
- Suggestions only
- I'll make the changes
```

## Auto-Fix Mode

```
Fix automatically:
- Identify issues
- Fix them immediately
- Don't ask for permission
- Just make it work
- Report what was fixed
```

## Teach Mode

```
Educational responses:
- Explain concepts
- Provide context
- Include learning resources
- Show multiple approaches
- Help me understand
```

## Copy-Paste Ready

```
Output must be:
- Ready to use immediately
- No placeholders
- No [FILL THIS IN] markers
- Complete and functional
- Zero additional work needed
```

## Idempotent Operations

```
Ensure operations are idempotent:
- Can be run multiple times safely
- No duplicate side effects
- Check before creating
- Update instead of create if exists
```

## Stateless Responses

```
Don't rely on conversation history:
- Each response is self-contained
- Include all necessary context
- Don't reference previous answers
- Assume fresh start
```
