"""
Advanced MCP Server with Comprehensive AI Capabilities
Includes: RAG, Image Generation, Code Execution, Web Scraping, Data Analysis, and more
"""
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import all modules
from rag_system import RAGSystem, CodeRAG
from image_generator import ImageGenerator, ImageEditor
from code_executor import CodeExecutor
from web_tools import WebScraper
from data_analyzer import DataAnalyzer
from file_tools import FileOperations, GitOperations
from document_processor import DocumentProcessor


class AdvancedMCPServer:
    """Advanced MCP Server with extensive AI capabilities"""

    def __init__(self):
        self.server = Server("advanced-ai-framework")

        # Initialize all subsystems
        self.rag = RAGSystem()
        self.code_rag = CodeRAG()
        self.image_gen = ImageGenerator()
        self.image_editor = ImageEditor()
        self.code_exec = CodeExecutor()
        self.web_scraper = WebScraper()
        self.data_analyzer = DataAnalyzer()
        self.file_ops = FileOperations()
        self.git_ops = GitOperations()
        self.doc_processor = DocumentProcessor()

        # Track initialization
        self.subsystems_initialized = False

        self.setup_handlers()

    async def initialize_subsystems(self):
        """Initialize all AI subsystems"""
        if not self.subsystems_initialized:
            print("Initializing AI subsystems...")
            try:
                await self.rag.initialize()
                await self.code_rag.initialize()
                # Image generator initialized on first use (heavy)
                # self.image_gen.initialize()
                self.git_ops.initialize()
                self.subsystems_initialized = True
                print("All subsystems ready!")
            except Exception as e:
                print(f"Warning: Some subsystems failed to initialize: {e}")

    def setup_handlers(self):
        """Setup all tool handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            return [
                # CALCULATOR & WEATHER (Original)
                Tool(
                    name="calculator",
                    description="Perform arithmetic operations (add, subtract, multiply, divide)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["operation", "a", "b"]
                    }
                ),
                Tool(
                    name="weather",
                    description="Get weather information (mock data)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                        },
                        "required": ["city"]
                    }
                ),

                # RAG SYSTEM
                Tool(
                    name="rag_index_document",
                    description="Index a document (PDF, DOCX, TXT, code) into RAG system for Q&A",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to document file"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="rag_index_directory",
                    description="Index all documents in a directory for RAG",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string"},
                            "recursive": {"type": "boolean", "default": True}
                        },
                        "required": ["directory"]
                    }
                ),
                Tool(
                    name="rag_query",
                    description="Query the RAG system to find relevant information from indexed documents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "k": {"type": "number", "default": 5, "description": "Number of results"}
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="rag_stats",
                    description="Get RAG system statistics",
                    inputSchema={"type": "object", "properties": {}}
                ),

                # CODE RAG
                Tool(
                    name="code_analyze_repository",
                    description="Analyze and index entire code repository for semantic code search",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_path": {"type": "string"}
                        },
                        "required": ["repo_path"]
                    }
                ),
                Tool(
                    name="code_find_function",
                    description="Find function definition in indexed code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "function_name": {"type": "string"}
                        },
                        "required": ["function_name"]
                    }
                ),
                Tool(
                    name="code_find_similar",
                    description="Find similar code patterns in repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code_snippet": {"type": "string"}
                        },
                        "required": ["code_snippet"]
                    }
                ),

                # IMAGE GENERATION
                Tool(
                    name="generate_image",
                    description="Generate image from text prompt using Stable Diffusion",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Describe the image to generate"},
                            "negative_prompt": {"type": "string", "description": "What to avoid"},
                            "width": {"type": "number", "default": 512},
                            "height": {"type": "number", "default": 512},
                            "steps": {"type": "number", "default": 25}
                        },
                        "required": ["prompt"]
                    }
                ),
                Tool(
                    name="generate_image_variations",
                    description="Generate multiple variations of an image",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "num_variations": {"type": "number", "default": 4}
                        },
                        "required": ["prompt"]
                    }
                ),

                # CODE EXECUTION
                Tool(
                    name="execute_code",
                    description="Execute Python code safely in sandbox",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Python code to execute"}
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="analyze_code",
                    description="Analyze Python code structure without executing",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="format_code",
                    description="Format Python code using black",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                ),

                # WEB SCRAPING
                Tool(
                    name="web_extract_text",
                    description="Extract readable text from webpage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="web_extract_links",
                    description="Extract all links from webpage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="web_search_in_page",
                    description="Search for keyword in webpage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "keyword": {"type": "string"}
                        },
                        "required": ["url", "keyword"]
                    }
                ),
                Tool(
                    name="web_download_file",
                    description="Download file from URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"}
                        },
                        "required": ["url"]
                    }
                ),

                # DATA ANALYSIS
                Tool(
                    name="data_load_csv",
                    description="Load CSV file for analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "name": {"type": "string", "description": "Optional name for dataset"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="data_get_summary",
                    description="Get statistical summary of dataset",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "df_name": {"type": "string", "description": "Name of loaded dataset"}
                        },
                        "required": ["df_name"]
                    }
                ),
                Tool(
                    name="data_query",
                    description="Query dataset using pandas syntax",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "df_name": {"type": "string"},
                            "query": {"type": "string", "description": "Pandas query (e.g., 'age > 30')"}
                        },
                        "required": ["df_name", "query"]
                    }
                ),
                Tool(
                    name="data_create_chart",
                    description="Create data visualization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "df_name": {"type": "string"},
                            "chart_type": {"type": "string", "enum": ["bar", "line", "scatter", "histogram", "heatmap"]},
                            "x": {"type": "string"},
                            "y": {"type": "string"}
                        },
                        "required": ["df_name", "chart_type"]
                    }
                ),

                # FILE OPERATIONS
                Tool(
                    name="file_read",
                    description="Read file contents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"}
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="file_write",
                    description="Write content to file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string"}
                        },
                        "required": ["file_path", "content"]
                    }
                ),
                Tool(
                    name="file_list_directory",
                    description="List directory contents",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string", "default": "."},
                            "recursive": {"type": "boolean", "default": False},
                            "pattern": {"type": "string", "description": "Glob pattern like '*.py'"}
                        }
                    }
                ),
                Tool(
                    name="file_search",
                    description="Search for files matching pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {"type": "string"},
                            "pattern": {"type": "string", "description": "Glob pattern like '**/*.py'"}
                        },
                        "required": ["directory", "pattern"]
                    }
                ),

                # GIT OPERATIONS
                Tool(
                    name="git_status",
                    description="Get git repository status",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="git_log",
                    description="Get git commit history",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_count": {"type": "number", "default": 10}
                        }
                    }
                ),
                Tool(
                    name="git_diff",
                    description="Get current git diff",
                    inputSchema={"type": "object", "properties": {}}
                ),

                # DOCUMENT PROCESSING
                Tool(
                    name="process_pdf",
                    description="Extract text from PDF file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pdf_path": {"type": "string"}
                        },
                        "required": ["pdf_path"]
                    }
                ),
                Tool(
                    name="summarize_document",
                    description="Create summary of document",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "max_length": {"type": "number", "default": 500}
                        },
                        "required": ["file_path"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle all tool calls"""

            # Ensure subsystems are initialized
            if not self.subsystems_initialized:
                await self.initialize_subsystems()

            # Original tools
            if name == "calculator":
                return await self.calculator_tool(arguments)
            elif name == "weather":
                return await self.weather_tool(arguments)

            # RAG tools
            elif name == "rag_index_document":
                result = await self.rag.index_document(arguments["file_path"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "rag_index_directory":
                result = await self.rag.index_directory(
                    arguments["directory"],
                    arguments.get("recursive", True)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "rag_query":
                result = await self.rag.query(
                    arguments["question"],
                    arguments.get("k", 5)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "rag_stats":
                result = self.rag.get_stats()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Code RAG tools
            elif name == "code_analyze_repository":
                result = await self.code_rag.analyze_repository(arguments["repo_path"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "code_find_function":
                result = await self.code_rag.find_function(arguments["function_name"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "code_find_similar":
                result = await self.code_rag.find_similar_code(arguments["code_snippet"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Image generation tools
            elif name == "generate_image":
                # Initialize on first use
                if not self.image_gen.initialized:
                    self.image_gen.initialize()

                result = self.image_gen.generate_image(
                    prompt=arguments["prompt"],
                    negative_prompt=arguments.get("negative_prompt"),
                    width=arguments.get("width", 512),
                    height=arguments.get("height", 512),
                    num_inference_steps=arguments.get("steps", 25)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "generate_image_variations":
                if not self.image_gen.initialized:
                    self.image_gen.initialize()

                result = self.image_gen.generate_variations(
                    prompt=arguments["prompt"],
                    num_variations=arguments.get("num_variations", 4)
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Code execution tools
            elif name == "execute_code":
                result = self.code_exec.execute_code(arguments["code"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "analyze_code":
                result = self.code_exec.analyze_code(arguments["code"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "format_code":
                result = self.code_exec.format_code(arguments["code"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Web scraping tools
            elif name == "web_extract_text":
                result = await self.web_scraper.extract_text(arguments["url"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "web_extract_links":
                result = await self.web_scraper.extract_links(arguments["url"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "web_search_in_page":
                result = await self.web_scraper.search_in_page(
                    arguments["url"],
                    arguments["keyword"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "web_download_file":
                result = await self.web_scraper.download_file(arguments["url"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Data analysis tools
            elif name == "data_load_csv":
                result = self.data_analyzer.load_csv(
                    arguments["file_path"],
                    arguments.get("name")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "data_get_summary":
                result = self.data_analyzer.get_summary(arguments["df_name"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "data_query":
                result = self.data_analyzer.query_data(
                    arguments["df_name"],
                    arguments["query"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "data_create_chart":
                result = self.data_analyzer.create_visualization(
                    arguments["df_name"],
                    arguments["chart_type"],
                    arguments.get("x"),
                    arguments.get("y")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # File operations
            elif name == "file_read":
                result = self.file_ops.read_file(arguments["file_path"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "file_write":
                result = self.file_ops.write_file(
                    arguments["file_path"],
                    arguments["content"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "file_list_directory":
                result = self.file_ops.list_directory(
                    arguments.get("directory", "."),
                    arguments.get("recursive", False),
                    arguments.get("pattern")
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "file_search":
                result = self.file_ops.search_files(
                    arguments["directory"],
                    arguments["pattern"]
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Git operations
            elif name == "git_status":
                result = self.git_ops.get_status()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "git_log":
                result = self.git_ops.get_log(arguments.get("max_count", 10))
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "git_diff":
                result = self.git_ops.get_diff()
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            # Document processing
            elif name == "process_pdf":
                result = self.doc_processor.process_pdf(arguments["pdf_path"])
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "summarize_document":
                # First process the document
                file_path = arguments["file_path"]
                if file_path.endswith('.pdf'):
                    doc_data = self.doc_processor.process_pdf(file_path)
                else:
                    doc_data = self.doc_processor.process_text_file(file_path)

                if 'error' in doc_data:
                    return [TextContent(type="text", text=json.dumps(doc_data, indent=2))]

                summary = self.doc_processor.summarize_document(
                    doc_data['text'],
                    arguments.get('max_length', 500)
                )

                result = {
                    'file_path': file_path,
                    'summary': summary,
                    'original_length': len(doc_data['text']),
                    'summary_length': len(summary)
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            else:
                raise ValueError(f"Unknown tool: {name}")

    # Original tool implementations
    async def calculator_tool(self, arguments: dict) -> list[TextContent]:
        """Calculator tool (from original)"""
        operation = arguments.get("operation")
        a = arguments.get("a")
        b = arguments.get("b")

        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return [TextContent(type="text", text="Error: Division by zero")]
                result = a / b
            else:
                return [TextContent(type="text", text=f"Error: Unknown operation '{operation}'")]

            return [TextContent(type="text", text=f"Result: {a} {operation} {b} = {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def weather_tool(self, arguments: dict) -> list[TextContent]:
        """Weather tool (from original)"""
        import random

        city = arguments.get("city", "Unknown")
        units = arguments.get("units", "celsius")

        temp_celsius = random.randint(10, 30)
        temp_fahrenheit = (temp_celsius * 9/5) + 32

        conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Overcast"]
        condition = random.choice(conditions)

        temp = temp_celsius if units == "celsius" else temp_fahrenheit
        temp_unit = "°C" if units == "celsius" else "°F"

        weather_info = f"""Weather in {city}:
Temperature: {temp:.1f}{temp_unit}
Condition: {condition}
Humidity: {random.randint(30, 80)}%
Wind Speed: {random.randint(5, 25)} km/h

Note: This is mock data for demonstration."""

        return [TextContent(type="text", text=weather_info)]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = AdvancedMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
