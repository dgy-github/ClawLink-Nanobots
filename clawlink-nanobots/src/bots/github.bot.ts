import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const GitHubBot: Nanobot = {
    name: "github_submit",
    description: "Autonomously commit and push the current project to GitHub via OpenClaw.",
    inputSchema: {
        type: "object",
        properties: { 
            message: { type: "string" }
        },
        required: ["message"]
    },
    execute: async (args: { message: string }) => {
        console.log(`[GitHubBot] Staging changes...`);
        await openClawClient.invokeTool('exec', { command: 'git add .' });
        
        console.log(`[GitHubBot] Committing: ${args.message}`);
        await openClawClient.invokeTool('exec', { command: `git commit -m "${args.message.replace(/"/g, '\\"')}"` });
        
        console.log(`[GitHubBot] Pushing to remote...`);
        const result = await openClawClient.invokeTool('exec', { command: 'git push origin main' });
        
        return { success: true, result };
    }
};

registry.register(GitHubBot);
export default GitHubBot;
