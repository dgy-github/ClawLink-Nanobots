import { openClawClient } from "./openclaw-client.js";

/**
 * The Nanobot Interface
 * Each bot defines its tool schema and its internal logic.
 */
export interface Nanobot {
    name: string;
    description: string;
    inputSchema: any;
    execute: (args: any) => Promise<any>;
}

export class NanobotRegistry {
    private bots: Map<string, Nanobot> = new Map();

    register(bot: Nanobot) {
        this.bots.set(bot.name, bot);
        console.log(`[Registry] Registered Bot: ${bot.name}`);
    }

    getTools() {
        return Array.from(this.bots.values()).map(bot => ({
            name: bot.name,
            description: bot.description,
            inputSchema: bot.inputSchema
        }));
    }

    async run(name: string, args: any) {
        const bot = this.bots.get(name);
        if (!bot) throw new Error(`Bot ${name} not found`);
        return await bot.execute(args);
    }
}

export const registry = new NanobotRegistry();
