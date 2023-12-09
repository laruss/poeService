# poeService

## Overview

The `poeService` repository serves as a proxy for interacting with the API provided by `poe.com`. This setup is designed for easy integration within a Docker environment, facilitating direct access to `poe.com`'s API. The service leverages MongoDB for storing configurations such as API tokens. An example `docker-compose.yml` file is included in the repository to simplify deployment.

### Prerequisites

Before starting, ensure you have the following installed:
- Docker
- Docker Compose

### Getting Started

To use `poeService`, follow these steps:

1. **Clone the Repository:**
   ```sh
   git clone https://github.com/laruss/poeService.git
   ```
   
2. **Navigate to the Directory:**
   ```sh
   cd poeService
   ```
   
3. **Copy .env.sample to .env:**
   ```sh
   cp .env.sample .env
   ```
   
4. **Edit .env:**
   ```sh
    nano .env # or use your favorite editor
    ```

5. **Start the Service Using Docker Compose:**
   Use the provided `docker-compose.yml` file to start the service along with MongoDB.
   ```sh
   docker-compose up -d
   ```
   This will start the service and MongoDB in detached mode. The service will be accessible at `http://localhost:5002` by default.

### Using Rest API with session id

After the service is up, set the API Session in headers. All the requests must have the following header:

 ```sh
 curl -X POST "http://localhost:<PORT>/settings" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"session-id\": \"<your_token>\"}"
 ```

### Usage

With `poeService` running, you can now interact with the `poe.com` API via the proxy. The service acts as a middleware, handling requests and responses to and from `poe.com`.

Service has OpenAPI documentation, accessible at `http://localhost:5002/openapi/` (change 5002 to your port).
This provides an interactive guide for all the available features of the `poeService`.

### Links to used libraries

- [python-decouple](https://github.com/HBNetwork/python-decouple)
- [flask](https://flask.palletsprojects.com/en/3.0.x/)
- [Flask-PyMongo](https://flask-pymongo.readthedocs.io/en/latest/)
- [pymongo](https://pymongo.readthedocs.io/en/stable/)
- [pydantic-2.4.2](https://docs.pydantic.dev/latest/)

### OpenAPI Documentation

Explore the API endpoints and their functionalities in detail via the OpenAPI documentation, accessible at
`http://localhost:5002/openapi/` (change 5002 to your port).
This provides an interactive guide for all the available features of the `poeService`.

### Contribution

Contributions are greatly appreciated. If you have any suggestions or improvements, feel free to fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

### License

This project is released under the MIT License—see the [LICENSE](LICENSE) file for details.
