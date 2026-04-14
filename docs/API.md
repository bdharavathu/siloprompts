# API Reference

Base URL: `http://localhost:5000` (pip) or `http://localhost:5002` (Docker)

## Endpoints

### List Prompts
```bash
GET /api/prompts
```
Returns all prompts with metadata (title, category, tags, sections count, size, modified date).

```bash
curl http://localhost:5002/api/prompts
```

### Get Prompt Details
```bash
GET /api/prompts/<path>
```
Returns full content: raw markdown, parsed sections, tags, description.

```bash
curl http://localhost:5002/api/prompts/coding/code-review.md
```

### Create Prompt
```bash
POST /api/prompts
Content-Type: application/json
```

```bash
curl -X POST http://localhost:5002/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "category": "coding",
    "filename": "my-prompt",
    "title": "My Prompt",
    "sections": [{"title": "Section 1", "prompt": "Your prompt text here"}],
    "tags": ["python", "debugging"]
  }'
```

**Required fields:** `category`, `filename`, `title`, `sections`
**Optional fields:** `tags`

### Update Prompt
```bash
PUT /api/prompts/<path>
Content-Type: application/json
```

```bash
curl -X PUT http://localhost:5002/api/prompts/coding/my-prompt.md \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "sections": [{"title": "Section 1", "prompt": "Updated text"}],
    "tags": ["python"]
  }'
```

**Required fields:** `title`, `sections`
**Optional fields:** `tags` (omit to preserve existing tags)

### Delete Prompt
```bash
DELETE /api/prompts/<path>
```

```bash
curl -X DELETE http://localhost:5002/api/prompts/coding/my-prompt.md

# Also remove empty category folder
curl -X DELETE "http://localhost:5002/api/prompts/coding/my-prompt.md?delete_empty_category=true"
```

### Download Prompt
```bash
GET /api/prompts/<path>/download
```
Downloads the raw `.md` file.

```bash
curl -O http://localhost:5002/api/prompts/coding/code-review.md/download
```

### Import Prompt
```bash
POST /api/prompts/import
Content-Type: multipart/form-data
```

```bash
curl -X POST http://localhost:5002/api/prompts/import \
  -F "file=@my-prompt.md" \
  -F "category=coding"
```

**Validation:** `.md` extension required, max 1MB, no overwrites (409 if exists).

### List Categories
```bash
GET /api/categories
```

```bash
curl http://localhost:5002/api/categories
```

### List Tags
```bash
GET /api/tags
```
Returns all unique tags with counts.

```bash
curl http://localhost:5002/api/tags
```

### Search
```bash
GET /api/search?q=<query>
```

```bash
curl "http://localhost:5002/api/search?q=debug"

# Case-sensitive search
curl "http://localhost:5002/api/search?q=Debug&case_sensitive=true"
```

### Health Check
```bash
GET /health
```

```bash
curl http://localhost:5002/health
```

Returns: status, version, prompts directory path, timestamp.
