

export const getInt = (val: string, e: string) => {
    var index = e.search(val);
    if (index != -1) {
        var substring = e.substring(index, e.length);
        var endOfLineChar = '\n';
        var endIndex = substring.indexOf(endOfLineChar);
        if (endIndex != -1) {
            return +(substring.substring(val.length + 1, endIndex)); //string is converted to int with unary + operator
        } else {
            return -1;
        }
    } else {
        return -1;
    }
}

export const checkBoolLabel = (val: string) => {
    switch ((val as string).toLowerCase().trim()) {
        case "yes":
        case "true":
        case "1":
        case "on":
            return true;
        case "no":
        case "false":
        case "0":
        case "off":
            return false;
        default:
            return false;
    }
}

export const getBool = (val: string, e: string) => {
    var index = e.search(val);
    if (index != -1) {
        var substring = e.substring(index, e.length);
        var endOfLineChar = '\n';
        var endIndex = substring.indexOf(endOfLineChar);
        if (endIndex != -1 && checkBoolLabel(substring.substring(val.length + 1, endIndex))) {
            return true;
        } else {
            return false;
        }
    } else {
        return false;
    }
}

export const getString = (val: string, e: string) => {
    var index = e.search(val);
    if (index != -1) {
        var substring = e.substring(index, e.length);
        var endOfLineChar = '\n';
        var endIndex = substring.indexOf(endOfLineChar);
        if (endIndex != -1) {
            return substring.substring(val.length + 1, endIndex);
        } else {
            return "";
        }
    } else {
        return "";
    }
}


export const getSubstringAfter = (val: string, e: string) => {
    var index = e.search(val);
    if (index != -1) {
        return e.substring(index + val.length);
    } else {
        return e;
    }
}

export const getLiftPlan = (e: string, wefts: number): Array<Array<number>> => {
    const treadling: Array<Array<number>> = [];
    for (let i = 0; i < wefts; i++) {
        treadling.push([]);
    }

    var indexOfLabel = e.search("LIFTPLAN]");
    var startIndex = indexOfLabel + "LIFTPLAN]".length + 1;
    var endOfLineChar = '\n';
    var endIndex = (e.substring(startIndex)).indexOf(endOfLineChar) + startIndex;
    var line = e.substring(startIndex, endIndex);

    while (line.match(/[0-9]*=[0-9]*/) != null) {
        var weft = +(line.match(/[0-9]*/) ?? 0);
        var all_treadles = (line.match(/=[0-9]*/)?.[0]?.substring(1) ?? '');
        var treadle_list = all_treadles.split(',');
        for (let i = 0; i < treadle_list.length; i++) {
            if (+(treadle_list[i]) > 0) {
                treadling[weft - 1].push(+(treadle_list[i]) - 1);
            }
        }
        startIndex = endIndex + 1;
        endIndex = e.substring(startIndex).indexOf(endOfLineChar) + startIndex;
        line = e.substring(startIndex, endIndex);
    }

    return treadling;
}


//**UPATE THIS */
export const getTreadling = (e: string, wefts: number): Array<Array<number>> => {
    const treadling: Array<Array<number>> = [];
    const treadles = getInt("Treadles", e);
    for (let i = 0; i < wefts; i++) {
        treadling.push([]);
    }

    var indexOfLabel = e.search("TREADLING]");
    var startIndex = indexOfLabel + "TREADLING]".length + 1;
    var endOfLineChar = '\n';
    var endIndex = (e.substring(startIndex)).indexOf(endOfLineChar) + startIndex;
    var line = e.substring(startIndex, endIndex);

    while (line.match(/[0-9]*=[0-9]*/) != null) {
        var weft = +(line.match(/[0-9]*/) ?? 0);
        var all_treadles = (line.match(/=[0-9]*/)?.[0]?.substring(1) ?? '');
        var treadle_list = all_treadles.split(',');
        for (let i = 0; i < treadle_list.length; i++) {
            if (+(treadle_list[i]) > 0) {
                treadling[weft - 1].push(+(treadle_list[i]) - 1);
            }
        }
        startIndex = endIndex + 1;
        endIndex = e.substring(startIndex).indexOf(endOfLineChar) + startIndex;
        line = e.substring(startIndex, endIndex);
    }

    return treadling;
}

export const getThreading = (e: string, warps: number): Array<number> => {
    const threading: Array<number> = [];
    for (let i = 0; i < warps; i++) {
        threading.push(-1);
    }

    var indexOfLabel = e.search("THREADING]");
    var startIndex = indexOfLabel + "THREADING]".length + 1;
    var endOfLineChar = '\n';
    var endIndex = (e.substring(startIndex)).indexOf(endOfLineChar) + startIndex;

    var line = e.substring(startIndex, endIndex);
    while (line.match(/[0-9]*=[0-9]*/) != null) {
        var warp = +(line.match(/[0-9]*/) ?? 0);
        var frame = +(line.match(/=[0-9]*/)?.[0]?.substring(1) ?? 0);
        threading[warps - warp] = frame - 1;
        startIndex = endIndex + 1;
        endIndex = e.substring(startIndex).indexOf(endOfLineChar) + startIndex;
        line = e.substring(startIndex, endIndex);
    }

    return threading;
}

export const getTieups = (e: string, frames: number, treadles: number): Array<Array<boolean>> => {
    const tieups: Array<Array<boolean>> = [];

    for (let i = 0; i < frames; i++) {
        tieups.push(Array(treadles).fill(false));
    }

    var indexOfLabel = e.search("TIEUP]");
    var startIndex = indexOfLabel + "TIEUP]".length + 1;
    var endOfLineChar = '\n';
    var endIndex = (e.substring(startIndex)).indexOf(endOfLineChar) + startIndex;
    var line = e.substring(startIndex, endIndex);

    while (line.match(/[0-9]*=[0-9]*/) != null) {
        var treadle = +(line.match(/[0-9]*/) ?? 0);
        var firstFrame = +(line.match(/=[0-9]*/)?.[0]?.substring(1) ?? 0);
        tieups[firstFrame - 1][treadle - 1] = true;
        var restOfFrames = line.match(/,[0-9]/g);
        if (restOfFrames != null) {
            for (var i = 0; i < restOfFrames.length; i++) {
                var currentFrame = +(restOfFrames[i].substring(1));
                tieups[currentFrame - 1][treadle - 1] = true;
            }
        }
        startIndex = endIndex + 1;
        endIndex = e.substring(startIndex).indexOf(endOfLineChar) + startIndex;
        line = e.substring(startIndex, endIndex);
    }

    return tieups;
}

