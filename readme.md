# InfoRebornNew RESTful API by Salman Khokhar

This project provides a RESTful API for an InfoRebornNew website, offering information about in-season sports events and their respective odds/rates. The API utilizes Flask and external APIs to handle HTTP requests and responses.

## Features

- Retrieve information about active sports events
- Fetch odds/rates for specific sports events
- Get event scores
- Retrieve upcoming events

## Setup

1. Clone the repository:

```bash
git clone https://github.com/msalmankhokhar/betting-website-api.git
cd betting-website-api
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the application:

   - Ensure you have a `settings.json` file in the root directory of the project.
   - Update the `settings.json` file with necessary configurations, such as external URLs and API keys.

4. Run the application:

```bash
python3 app.py
```

## API Endpoints

### 1. Get Active Events

- **URL:** `/events/<string:sport_name>`
- **Method:** `GET`
- **Description:** Retrieve active events for a specific sport.
- **Parameters:**
  - `sport_name` (string): Name of the sport. Use 'all' to retrieve events for all sports.
- **Response:**
  - Success: Returns a JSON object containing active events.
  - Error: Returns an error message if the sport name is invalid.

### 2. Get Event Data

- **URL:** `/odds/<string:sport_name>/<string:event_key>`
- **Method:** `GET`
- **Description:** Retrieve data (such as odds/rates) for a specific event.
- **Parameters:**
  - `sport_name` (string): Name of the sport.
  - `event_key` (string): Unique identifier for the event.
- **Response:**
  - Success: Returns a JSON object containing event data.
  - Error: Returns an error message if the event key is invalid.

### 3. Get Event Scores

- **URL:** `/scores/<string:sport_name>/<string:event_key>`
- **Method:** `GET`
- **Description:** Retrieve scores for a specific event.
- **Parameters:**
  - `sport_name` (string): Name of the sport.
  - `event_key` (string): Unique identifier for the event.
- **Response:**
  - Success: Returns a JSON object containing event scores.
  - Error: Returns an error message if the event key is invalid or scores are not available.

### 4. Get Upcoming Events

- **URL:** `/upcoming/<string:sport_name>`
- **Method:** `GET`
- **Description:** Retrieve upcoming events for a specific sport.
- **Parameters:**
  - `sport_name` (string): Name of the sport. Use 'all' to retrieve upcoming events for all sports.
- **Response:**
  - Success: Returns a JSON object containing upcoming events.
  - Error: Returns an error message if the sport name is invalid.

## Usage Examples

### 1. Retrieve Active Events

#### Request

```http
GET /events/Soccer
```

#### Response

```json
{
  "success": true,
  "response": [
    {
      "event_key": "1",
      "event title": "Premier League",
      "description": "Soccer League",
      "home": "Manchester United",
      "away": "Liverpool"
    },
    {
      "event_key": "2",
      "event title": "La Liga",
      "description": "Football League",
      "home": "Real Madrid",
      "away": "Barcelona"
    }
  ]
}
```

### 2. Retrieve Event Data

#### Request

```http
GET /odds/Soccer/1
```

#### Response

```json
{
  "success": true,
  "response": {
    "sport name": "Soccer",
    "data from BetsAPI": {
      "eventId": "1",
      "eventName": "Premier League",
      "odds": {
        "home_team": 2.5,
        "away_team": 1.8,
        "draw": 2.2
      }
    }
  }
}
```

### 3. Retrieve Event Scores

#### Request

```http
GET /scores/Soccer/1
```

#### Response

```json
{
  "success": true,
  "response": {
    "source": "BetsAPI",
    "sport name": "Soccer",
    "scores": {
      "home_team": 2,
      "away_team": 1
    }
  }
}
```

### 4. Retrieve Upcoming Events

#### Request

```http
GET /upcoming/Cricket
```

#### Response

```json
{
  "success": true,
  "response": [
    {
      "upcoming events of Cricket": [
        {
          "event_key": "1",
          "event title": "T20 World Cup",
          "home": "India",
          "away": "Australia"
        },
        {
          "event_key": "2",
          "event title": "Ashes Series",
          "home": "England",
          "away": "Australia"
        }
      ]
    }
  ]
}
```

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

--- 

This README.md provides an overview of the API, including setup instructions, available endpoints, usage examples, contribution guidelines, and licensing information.

If you have any questions or encounter any issues, feel free to contact [Salman Khokhar](https://github.com/msalmankhokhar).