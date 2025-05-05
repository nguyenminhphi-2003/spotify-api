# Django Spotify App

This is a Django application with WebSocket capabilities through Channels, utilizing MongoDB as a database backend.

## Requirements

- Python 3.8+
- MongoDB
- pip
- Linux-based OS *(Optional)*

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/nguyenminhphi-2003/spotify-api
   cd spotify-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root directory with your configuration:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   MONGO_URI=mongodb://localhost:27017/spotify
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   ```

## Running the Application

### Start the Django Development Server

```
python manage.py runserver
```

### Start the WebSocket Server

```
daphne -b 0.0.0.0 -p 5000 spotify.asgi:application
```

## Project Structure

The project uses:

- **Django**: Web framework
- **Django REST Framework**: For API endpoints
- **Channels**: For WebSocket functionality
- **MongoDB/MongoEngine**: NoSQL database
- **Boto3**: AWS SDK for Python, likely for S3 file storage

## Tests

To run tests:

```
python manage.py test
```

## License

*This project is licensed under the terms of the MIT license.*