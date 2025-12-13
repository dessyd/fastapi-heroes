# Usage Examples

Real-world scenarios and code examples for using the FastAPI Heroes API.

## Basic CRUD Operations

### Create a Hero

```bash
curl -X POST http://localhost:8000/heroes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Spider-Man",
    "secret_name": "Peter Parker",
    "age": 23
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "Spider-Man",
  "secret_name": "Peter Parker",
  "age": 23,
  "team_id": null
}
```

### List All Heroes

```bash
# Get first 10 heroes
curl http://localhost:8000/heroes

# Get with pagination
curl http://localhost:8000/heroes?offset=10&limit=20
```

### Get Single Hero

```bash
curl http://localhost:8000/heroes/1
```

### Update Hero

```bash
curl -X PATCH http://localhost:8000/heroes/1 \
  -H "Content-Type: application/json" \
  -d '{"age": 24}'
```

### Delete Hero

```bash
curl -X DELETE http://localhost:8000/heroes/1
```

## Real-World Scenarios

### Scenario 1: Building a Superhero Team

```bash
#!/bin/bash

# 1. Create a team
TEAM_RESPONSE=$(curl -s -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "Avengers", "headquarters": "New York"}')

TEAM_ID=$(echo $TEAM_RESPONSE | jq '.id')
echo "Created team: $TEAM_ID"

# 2. Create multiple heroes
curl -s -X POST http://localhost:8000/heroes \
  -H "Content-Type: application/json" \
  -d '{"name": "Iron Man", "secret_name": "Tony Stark", "age": 48, "team_id": '$TEAM_ID'}' | jq

curl -s -X POST http://localhost:8000/heroes \
  -H "Content-Type: application/json" \
  -d '{"name": "Spider-Man", "secret_name": "Peter Parker", "age": 23, "team_id": '$TEAM_ID'}' | jq

curl -s -X POST http://localhost:8000/heroes \
  -H "Content-Type: application/json" \
  -d '{"name": "Captain America", "secret_name": "Steve Rogers", "age": 100, "team_id": '$TEAM_ID'}' | jq

# 3. Get the team with all heroes
curl -s http://localhost:8000/teams/$TEAM_ID | jq '.heroes'
```

### Scenario 2: Frontend Integration (JavaScript/React)

```javascript
// React example using fetch API

async function fetchHeroes() {
  try {
    const response = await fetch('http://localhost:8000/heroes');
    const heroes = await response.json();
    return heroes;
  } catch (error) {
    console.error('Error fetching heroes:', error);
  }
}

async function createHero(heroData) {
  try {
    const response = await fetch('http://localhost:8000/heroes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(heroData)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const newHero = await response.json();
    return newHero;
  } catch (error) {
    console.error('Error creating hero:', error);
  }
}

async function updateHero(heroId, updates) {
  try {
    const response = await fetch(`http://localhost:8000/heroes/${heroId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });

    return await response.json();
  } catch (error) {
    console.error('Error updating hero:', error);
  }
}

async function deleteHero(heroId) {
  try {
    const response = await fetch(`http://localhost:8000/heroes/${heroId}`, {
      method: 'DELETE'
    });

    return response.status === 204;
  } catch (error) {
    console.error('Error deleting hero:', error);
  }
}

// Usage in React component
import React, { useState, useEffect } from 'react';

export function HeroesComponent() {
  const [heroes, setHeroes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHeroes().then(data => {
      setHeroes(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <p>Loading heroes...</p>;

  return (
    <div>
      <h1>Heroes</h1>
      <ul>
        {heroes.map(hero => (
          <li key={hero.id}>
            {hero.name} ({hero.secret_name}) - Age: {hero.age}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Scenario 3: Bulk Import from CSV

```python
import csv
import asyncio
import httpx

async def bulk_import_heroes(csv_file):
    """Import heroes from CSV file into API"""

    heroes = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            heroes.append({
                'name': row['name'],
                'secret_name': row['secret_name'],
                'age': int(row['age']) if row.get('age') else None,
                'team_id': int(row['team_id']) if row.get('team_id') else None
            })

    # Create heroes concurrently
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post('http://localhost:8000/heroes', json=hero)
            for hero in heroes
        ]
        results = await asyncio.gather(*tasks)

    # Report results
    successful = sum(1 for r in results if r.status_code == 201)
    print(f"✅ Imported {successful}/{len(heroes)} heroes")

    return results

# Usage
# Create heroes.csv:
# name,secret_name,age,team_id
# Thor,Thor Odinson,1500,1
# Black Widow,Natasha Romanoff,35,1

# asyncio.run(bulk_import_heroes('heroes.csv'))
```

### Scenario 4: Team Analytics

```python
import httpx

async def get_team_statistics(team_id: int):
    """Get statistics about a team"""

    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://localhost:8000/teams/{team_id}')
        team_data = response.json()

    heroes = team_data['heroes']

    stats = {
        'team_id': team_id,
        'team_name': team_data['name'],
        'headquarters': team_data['headquarters'],
        'total_heroes': len(heroes),
        'average_age': sum(h['age'] for h in heroes if h['age']) / len([h for h in heroes if h['age']]),
        'heroes': [h['name'] for h in heroes]
    }

    return stats

# Usage
# stats = asyncio.run(get_team_statistics(1))
# print(f"Team: {stats['team_name']}")
# print(f"Heroes: {len(stats['heroes'])}")
# print(f"Average age: {stats['average_age']:.1f}")
```

### Scenario 5: Error Handling

```python
import httpx
from httpx import HTTPStatusError

async def create_hero_with_validation(hero_data):
    """Create hero with proper error handling"""

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'http://localhost:8000/heroes',
                json=hero_data
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 422:
                # Validation error
                errors = e.response.json()
                print(f"❌ Validation error: {errors['detail']}")
            elif e.response.status_code == 404:
                print("❌ Team not found")
            else:
                print(f"❌ HTTP error: {e.response.status_code}")
            return None

        except httpx.RequestError as e:
            print(f"❌ Request failed: {e}")
            return None

# Usage with error cases
# Valid hero
# hero = await create_hero_with_validation({
#     'name': 'Deadpool',
#     'secret_name': 'Wade Wilson',
#     'age': 35
# })

# Missing required field (causes 422)
# hero = await create_hero_with_validation({
#     'name': 'Deadpool'
#     # Missing secret_name
# })
```

## Using Python Requests Library

```python
import requests

def get_all_heroes():
    """Get list of all heroes"""
    response = requests.get('http://localhost:8000/heroes')
    response.raise_for_status()
    return response.json()

def create_hero(name, secret_name, age=None):
    """Create a new hero"""
    payload = {
        'name': name,
        'secret_name': secret_name,
        'age': age
    }
    response = requests.post('http://localhost:8000/heroes', json=payload)
    response.raise_for_status()
    return response.json()

def update_hero(hero_id, **updates):
    """Update hero with partial data"""
    response = requests.patch(
        f'http://localhost:8000/heroes/{hero_id}',
        json=updates
    )
    response.raise_for_status()
    return response.json()

def delete_hero(hero_id):
    """Delete a hero"""
    response = requests.delete(f'http://localhost:8000/heroes/{hero_id}')
    return response.status_code == 204

# Usage
heroes = get_all_heroes()
print(f"Total heroes: {len(heroes)}")

new_hero = create_hero('Spider-Man', 'Peter Parker', 23)
print(f"Created: {new_hero['name']} (ID: {new_hero['id']})")

updated = update_hero(new_hero['id'], age=24)
print(f"Updated age to {updated['age']}")

deleted = delete_hero(new_hero['id'])
print(f"Deleted: {deleted}")
```

## Using cURL with jq for JSON Processing

```bash
# Pretty print response
curl http://localhost:8000/heroes | jq

# Extract specific field
curl http://localhost:8000/heroes | jq '.[].name'

# Filter heroes by age
curl http://localhost:8000/heroes | jq '.[] | select(.age > 30)'

# Count heroes
curl http://localhost:8000/heroes | jq 'length'

# Get hero and save to file
curl http://localhost:8000/heroes/1 | jq > hero_1.json

# Create hero and extract ID
HERO_ID=$(curl -s -X POST http://localhost:8000/heroes \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","secret_name":"Test"}' | jq '.id')

echo "Created hero with ID: $HERO_ID"
```

## Testing the API

```bash
# Run with pytest
pytest app/test_main.py -v

# Run specific test
pytest app/test_main.py::test_create_hero -v

# Run with coverage
pytest app/test_main.py --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

See [Contributing Guide](CONTRIBUTING.md) for running tests during development.
