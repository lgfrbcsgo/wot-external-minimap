<template>
    <circle v-if="entry.active" :cx="position[0]" :cy="position[1]" r="15" stroke="black" stroke-width="2"
            :fill="color"/>
</template>

<script lang="ts">
    import {Component, Prop} from 'vue-property-decorator';
    import BaseEntry from "./BaseEntry";
    import {VehicleEntry as VehicleEntry_} from "../../model/symbols";

    @Component
    export default class VehicleEntry extends BaseEntry {
        @Prop({required: true}) entry!: VehicleEntry_;

        get color(): string {
            switch (this.entry.team) {
                case 'ally':
                    return 'green';
                case 'squadman':
                    return 'orange';
                default:
                    return this.entry.spotted ? 'red' : 'grey';
            }
        }
    }
</script>