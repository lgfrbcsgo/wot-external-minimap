import {Prop, Vue} from 'vue-property-decorator';
import {MiniMapEntry} from "@/model/symbols";
import {Vector2} from "@/model/common";

export default class BaseEntry extends Vue {
    @Prop({required: true}) entry!: MiniMapEntry;

    get position(): Vector2 {
        const [width, height] = this.$store.state.arena.size;
        const [x, y, z] = this.entry.position || [0, 0, 0];
        return [width / 2 + x, height / 2 - z].map(n => n * 1000 / Math.max(width, height)) as Vector2;
    }
}