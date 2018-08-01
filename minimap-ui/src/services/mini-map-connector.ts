import Vue from 'vue';
import store from '../store';
import {UPDATE_ARENA, UPDATE_MINI_MAP_ENTRIES} from "@/store";
import {MiniMapData} from "@/model/payloads";

export const INVOKATION = 'invokation';

class MiniMapConnector {
    private websocket: WebSocket | undefined;

    public miniMapEvents = new Vue();

    constructor() {
    }

    connect(websocketURL: string): Promise<void> {
        return this.disconnect().then(() => {
            return new Promise<void>((resolve, reject) => {
                const socket = this.websocket = new WebSocket(websocketURL);
                socket.onmessage = event => this.onMessage(event);
                socket.onerror = error => reject(error);
                socket.onopen = () => {
                    socket.onerror = null;
                    resolve();
                }
            })
        });
    }

    disconnect(): Promise<void> {
        return new Promise<void>(resolve => {
            if (!this.websocket) {
                return resolve();
            }
            this.websocket.onclose = () => resolve();
            this.websocket.close();
        });
    }

    private onMessage(event: MessageEvent) {
        const data: MiniMapData = JSON.parse(event.data);
        store.commit(UPDATE_ARENA, data.arena);
        store.commit(UPDATE_MINI_MAP_ENTRIES, data.entries);
        Vue.nextTick().then(() => {
            data.events.forEach(event => this.miniMapEvents.$emit(INVOKATION, event))
        });
    }
}

export default new MiniMapConnector();

