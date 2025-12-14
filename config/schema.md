# Entity Relationship Diagram

```mermaid
erDiagram

    team {
        int id
        string name
        string headquarters
    }

    hero {
        int id
        string name
        string secret_name
        int age
        int team_id
    }
    hero ||--o| team : ""
```

## Tables


### Team

| Column | Type | Nullable | Primary Key |
|--------|------|----------|-------------|
| id | int | Yes | Yes |
| name | string | No | No |
| headquarters | string | No | No |

### Hero

| Column | Type | Nullable | Primary Key |
|--------|------|----------|-------------|
| id | int | Yes | Yes |
| name | string | No | No |
| secret_name | string | No | No |
| age | int | Yes | No |
| team_id | int | Yes | No |
