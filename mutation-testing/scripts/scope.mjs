import { execFileSync } from "node:child_process";

const [base, ...prefixes] = process.argv.slice(2);
if (!/^[a-f0-9]{7,64}$/i.test(base ?? "") || !prefixes.length ||
    prefixes.some(p => !/^[\w./-]+\/$/.test(p) || p.startsWith("/") || p.split("/").includes(".."))) {
  console.error("Usage: node scope.mjs <base-commit-sha> <domain-directory/> [...]");
  process.exit(2);
}

function git(...args) {
  return execFileSync("git", args, { encoding: "utf8" });
}

const mergeBase = git("merge-base", base, "HEAD").trim();
const changed = git("diff", "--name-only", "-z", "--no-renames", "--diff-filter=ACM", mergeBase, "HEAD", "--")
  .split("\0").filter(Boolean);
const targets = changed.filter(file =>
  prefixes.some(prefix => file.startsWith(prefix)) &&
  /\.(?:[cm]?[jt]s|java|kt)$/i.test(file) &&
  !/(?:^|\/)(?:tests?|__tests__|ui|views?|migrations?|schema|generated|fixtures?)(?:\/|$)|\.(?:test|spec|d)\.[^.]+$/i.test(file) &&
  !/(?:^|\/)[^/]*(?:Test|Tests|Spec)\.(?:java|kt)$/.test(file)
);
console.log(JSON.stringify({ mergeBase, targets, status: targets.length ? "scoped" : "no-targets" }, null, 2));
