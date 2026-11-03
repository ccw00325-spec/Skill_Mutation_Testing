import { readFileSync } from "node:fs";

const [reportPath, scopePath] = process.argv.slice(2);
if (!reportPath || !scopePath) {
  console.error("Usage: node feedback.mjs <stryker-report.json> <scope.json>");
  process.exit(2);
}

const report = JSON.parse(readFileSync(reportPath, "utf8"));
const scope = JSON.parse(readFileSync(scopePath, "utf8"));
if (!Array.isArray(scope.targets) || !report.files || typeof report.files !== "object") {
  throw new Error("Expected a Stryker JSON report and explicit target list");
}

const counts = {};
const gaps = [];
const missingTargets = [];
for (const file of new Set(scope.targets)) {
  const mutants = Object.hasOwn(report.files, file) ? report.files[file].mutants : null;
  if (!Array.isArray(mutants)) {
    missingTargets.push(file);
    continue;
  }
  for (const mutant of mutants) {
    const status = mutant.status;
    if (typeof status !== "string" || !/^[A-Za-z]+$/.test(status)) throw new Error(`Invalid mutant status in ${file}`);
    counts[status] = (counts[status] ?? 0) + 1;
    if (status === "Survived" || status === "NoCoverage") {
      gaps.push({ file, line: mutant.location?.start?.line, id: mutant.id, operator: mutant.mutatorName, replacement: mutant.replacement, status });
    }
  }
}
console.log(JSON.stringify({ counts, gaps, missingTargets }, null, 2));
