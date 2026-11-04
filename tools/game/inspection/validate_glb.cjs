// Official Khronos validator; read-only, with persistent source-hashed reports.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const validator = require(path.resolve(__dirname, '../../../build/tools/gltf-validator/node_modules/gltf-validator'));
const [destination, ...files] = process.argv.slice(2);
if (!destination || !files.length) throw new Error('Usage: node validate_glb.cjs OUTPUT_DIR MODEL.glb [...]');
fs.mkdirSync(destination, {recursive:true});
(async () => {
  let errors = 0;
  for (const file of files) {
    const bytes = fs.readFileSync(file);
    const report = await validator.validateBytes(new Uint8Array(bytes), {uri:path.basename(file), maxIssues:1000});
    const result = {source:path.resolve(file), sha256:crypto.createHash('sha256').update(bytes).digest('hex'), validator_version:validator.version(), report};
    fs.writeFileSync(path.join(destination,path.basename(file)+'.json'),JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify({file,errors:report.issues.numErrors,warnings:report.issues.numWarnings}));
    errors += report.issues.numErrors;
  }
  process.exitCode = errors ? 1 : 0;
})().catch(error => {console.error(error);process.exitCode=1;});
