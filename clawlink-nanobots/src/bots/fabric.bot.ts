import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const FabricBot: Nanobot = {
    name: "fabric_pattern",
    description: "Run a Fabric AI pattern via the local RAG engine.",
    inputSchema: {
        type: "object",
        properties: { 
            pattern: { type: "string" },
            input: { type: "string" }
        },
        required: ["pattern", "input"]
    },
    execute: async (args: { pattern: string, input: string }) => {
        return await openClawClient.invokeTool('exec', { 
            command: `echo "${args.input.replace(/"/g, '\\"')}" | fabric --pattern ${args.pattern}` 
        });
    }
};

registry.register(FabricBot);
export default FabricBot;
