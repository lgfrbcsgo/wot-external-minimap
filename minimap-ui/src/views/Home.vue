<template>
    <MiniMap msg="Welcome to Your Vue.js + TypeScript App"/>
</template>

<script lang="ts">
    import {Component, Vue} from 'vue-property-decorator';
    import MiniMap from '../components/MiniMap.vue';

    @Component({
        components: {
            MiniMap,
        },
    })
    export default class Home extends Vue {

    }
</script>
