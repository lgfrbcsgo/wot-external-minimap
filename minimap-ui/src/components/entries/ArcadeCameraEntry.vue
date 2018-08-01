<template>
    <circle v-if="entry.active" :cx="position[0]" :cy="position[1]" r="15" stroke="black" stroke-width="2" fill="white"/>
</template>

<script lang="ts">
    import {Component, Prop} from 'vue-property-decorator';
    import BaseEntry from "./BaseEntry";

    @Component
    export default class ArcadeCameraEntry extends BaseEntry {}
</script>