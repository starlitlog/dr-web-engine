# Internal Plugins

This directory contains internal plugins that are shipped with DR Web Engine. These plugins are automatically discovered and loaded without requiring separate installation.

## Available Internal Plugins

### 1. AI-Selector (`ai_selector/`)
AI-powered element selector that converts natural language descriptions to XPath selectors.

**Usage:**
```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@ai-select": "product prices",
      "@name": "prices"
    }
  ]
}
```

### 2. JSON-LD Extractor (`jsonld_extractor/`)
Extracts structured data in JSON-LD format from web pages.

**Usage:**
```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@jsonld": true,
      "@name": "structured_data"
    }
  ]
}
```

### 3. API Extractor (`api_extractor/`)
Makes API calls as part of the extraction pipeline.

**Usage:**
```json5
{
  "@url": "https://example.com",
  "@steps": [
    {
      "@api": "https://api.example.com/data",
      "@method": "GET",
      "@name": "api_data"
    }
  ]
}
```

## Creating New Internal Plugins

To create a new internal plugin:

1. Create a new directory under `internal-plugins/`:
   ```
   internal-plugins/
   └── my_plugin/
       ├── __init__.py
       └── plugin.py
   ```

2. Implement the plugin class in `plugin.py`:
   ```python
   from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
   
   class MyPlugin(DrWebPlugin):
       @property
       def metadata(self) -> PluginMetadata:
           return PluginMetadata(
               name="my-plugin",
               version="1.0.0",
               description="My internal plugin",
               author="Your Name"
           )
       
       def get_processors(self):
           return [MyProcessor()]
   ```

3. The plugin will be automatically discovered and loaded when DR Web Engine starts.

## Benefits of Internal Plugins

- **No installation required**: Automatically available with DR Web Engine
- **Version synchronized**: Always compatible with the current engine version
- **Easy development**: No need for separate repos or packaging
- **Immediate testing**: Changes are reflected immediately after restart
- **Shared maintenance**: Maintained alongside the main codebase

## Plugin Loading Order

1. Internal plugins (this directory)
2. User plugins (~/.drweb/plugins)
3. Project plugins (./plugins)
4. Installed plugins (via pip)

Internal plugins are loaded first to ensure core functionality is always available.