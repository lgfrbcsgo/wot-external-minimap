import {MiniMapEntry} from "@/model/symbols";
import {Arena} from "@/model/arena";
import {Invocation} from "@/model/invocation";

export interface MiniMapData {
    arena: Arena
    entries: MiniMapEntry[]
    events: Invocation[]
}