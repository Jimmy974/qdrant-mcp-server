#!/usr/bin/env python3
import logging
from fastmcp import FastMCP
from .tools.vector import VectorTools
from .tools.point import PointTools
from .tools.text import TextTools

class QdrantMCPServer:
    def __init__(self):
        self.name = "qdrant_mcp_server"
        self.mcp = FastMCP(self.name)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)
        
        # Initialize tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        # Initialize tool classes
        vector_tools = VectorTools(self.logger)
        point_tools = PointTools(self.logger)
        text_tools = TextTools(self.logger)
        
        # Register tools from each module
        vector_tools.register_tools(self.mcp)
        point_tools.register_tools(self.mcp)
        text_tools.register_tools(self.mcp)

    def run(self):
        """Run the MCP server."""
        self.mcp.run()

def main():
    server = QdrantMCPServer()
    server.run() 