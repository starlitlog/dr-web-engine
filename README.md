# DR Web Engine

**DR Web Engine** is an open-source data retrieval engine designed for extracting structured data from web pages using Playwright. It allows users to define queries in JSON5 or YAML format and execute them to retrieve data from websites. The project is highly extensible and can be used for web scraping, data extraction, and automation tasks.

---

## Features
- **Queryable Web**: Define data extraction queries in JSON5 or YAML format.
- **Playwright Integration**: Leverages Playwright for reliable and efficient web automation.
- **Extensible**: Easily extend the engine by adding new parsers, extractors, or custom logic.
- **Command-Line Interface (CLI)**: Run queries directly from the terminal.
- **Docker Support**: Use the engine in a containerized environment for easy deployment.

---

## Installation

### **Option 1: Install from Source**
1. Clone the repository:
   ```bash
   git clone https://github.com/starlitlog/dr-web-engine.git
   cd dr-web-engine
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the project in editable mode:
   ```bash
   pip install -e .
   ```

### **Option 2: Install via pip**
The project is available on PyPI. You can install it directly via pip:
```bash
pip install dr-web-engine
```

### **Option 3: Run with Docker**
1. Build the Docker image:
   ```bash
   docker build -t dr-web-engine .
   ```
2. Run the container, mounting your local data directory:
   ```bash
   docker run -v $(pwd)/data:/app/data dr-web-engine -q /app/data/query.json5 -o /app/data/output.json
   ```

---

## Usage

### **Command Line Interface (CLI)**
To execute queries using the CLI, run:
```bash
dr-web-engine -q engine/data/query.json5 -o engine/data/output.json
```

#### **Available Parameters**
- `-q` or `--query`: Path to the query file (JSON5 or YAML format).
- `-o` or `--output`: Path to the output file where results will be saved.
- `-f` or `--format`: Query format (`json5` or `yaml`). Default: `json5`.
- `-l` or `--log-level`: Set the logging level (`error`, `warning`, `info`, `debug`). Default: `error`.
- `--log-file`: Path to a log file. If not specified, logs are printed to stdout.

---

## Extending the Project

### **Adding New Parsers**
To add a custom parser:
1. Create a new parser in the `web_engine/parsers/` directory.
2. Implement a `parse()` function that takes a file path and returns a parsed query.
3. Register the parser in `web_engine/parsers/__init__.py` using the `get_parser()` function.

Example:
```python
# web_engine/parsers/custom_parser.py
def parse(file_path):
    # Custom parsing logic here
    return parsed_query
```

### **Adding New Extractors**
To add a new extractor:
1. Create a new extractor in the `web_engine/extractors/` directory.
2. Implement the extraction logic.
3. Update the `execute_query()` function in `web_engine/engine.py` to use the new extractor.

### **Adding New Query Types**
To define a new query type:
1. Create a new query model in `web_engine/models.py`.
2. Modify the `ExtractionQuery` class to support the new query type.
3. Add the relevant parsing and extraction logic for the new query type.

---

## Example Queries

### **JSON5 Query Example**
```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@xpath": "//div[@class='item']",
      "@name": "items",
      "@fields": {
        "title": ".//h2",
        "description": ".//p"
      }
    }
  ],
  "@pagination": {
    "@xpath": "//a[@class='next']",
    "@limit": 5
  }
}
```

### **YAML Query Example**
```yaml
url: https://example.com
steps:
  - xpath: //div[@class='item']
    name: items
    fields:
      title: .//h2
      description: .//p
pagination:
  xpath: //a[@class='next']
  limit: 5
```

---

## Learn More

For additional details and use cases, check out the blog posts at:
- [Queryable Web Blog](https://ylli.prifti.us/category/queryable-web/)

---

## Contributing

Contributions are welcome! To contribute, follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Support

If you encounter any issues or have questions, please open an issue on [GitHub](https://github.com/starlitlog/dr-web-engine/issues).

---
