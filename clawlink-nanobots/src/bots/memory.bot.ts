import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const MemoryBot: Nanobot = {
    name: "memory_search",
    description: "Search long-term project memory and cross-agent history.",
    inputSchema: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"]
    },
    execute: async (args: { query: string }) => {
        return await openClawClient.invokeTool('memory_search', args);
    }
};

const MemoryAddBot: Nanobot = {
    name: "memory_add",
    description: "Record a solution, discovery, or pattern into long-term memory.",
    inputSchema: {
        type: "object",
        properties: { 
            text: { type: "string" },
            tags: { type: "array", items: { type: "string" } }
        },
        required: ["text"]
    },
    execute: async (args: { text: string, tags?: string[] }) => {
        return await openClawClient.invokeTool('memory_add', args);
    }
};

registry.register(MemoryBot);
registry.register(MemoryAddBot);
export { MemoryBot, MemoryAddBot };
