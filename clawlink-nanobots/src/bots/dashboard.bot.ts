import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const DashboardBot: Nanobot = {
    name: "dashboard_update",
    description: "Update the local desktop status dashboard (Canvas A2UI).",
    inputSchema: {
        type: "object",
        properties: { 
            text: { type: "string" },
            progress: { type: "number" }
        },
        required: ["text"]
    },
    execute: async (args: { text: string, progress?: number }) => {
        const bar = args.progress ? ` [${'#'.repeat(Math.floor(args.progress/10))}${' '.repeat(10-Math.floor(args.progress/10))}]` : '';
        return await openClawClient.invokeTool('canvas', { 
            action: 'a2ui_push',
            text: `${args.text}${bar}`
        });
    }
};

registry.register(DashboardBot);
export default DashboardBot;
