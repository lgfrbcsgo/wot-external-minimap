<template>
    <svg viewBox="0 0 1000 1000">
        <image :xlink:href="texture" x="0" y="0" height="100%" width="100%"/>
        <component :is="entry.symbol" v-for="entry in entries" :key="entry.id" :entry="entry"></component>
    </svg>
</template>

<script lang="ts">
    import {Component, Vue} from 'vue-property-decorator';
    import miniMapConnector from '../services/mini-map-connector';
    import VehicleEntry from "./entries/VehicleEntry.vue";
    import ArcadeCameraEntry from "./entries/ArcadeCameraEntry.vue";
    import {MiniMapEntry} from "../model/symbols";

    @Component({
        components: {VehicleEntry, ArcadeCameraEntry}
    })
    export default class MiniMap extends Vue {
        get entries(): MiniMapEntry[] {
            return this.$store.state.miniMapEntries;
        }

        get texture(): string {
            return `/minimap/vanilla/${this.$store.state.arena.texture}.png`;
        }

        async created () {
            await miniMapConnector.connect('ws://localhost:13371');
        }

        async beforeDestroy () {
            await miniMapConnector.disconnect();
        }
    }
</script>