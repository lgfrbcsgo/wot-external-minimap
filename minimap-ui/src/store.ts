import Vue from 'vue';
import Vuex from 'vuex';
import {MiniMapEntry} from "./model/symbols";
import {Arena} from "@/model/arena";

Vue.use(Vuex);

export const UPDATE_ARENA = 'updateArena';
export const UPDATE_MINI_MAP_ENTRIES = 'updateMinimapEntries';

export default new Vuex.Store({
    state: {
        arena: {
            name: '',
            size: [1000, 1000],
            texture: ''
        },
        miniMapEntries: Array<MiniMapEntry>()
    },
    mutations: {
        updateArena(state, arena: Arena) {
            state.arena = arena
        },
        updateMinimapEntries(state, entries: MiniMapEntry[]) {
            state.miniMapEntries = entries;
        }
    }
});
