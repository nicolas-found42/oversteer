/** Apply the pinned source viewer's GT4 preview correction, without changing meshes/PNGs. */
import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { correctGT4Materials } from "./source_viewer/gt4-materials.mjs";

const rows = JSON.parse(await readFile(process.argv[2], "utf8"));
const reports = [];
for (const row of rows) {
  const bytes = await readFile(row.source);
  if (createHash("sha256").update(bytes).digest("hex") !== row.sha256)
    throw new Error("Source hash mismatch: " + row.code);
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  const view = new DataView(buffer);
  let doc, binary;
  for (let cursor = 12; cursor < buffer.byteLength;) {
    const size = view.getUint32(cursor, true), type = view.getUint32(cursor + 4, true);
    if (type === 0x4e4f534a) doc = JSON.parse(new TextDecoder().decode(new Uint8Array(buffer, cursor + 8, size)));
    if (type === 0x004e4942) binary = new Uint8Array(buffer, cursor + 8, size);
    cursor += size + 8;
  }
  if (!doc || !binary) throw new Error("Incomplete GLB: " + row.code);
  const images = (doc.images ?? []).map(image => {
    const span = doc.bufferViews[image.bufferView];
    return binary.subarray(span.byteOffset ?? 0, (span.byteOffset ?? 0) + span.byteLength);
  });
  const corrected = await correctGT4Materials(buffer, { doc, images }, { sourceHash: row.sha256 });
  await writeFile(row.output, Buffer.from(corrected.buffer));
  reports.push({ code: row.code, report: corrected.report,
    output_sha256: createHash("sha256").update(Buffer.from(corrected.buffer)).digest("hex") });
}
await writeFile(process.argv[3], JSON.stringify(reports, null, 2));
console.log(JSON.stringify({ processed: reports.length,
  corrected: reports.filter(row => row.report !== null).length }));
