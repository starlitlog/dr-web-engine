"""
Output Format Plugin Implementation
Provides JSONL, LLM-optimized, and agentic output formats for AI workflows.
"""

import json
import time
from typing import List, Dict, Any, Optional, Union, IO
from enum import Enum
from pathlib import Path
import logging
from engine.web_engine.plugin_interface import DrWebPlugin, PluginMetadata
from engine.web_engine.processors import StepProcessor
from engine.web_engine.models import BaseModel, OutputFormatStep
from pydantic import Field, validator

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    JSONL = "jsonl"
    LLM_MESSAGES = "llm-messages"
    OPENAI_CHAT = "openai-chat"
    ANTHROPIC_MESSAGES = "anthropic-messages"
    AGENT_STRUCTURED = "agent-structured"
    TOKEN_OPTIMIZED = "token-optimized"
    STREAMING_JSONL = "streaming-jsonl"


class CompressionLevel(str, Enum):
    NONE = "none"
    MINIMAL = "minimal"  # Remove unnecessary whitespace
    COMPACT = "compact"  # Compact field names
    ULTRA = "ultra"      # Aggressive token optimization


# OutputFormatStep is now imported from models.py


class OutputFormatProcessor(StepProcessor):
    """
    Output format processor for AI-optimized data export.
    
    Features:
    - JSONL streaming for real-time processing
    - LLM-optimized message formats (OpenAI, Anthropic)
    - Token compression and optimization
    - Agent-structured outputs
    - Field mapping and transformation
    - Metadata enrichment
    """
    
    def __init__(self):
        super().__init__()
        self.priority = 80  # Lower priority - runs after data extraction
        self.active_streams = {}  # Track open file streams
        self.token_cache = {}  # Cache for token counting
    
    def can_handle(self, step: Any) -> bool:
        return isinstance(step, OutputFormatStep)
    
    def get_supported_step_types(self) -> List[str]:
        return ["OutputFormatStep"]
    
    def execute(self, context: Any, page: Any, step: OutputFormatStep) -> List[Any]:
        """Execute step with output formatting."""
        try:
            # Execute the target step first to get data
            results = self._execute_target_step(context, page, step.target_step)
            
            if not results:
                self.logger.warning("No data to format - target step returned empty results")
                return []
            
            # Process and format the results
            formatted_data = self._format_results(results, step, context, page)
            
            # Output the formatted data
            self._output_data(formatted_data, step)
            
            # Return original results for potential chaining
            return results
            
        except Exception as e:
            self.logger.error(f"Output formatting failed: {e}")
            return []
    
    def _execute_target_step(self, context: Any, page: Any, target_step: Dict[str, Any]) -> List[Any]:
        """Execute the target step to get data."""
        from engine.web_engine.models import parse_step
        from engine.web_engine.processors import get_default_registry
        
        try:
            step_obj = parse_step(target_step)
            registry = get_default_registry()
            processor = registry.find_processor(step_obj)
            
            if processor:
                return processor.execute(context, page, step_obj)
            else:
                self.logger.error(f"No processor found for step type: {type(step_obj).__name__}")
                return []
                
        except Exception as e:
            raise
    
    def _format_results(self, results: List[Any], step: OutputFormatStep, context: Any, page: Any) -> List[Dict[str, Any]]:
        """Format results according to the specified output format."""
        formatted_results = []
        
        for result in results:
            if not isinstance(result, dict):
                result = {"content": str(result)}
            
            # Apply field mapping
            if step.field_mapping:
                result = self._apply_field_mapping(result, step.field_mapping)
            
            # Exclude specified fields
            if step.exclude_fields:
                result = {k: v for k, v in result.items() if k not in step.exclude_fields}
            
            # Add metadata if requested
            if step.include_metadata:
                result = self._add_metadata(result, step, context, page)
            
            # Format according to output type
            if step.format == "jsonl":
                formatted_result = result
                
            elif step.format == "llm-messages":
                formatted_result = self._format_as_llm_messages(result, step)
                
            elif step.format == "openai-chat":
                formatted_result = self._format_as_openai_chat(result, step)
                
            elif step.format == "anthropic-messages":
                formatted_result = self._format_as_anthropic_messages(result, step)
                
            elif step.format == "agent-structured":
                formatted_result = self._format_as_agent_structured(result, step)
                
            elif step.format == "token-optimized":
                formatted_result = self._format_token_optimized(result, step)
                
            else:
                formatted_result = result
            
            # Apply compression
            if step.compression != "none":
                formatted_result = self._apply_compression(formatted_result, step.compression)
            
            # Check token limits (if attributes exist)
            if hasattr(step, 'max_tokens_per_record') and step.max_tokens_per_record:
                formatted_result = self._enforce_token_limit(formatted_result, step.max_tokens_per_record, getattr(step, 'token_model', 'gpt-4'))
            
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def _apply_field_mapping(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Apply field name mapping."""
        mapped_data = {}
        for old_name, new_name in mapping.items():
            if old_name in data:
                mapped_data[new_name] = data[old_name]
        
        # Keep unmapped fields
        for key, value in data.items():
            if key not in mapping:
                mapped_data[key] = value
        
        return mapped_data
    
    def _add_metadata(self, data: Dict[str, Any], step: OutputFormatStep, context: Any, page: Any) -> Dict[str, Any]:
        """Add metadata to the result."""
        metadata = {}
        
        if step.add_timestamps:
            metadata["timestamp"] = time.time()
            metadata["extracted_at"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        
        if step.add_source_url and page:
            metadata["source_url"] = getattr(page, 'url', None)
        
        if step.add_extraction_metadata:
            metadata["extraction_format"] = step.format.value
            metadata["compression"] = step.compression.value
            metadata["drweb_version"] = "1.0.0"  # TODO: Get actual version
        
        if metadata:
            data["_metadata"] = metadata
        
        return data
    
    def _format_as_llm_messages(self, data: Dict[str, Any], step: OutputFormatStep) -> Dict[str, Any]:
        """Format as generic LLM message structure."""
        message = {
            "role": "user",
            "content": self._extract_content_for_llm(data),
            "metadata": {
                "source": "drweb-extraction",
                "format": "llm-messages"
            }
        }
        
        if step.system_prompt:
            message["system"] = step.system_prompt
            
        return message
    
    def _format_as_openai_chat(self, data: Dict[str, Any], step: OutputFormatStep) -> Dict[str, Any]:
        """Format as OpenAI Chat Completion format."""
        messages = []
        
        if step.system_prompt:
            messages.append({
                "role": "system",
                "content": step.system_prompt
            })
        
        content = self._extract_content_for_llm(data)
        if step.user_template:
            content = step.user_template.format(content=content, **data)
        
        messages.append({
            "role": "user", 
            "content": content
        })
        
        return {
            "messages": messages,
            "metadata": {
                "source": "drweb-extraction",
                "format": "openai-chat",
                "extracted_fields": list(data.keys())
            }
        }
    
    def _format_as_anthropic_messages(self, data: Dict[str, Any], step: OutputFormatStep) -> Dict[str, Any]:
        """Format as Anthropic Messages format."""
        content = self._extract_content_for_llm(data)
        if step.user_template:
            content = step.user_template.format(content=content, **data)
        
        result = {
            "messages": [{
                "role": "user",
                "content": content
            }],
            "metadata": {
                "source": "drweb-extraction", 
                "format": "anthropic-messages"
            }
        }
        
        if step.system_prompt:
            result["system"] = step.system_prompt
        
        return result
    
    def _format_as_agent_structured(self, data: Dict[str, Any], step: OutputFormatStep) -> Dict[str, Any]:
        """Format for agent workflows."""
        structured = {
            "agent_input": {
                "role": step.agent_role or "data_processor",
                "task": step.task_description or "Process extracted data",
                "data": data,
                "context": {
                    "extraction_timestamp": time.time(),
                    "format": "agent-structured"
                }
            },
            "execution_metadata": {
                "requires_response": True,
                "context_window": step.context_window,
                "priority": "normal"
            }
        }
        
        return structured
    
    def _format_token_optimized(self, data: Dict[str, Any], step: OutputFormatStep) -> Dict[str, Any]:
        """Format with aggressive token optimization."""
        # Use short field names
        optimized = {}
        field_mapping = {
            "title": "t",
            "content": "c", 
            "description": "d",
            "url": "u",
            "text": "txt",
            "author": "a",
            "date": "dt",
            "timestamp": "ts"
        }
        
        for key, value in data.items():
            short_key = field_mapping.get(key, key[:3])  # Use mapping or first 3 chars
            
            # Optimize string values
            if isinstance(value, str):
                value = value.strip()
                # Remove extra whitespace
                value = ' '.join(value.split())
            
            optimized[short_key] = value
        
        return optimized
    
    def _extract_content_for_llm(self, data: Dict[str, Any]) -> str:
        """Extract the main content from data for LLM processing."""
        # Priority order for content fields
        content_fields = ["content", "text", "description", "title", "name", "value"]
        
        for field in content_fields:
            if field in data and data[field]:
                return str(data[field])
        
        # Fallback: join all string values
        text_parts = []
        for key, value in data.items():
            if isinstance(value, str) and value.strip():
                text_parts.append(f"{key}: {value}")
        
        return " | ".join(text_parts) if text_parts else json.dumps(data)
    
    def _apply_compression(self, data: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Apply compression to reduce token usage."""
        if level == "minimal":
            # Just clean up strings
            return self._clean_strings(data)
            
        elif level == "compact":
            # Use shorter field names and clean strings
            return self._compact_fields(self._clean_strings(data))
            
        elif level == "ultra":
            # Aggressive optimization
            return self._ultra_compress(data)
        
        return data
    
    def _clean_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up strings to remove unnecessary whitespace."""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = ' '.join(value.split())
            elif isinstance(value, dict):
                cleaned[key] = self._clean_strings(value)
            else:
                cleaned[key] = value
        return cleaned
    
    def _compact_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Use shorter field names."""
        mapping = {
            "timestamp": "ts", "created_at": "ca", "updated_at": "ua",
            "description": "desc", "content": "txt", "author": "by",
            "category": "cat", "tags": "tag", "metadata": "meta"
        }
        
        compacted = {}
        for key, value in data.items():
            new_key = mapping.get(key, key)
            compacted[new_key] = value
        
        return compacted
    
    def _ultra_compress(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ultra-aggressive compression."""
        # Remove metadata, use minimal field names, abbreviate text
        essential_data = {}
        
        for key, value in data.items():
            if key.startswith('_'):  # Skip metadata fields
                continue
                
            short_key = key[:2]  # Super short keys
            
            if isinstance(value, str):
                # Truncate very long strings
                if len(value) > 200:
                    value = value[:197] + "..."
                value = ' '.join(value.split())
            
            essential_data[short_key] = value
        
        return essential_data
    
    def _enforce_token_limit(self, data: Dict[str, Any], max_tokens: int, model: str) -> Dict[str, Any]:
        """Enforce token limit by truncating data."""
        # Simple approximation: ~4 chars per token for English
        estimated_tokens = len(json.dumps(data)) // 4
        
        if estimated_tokens <= max_tokens:
            return data
        
        # Try progressively more aggressive compression
        if estimated_tokens > max_tokens * 1.5:
            data = self._ultra_compress(data)
            estimated_tokens = len(json.dumps(data)) // 4
        
        # If still too long, truncate string fields
        if estimated_tokens > max_tokens:
            data = self._truncate_strings(data, max_tokens)
        
        return data
    
    def _truncate_strings(self, data: Dict[str, Any], target_tokens: int) -> Dict[str, Any]:
        """Truncate string fields to meet token limit."""
        current_size = len(json.dumps(data))
        target_size = target_tokens * 4  # Approximate
        
        if current_size <= target_size:
            return data
        
        reduction_factor = target_size / current_size
        
        truncated = {}
        for key, value in data.items():
            if isinstance(value, str):
                new_length = int(len(value) * reduction_factor)
                if new_length < len(value):
                    truncated[key] = value[:new_length] + "..."
                else:
                    truncated[key] = value
            else:
                truncated[key] = value
        
        return truncated
    
    def _output_data(self, data: List[Dict[str, Any]], step: OutputFormatStep):
        """Output formatted data to file or stream."""
        if not step.output_file:
            # Log to console if no output file specified
            for record in data:
                self.logger.info(f"Formatted output: {json.dumps(record)}")
            return
        
        output_path = Path(step.output_file)
        
        try:
            if step.streaming:
                self._stream_output(data, output_path, step)
            else:
                self._batch_output(data, output_path, step)
                
        except Exception as e:
            self.logger.error(f"Failed to write output to {output_path}: {e}")
    
    def _stream_output(self, data: List[Dict[str, Any]], output_path: Path, step: OutputFormatStep):
        """Stream output data in real-time."""
        stream_id = str(output_path)
        
        # Get or create stream
        if stream_id not in self.active_streams:
            self.active_streams[stream_id] = {
                "file": output_path.open('a', encoding='utf-8'),
                "buffer": [],
                "last_flush": time.time()
            }
        
        stream = self.active_streams[stream_id]
        
        # Add data to buffer
        stream["buffer"].extend(data)
        
        # Check if we should flush
        should_flush = (
            len(stream["buffer"]) >= step.batch_size or
            time.time() - stream["last_flush"] >= step.flush_interval
        )
        
        if should_flush:
            self._flush_stream(stream_id, step)
    
    def _flush_stream(self, stream_id: str, step: OutputFormatStep):
        """Flush buffered data to stream."""
        if stream_id not in self.active_streams:
            return
        
        stream = self.active_streams[stream_id]
        
        for record in stream["buffer"]:
            stream["file"].write(json.dumps(record) + "\n")
        
        stream["file"].flush()
        stream["buffer"].clear()
        stream["last_flush"] = time.time()
        
        self.logger.debug(f"Flushed stream {stream_id}")
    
    def _batch_output(self, data: List[Dict[str, Any]], output_path: Path, step: OutputFormatStep):
        """Output data in batch mode."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open('a', encoding='utf-8') as f:
            for record in data:
                f.write(json.dumps(record) + "\n")
        
        self.logger.info(f"Wrote {len(data)} records to {output_path}")
    
    def finalize(self):
        """Close all active streams."""
        for stream_id, stream in self.active_streams.items():
            try:
                # Flush any remaining data
                for record in stream["buffer"]:
                    stream["file"].write(json.dumps(record) + "\n")
                
                stream["file"].close()
                self.logger.info(f"Closed stream {stream_id}")
            except Exception as e:
                self.logger.error(f"Error closing stream {stream_id}: {e}")
        
        self.active_streams.clear()


class OutputFormatPlugin(DrWebPlugin):
    """
    Output Format plugin for AI-optimized data export.
    
    Provides JSONL streaming, LLM message formats, token optimization,
    and agent-structured outputs for AI workflows.
    """
    
    def __init__(self):
        self._processor = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="output-format",
            version="1.0.0",
            description="JSONL, LLM-optimized, and agentic output formats for AI workflows",
            author="DR Web Engine Team",
            homepage="https://github.com/starlitlog/dr-web-engine",
            supported_step_types=["OutputFormatStep"],
            dependencies=["pathlib"],
            min_drweb_version="0.10.0",
            enabled=True
        )
    
    def get_processors(self) -> List[StepProcessor]:
        if not self._processor:
            self._processor = OutputFormatProcessor()
        return [self._processor]
    
    def finalize(self) -> None:
        if self._processor:
            self._processor.finalize()
        self._processor = None