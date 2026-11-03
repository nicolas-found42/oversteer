/** Run the public twelve-tool Jev library over reproducible offline training jobs.
 * No credentials enter jobs/logs. Jev advises; the Python pipeline owns decisions.
 */
import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";

process.env.JEV_PROVIDER = "openrouter";
process.env.JEV_MCP_MODEL = "typesafe/jev-1.14";

const capabilities = ["screen", "verify", "find", "rerank", "classify", "decide", "compare",
  "extract", "audit", "review", "gate", "noul"].map(name => "jev_" + name);
const jobsPath = resolve(process.argv[2] ?? "artifacts/carmodels-research/jev-jobs.json");
const output = resolve(process.argv[3] ?? "artifacts/carmodels-research/jev-workflow");
const budgetPath = resolve("artifacts/carmodels-research/jev-budget.json");
const jobs = JSON.parse(await readFile(jobsPath, "utf8"));
await mkdir(output, { recursive: true });
await mkdir(dirname(budgetPath), { recursive: true });

// The MCP library reports tokens but discards upstream dollar cost. Reserve $0.02
// per call, above a full 262144-token request at the verified $0.042/M input rate.
// The starting reserve covers earlier raw-API experiments and MCP screening.
let budget;
try { budget = JSON.parse(await readFile(budgetPath, "utf8")); }
catch (error) {
  if (error.code !== "ENOENT") throw error;
  budget = { cap_usd: 5, reserved_usd: 0.65, per_call_reserve_usd: 0.02, calls: [] };
}

const { createServer } = await import("@jkudish/jev-mcp");
const { Client, InMemoryTransport } = await import("@modelcontextprotocol/client");
const server = createServer();
const client = new Client({ name: "oversteer-carmodels", version: "1" });
const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
let results;
try { results = JSON.parse(await readFile(join(output, "results.json"), "utf8")); }
catch (error) {
  if (error.code !== "ENOENT") throw error;
  results = [];
}
try {
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)]);
  const offered = new Set((await client.listTools()).tools.map(tool => tool.name));
  if (!capabilities.every(name => offered.has(name))) throw new Error("Incomplete Jev capability set");
  for (const job of jobs) {
    if (!capabilities.includes(job.tool) || !/^[a-z0-9_-]+$/.test(job.id))
      throw new Error("Invalid judgment job");
    const request = { name: job.tool, arguments: job.arguments };
    const hash = createHash("sha256").update(JSON.stringify(request)).digest("hex").slice(0, 16);
    const prefix = join(output, job.id + "-" + hash);
    let result;
    try { result = JSON.parse(await readFile(prefix + ".response.json", "utf8")); }
    catch (error) {
      if (error.code !== "ENOENT") throw error;
      if (budget.reserved_usd + budget.per_call_reserve_usd > budget.cap_usd)
        throw new Error("Jev experiment budget exhausted");
      // Reserve before sending: even a timeout or malformed answer may have incurred cost.
      budget.reserved_usd += budget.per_call_reserve_usd;
      const accounting = { id: job.id, tool: job.tool, request_hash: hash,
        reserve_usd: budget.per_call_reserve_usd, status: "started" };
      budget.calls.push(accounting);
      await writeFile(budgetPath, JSON.stringify(budget, null, 2));
      await writeFile(prefix + ".request.json", JSON.stringify(request, null, 2));
      const response = await client.callTool(request);
      await writeFile(prefix + ".mcp.json", JSON.stringify(response, null, 2));
      if (response.isError) throw new Error("Jev operation failed: " + job.id);
      const content = response.content.find(item => item.type === "text");
      if (!content) throw new Error("Jev omitted result: " + job.id);
      result = JSON.parse(content.text);
      if (result.status === "invalid_response") throw new Error("Jev invalid response: " + job.id);
      accounting.status = "returned";
      accounting.usage = result.usage ?? null;
      // Reconcile only a nonzero reported token count against a separately verified
      // provider receipt. Missing/zero usage retains the entire reservation.
      if (budget.input_usd_per_token && accounting.usage?.input_tokens > 0) {
        accounting.accounted_usd = accounting.usage.input_tokens * budget.input_usd_per_token +
          accounting.usage.output_tokens * budget.output_usd_per_token;
        budget.reserved_usd += accounting.accounted_usd - accounting.reserve_usd;
      }
      await writeFile(prefix + ".response.json", JSON.stringify(result, null, 2));
      await writeFile(budgetPath, JSON.stringify(budget, null, 2));
    }
    if (result.status === "invalid_response") throw new Error("Jev invalid response: " + job.id);
    const record = { id: job.id, tool: job.tool, request_hash: hash, result };
    const previous = results.findIndex(row => row.id === job.id);
    if (previous < 0) results.push(record);
    else results[previous] = record;
    await writeFile(join(output, "results.json"), JSON.stringify(results, null, 2));
    console.log(JSON.stringify({ id: job.id, tool: job.tool,
      action: result.action ?? result.recommendation?.action ?? null,
      reserved_usd: budget.reserved_usd }));
    if (job.tool === "jev_screen" && result.recommendation?.action !== "pass")
      throw new Error("Source intake requires inspection: " + prefix + ".response.json");
    if (job.tool === "jev_decide" && result.recommendation?.escaped)
      throw new Error("Jev declined the bounded decision: " + prefix + ".response.json");
  }
} finally {
  await client.close();
  await server.close();
}
