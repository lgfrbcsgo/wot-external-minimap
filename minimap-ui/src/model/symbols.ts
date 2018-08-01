import {Vector2, Vector3} from "@/model/common";

export interface MiniMapSymbol {
    id: number
    active: boolean
    position: Vector3 | null
    orientation: Vector3 | null
    symbol: string
    container: string
}

export interface ArcadeCameraEntry extends MiniMapSymbol {
    showDirectionLine: boolean
}

export interface ViewRangeCirclesEntry extends MiniMapSymbol {
    arenaSize: Vector2
    showMaxRenderRange: boolean
    maxRenderRange: number
    showMaxViewRange: boolean
    maxViewRange: number
    showViewRange: boolean
    viewRange: number
}

export interface TeamBaseEntry extends MiniMapSymbol {
    number: number
}

export interface VehicleEntry extends MiniMapSymbol {
    playerID: number
    type: string
    name: string
    team: string
    spotted: boolean
    alive: boolean
}

export type MiniMapEntry = MiniMapSymbol | ArcadeCameraEntry | ViewRangeCirclesEntry | TeamBaseEntry | VehicleEntry