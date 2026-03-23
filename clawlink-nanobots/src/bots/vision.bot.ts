import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const VisionBot: Nanobot = {
    name: "capture_screen",
    description: "Capture a screenshot of the local desktop via OpenClaw node sensors.",
    inputSchema: { type: "object", properties: {} },
    execute: async () => {
        console.log(`[VisionBot] Triggering capture...`);
        const status = await openClawClient.invokeTool('nodes', { action: 'status' });
        const node = status.nodes?.[0]?.id || 'local';
        return await openClawClient.invokeTool('nodes', { action: 'camera_snap', node });
    }
};

registry.register(VisionBot);
export default VisionBot;
