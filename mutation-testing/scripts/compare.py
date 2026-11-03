"""Compare two scoped mutation reports from one module and one tool."""
import argparse
from collections import Counter
import json
from pathlib import Path
import xml.etree.ElementTree as ET

STATUS = {
    "KILLED": "Killed", "SURVIVED": "Survived", "NOCOVERAGE": "NoCoverage",
    "TIMEOUT": "Timeout", "TIMEDOUT": "Timeout", "COMPILEERROR": "CompileError",
    "RUNTIMEERROR": "RuntimeError", "RUNERROR": "RunError", "MEMORYERROR": "MemoryError",
}


def read_report(path, tool, targets):
    records, sources = {}, {}
    seen = set()

    def add(key, status, tests):
        if key in records or not status:
            raise ValueError(f"Duplicate mutation identity or missing status: {key}")
        records[key] = {
            "status": STATUS.get(status.replace("_", "").upper(), status),
            "rawStatus": status,
            "killingTests": tests,
        }

    if tool == "stryker":
        report = json.loads(path.read_text(encoding="utf-8-sig"))
        for file, data in report["files"].items():
            if file not in targets:
                continue
            seen.add(file)
            sources[file] = data.get("source")
            for mutant in data["mutants"]:
                location = mutant["location"]
                key = (file, location["start"]["line"], location["start"]["column"],
                       location["end"]["line"], location["end"]["column"],
                       mutant["mutatorName"], mutant["replacement"])
                add(key, mutant["status"], mutant.get("killedBy", []))
    else:
        xml = path.read_bytes()
        if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
            raise ValueError("Use a PIT XML report without DTD or entity declarations")
        root = ET.fromstring(xml)
        if root.tag != "mutations":
            raise ValueError("Expected PIT mutations XML")
        for mutant in root.findall("mutation"):
            cls = mutant.findtext("mutatedClass")
            if cls not in targets:
                continue
            seen.add(cls)
            indexes = tuple(node.text for node in mutant.findall("indexes/index"))
            if not indexes:
                raise ValueError(f"No bytecode indexes for PIT mutant in {cls}")
            key = (cls, mutant.findtext("mutatedMethod"), mutant.findtext("methodDescription"),
                   mutant.findtext("mutator"), indexes)
            if any(value is None for value in key):
                raise ValueError(f"Incomplete PIT mutant identity in {cls}")
            test = mutant.findtext("killingTest")
            add(key, mutant.get("status"), [test] if test else [])
    return records, targets - seen, sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=["stryker", "pit"])
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("targets", nargs="+", help="Exact report paths or JVM class names")
    args = parser.parse_args()
    targets = set(args.targets)
    try:
        before, missing_before, source_before = read_report(args.before, args.tool, targets)
        after, missing_after, source_after = read_report(args.after, args.tool, targets)
        for file in source_before.keys() & source_after.keys():
            if source_before[file] != source_after[file]:
                raise ValueError(f"Source differs across reports: {file}")
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        parser.exit(2, f"Cannot compare reports: {exc}\n")

    transitions = []
    for key in sorted(before.keys() & after.keys()):
        if before[key]["status"] != after[key]["status"]:
            transitions.append({"identity": key, "before": before[key], "after": after[key]})
    complete = bool(before and after) and not (
        missing_before or missing_after or before.keys() != after.keys()
    )
    print(json.dumps({
        "tool": args.tool,
        "before": dict(Counter(row["status"] for row in before.values())),
        "after": dict(Counter(row["status"] for row in after.values())),
        "transitions": transitions,
        "missingBefore": sorted(missing_before),
        "missingAfter": sorted(missing_after),
        "onlyBefore": sorted(before.keys() - after.keys()),
        "onlyAfter": sorted(after.keys() - before.keys()),
        "completeMatch": complete,
    }, ensure_ascii=False, indent=2))
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
