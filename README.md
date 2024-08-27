# Semantic Matching Service Test Environment

This project sets up a test environment for a [Semantic Matching Service](https://github.com/s-heppner/python-semantic-matcher). The environment allows you to execute tests either through a Python script or by using Docker Compose.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Environment](#running-the-environment)
- [Running Individual Tests](#running-individual-tests)
- [Add Tests](#add-tests)

## Overview

This project provides a framework to test the functionality of a Semantic Matching Service. The environment can be launched as a whole, or specific tests can be executed individually using Docker Compose.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.x
- Docker
- Docker Compose

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dxvidnrt/test-semantic-matcher.git
   cd test-semantic-matcher
   ```

2. **Install the required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Environment

To start the entire test environment, simply run:
```bash
python main/start_all.py
```

This will set up and execute all tests within the test cases folder.

## Running Individual Tests

If you want to run individual tests, you can do so using Docker Compose. Navigate to the directory containing the `docker-compose.yml` file and execute:
```bash
docker-compose up
```

This will spin up the containers necessary for the specific tests defined in the Docker Compose configuration

### Add Tests

To add more tests, create a new folder beginning with `class_` in `test cases`. Mimic the structure of previous test classes and overwrite the `create()` method in the class `Test` for each test case.
