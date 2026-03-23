import fs from 'fs';
import path from 'path';
import os from 'os';

export class OpenClawClient {
    private baseUrl: string = 'http://127.0.0.1:18789';
    private token: string = '';

    async init() {
        const configPath = path.join(os.homedir(), '.openclaw', 'openclaw.json');
        if (fs.existsSync(configPath)) {
            try {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                if (config.gateway?.auth?.token) {
                    this.token = config.gateway.auth.token;
                }
            } catch (e) {
                console.error("Failed to load OpenClaw config:", e);
            }
        }
    }

    async invokeTool(tool: string, args: any = {}) {
        const response = await fetch(`${this.baseUrl}/tools/invoke`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tool, args })
        });

        if (!response.ok) {
            const err = await response.text();
            throw new Error(`OpenClaw Error (${response.status}): ${err}`);
        }

        return await response.json();
    }
}

export const openClawClient = new OpenClawClient();
