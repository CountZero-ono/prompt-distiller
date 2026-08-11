#!/usr/bin/env python3
"""
Model Context Protocol (MCP) Server for Prompt Distiller.
Exposes 'distill_prompt' tool over stdio JSON-RPC protocol for Antigravity & Hermes agents.
"""

import sys
import os
import json
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.distiller import PromptDistiller

root_logger = logging.getLogger()
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

class PromptDistillerMCPServer:
    def __init__(self):
        import yaml
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
        config = {}
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f)
        self.distiller = PromptDistiller(config)

    async def handle_request(self, request: dict) -> dict:
        method = request.get("method")
        req_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "prompt-distiller-mcp",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "distill_prompt",
                            "description": "Distills messy, rambling, emotional, or STT-dictated prompts (in Russian or any language) into a high-potency, concise English prompt, saving 50-75% token context.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "raw_prompt": {
                                        "type": "string",
                                        "description": "The raw dictated or written prompt text to distill."
                                    }
                                },
                                "required": ["raw_prompt"]
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            name = params.get("name")
            args = params.get("arguments", {})

            if name == "distill_prompt":
                raw_prompt = args.get("raw_prompt", "")
                res = await self.distiller.distill_only(raw_prompt)
                distilled = res.get("distilled_prompt", raw_prompt)
                savings = res.get("token_savings_percent", 0)
                summary = res.get("raw_input_summary", "")

                output_text = f"Distilled Prompt:\n{distilled}\n\nToken Savings: {savings}%\nSummary: {summary}"

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": output_text
                            }
                        ]
                    }
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method/tool {name} not found"}
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method {method} not found"}
            }

async def main():
    server = PromptDistillerMCPServer()
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            response = await server.handle_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"MCP Server Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
