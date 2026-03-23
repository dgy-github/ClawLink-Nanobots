import { registry, Nanobot } from "../registry.js";
import { openClawClient } from "../openclaw-client.js";

const NotifyBot: Nanobot = {
    name: "local_notify",
    description: "Send a native desktop notification and/or voice summary.",
    inputSchema: {
        type: "object",
        properties: { 
            title: { type: "string" },
            message: { type: "string" },
            speak: { type: "boolean" }
        },
        required: ["message"]
    },
    execute: async (args: { title?: string, message: string, speak?: boolean }) => {
        if (args.title) {
            await openClawClient.invokeTool('nodes', { 
                action: 'notify',
                title: args.title,
                message: args.message
            });
        }
        if (args.speak) {
            await openClawClient.invokeTool('exec', { 
                command: `PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${args.message.replace(/'/g, "''")}')"`
            });
        }
        return { success: true };
    }
};

registry.register(NotifyBot);
export default NotifyBot;
