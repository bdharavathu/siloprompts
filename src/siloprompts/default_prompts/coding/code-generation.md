# Code Generation Prompts

## Function/Method Generation

```
Create a [LANGUAGE] function that:
- Purpose: [WHAT IT SHOULD DO]
- Input parameters: [LIST PARAMETERS AND TYPES]
- Return value: [EXPECTED RETURN TYPE]
- Requirements:
  * [REQUIREMENT 1]
  * [REQUIREMENT 2]
  * [REQUIREMENT 3]
- Include error handling and input validation
- Add appropriate comments and documentation
```

## API Endpoint Creation

```
Create a REST API endpoint with the following specifications:

**Endpoint:** [METHOD] /api/[path]
**Purpose:** [DESCRIPTION]
**Request Body:**
[JSON STRUCTURE]

**Response:**
- Success (200): [JSON STRUCTURE]
- Error (4xx/5xx): [ERROR STRUCTURE]

**Requirements:**
- Authentication: [YES/NO, TYPE]
- Validation rules: [LIST RULES]
- Database operations: [DESCRIBE]

Language/Framework: [SPECIFY]
```

## Database Schema Design

```
Design a database schema for [PURPOSE]:

**Entities:**
- [ENTITY 1]: [DESCRIPTION]
- [ENTITY 2]: [DESCRIPTION]

**Requirements:**
- [REQUIREMENT 1]
- [REQUIREMENT 2]

**Constraints:**
- [CONSTRAINT 1]
- [CONSTRAINT 2]

Please provide:
1. Table structures with columns and data types
2. Relationships and foreign keys
3. Indexes for optimization
4. Sample SQL CREATE statements
```

## Test Case Generation

```
Generate comprehensive test cases for the following code:

[PASTE YOUR CODE]

Include:
- Unit tests for all functions
- Edge cases and boundary conditions
- Error scenarios
- Mock data where needed

Framework: [pytest/jest/junit/etc]
```

## Algorithm Implementation

```
Implement [ALGORITHM NAME] in [LANGUAGE] with:

**Problem:**
[DESCRIBE THE PROBLEM]

**Input Format:**
[DESCRIBE INPUT]

**Output Format:**
[DESCRIBE OUTPUT]

**Constraints:**
- [CONSTRAINT 1]
- [CONSTRAINT 2]

**Example:**
Input: [EXAMPLE INPUT]
Output: [EXAMPLE OUTPUT]

Please include:
- Time and space complexity analysis
- Comments explaining the approach
- Test cases
```
