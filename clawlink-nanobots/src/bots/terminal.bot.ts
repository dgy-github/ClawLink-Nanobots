import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const TerminalBot: Nanobot = {
    name: "shell_command",
    description: "Run a shell command on the local system via OpenClaw execution engine.",
    inputSchema: {
        type: "object",
        properties: {
            command: { type: "string" },
            cwd: { type: "string" }
        },
        required: ["command"]
    },
    execute: async (args: { command: string, cwd?: string }) => {
        console.log(`[TerminalBot] Running: ${args.command}`);
        return await openClawClient.invokeTool('exec', args);
    }
};

registry.register(TerminalBot);
export default TerminalBot;
