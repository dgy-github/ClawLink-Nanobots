import { openClawClient } from "./openclaw-client.js";
import { registry } from "./registry.js";
import "./bots/terminal.bot.js";
import "./bots/vision.bot.js";
import "./bots/memory.bot.js";
import "./bots/fabric.bot.js";
import "./bots/dashboard.bot.js";
import "./bots/notify.bot.js";
import "./bots/github.bot.js";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema, CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

async function main() {
    await openClawClient.init();
    
    const server = new Server(
        { name: "clawlink-nanobots", version: "2.0.0" },
        { capabilities: { tools: {} } }
    );

    server.setRequestHandler(ListToolsRequestSchema, async () => ({
        tools: registry.getTools()
    }));

    server.setRequestHandler(CallToolRequestSchema, async (request) => {
        try {
            const result = await registry.run(request.params.name, request.params.arguments);
            return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } catch (error: any) {
            return {
                content: [{ type: "text", text: `Error: ${error.message}` }],
                isError: true
            };
        }
    });

    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("🚀 ClawLink-Nanobots MCP Server online!");
}

main().catch(console.error);
