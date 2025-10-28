# HNG 13 Backend Wizards - Stage 2 Task  
## Country Currency & Exchange API
This is Flask-based RESTful API that provides detailed information about countries and their currencies.
It allows users to view all countries, refresh the country data from an external API and generate a summary image of the 
data.

___
## Features
- Fetch and store country and currency data from an external API  
- View all stored countries and currencies
- Regenerate summary image of country data
- Health check endpoint to verify API and database status  
___
## Tech Stack
- **Language:** Python
- **Framework:** Flask
- **Database** SQLite3
- **ORM:** SQLAlchemy + Flask-Migrate 
- **Image Generation:** Pillow
- **Requests**
___
## ⚙️ Setup Instructions
```bash
# 1. Clone the repository
git clone https://github.com/Richardeze/HNG_Stage_2.git
cd HNG_Stage_2

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```
## 🔗 API ENDPOINT
| Method     | Endpoint             | Description                                                                                   |
|:-----------|:---------------------|:----------------------------------------------------------------------------------------------|
| **POST**   | `/countries/refresh` | Fetch all countries and exchange rates, cache them in DB and generate summary image           |
| **GET**    | `/countries`         | Get all countries (supports filters: ?region=Africa, ?currency=NGN; sorting: ?sort=gdp_desc ) |
| **GET**    | `/countries/<name>`  | Get a single country by name                                                                  |
| **GET**    | `/status`            | Show total countries and last refresh timestamp                                               |
| **DELETE** | `/countries/<name>`  | Delete a country record                                                                       |
| **GET**    | `/countries/image`   | Serve generated summary image                                                                 |

## Example Response
**GET /status**  
{  
  "database": "connected",  
  "message": "Country API is working smoothly",
  "status": "ok"
}

## Live API URL
You can access the deployed API here:  



