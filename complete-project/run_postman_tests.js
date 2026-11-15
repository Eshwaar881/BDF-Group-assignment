// Terminal runner for ToolTown Postman Collection
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ANSI = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  bgGreen: '\x1b[42m\x1b[30m',
  bgRed: '\x1b[41m\x1b[37m'
};

async function sendRequest(method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const postData = body ? JSON.stringify(body) : null;
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: urlPath,
      method: method,
      headers: {
        'Accept': 'application/json'
      }
    };
    if (postData) {
      options.headers['Content-Type'] = 'application/json';
      options.headers['Content-Length'] = Buffer.byteLength(postData);
    }

    const start = Date.now();
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const duration = Date.now() - start;
        let json = null;
        try { json = JSON.parse(data); } catch (e) { json = data; }
        resolve({
          statusCode: res.statusCode,
          statusMessage: res.statusMessage,
          body: json,
          duration
        });
      });
    });

    req.on('error', reject);
    if (postData) req.write(postData);
    req.end();
  });
}

async function run() {
  console.log(`\n${ANSI.bold}${ANSI.cyan}====================================================${ANSI.reset}`);
  console.log(`${ANSI.bold}${ANSI.cyan}    ToolTown Makerspace API - Postman Test Runner   ${ANSI.reset}`);
  console.log(`${ANSI.bold}${ANSI.cyan}====================================================${ANSI.reset}\n`);

  // Reset database before tests
  const dbPath = path.join(__dirname, 'tooltown.db');
  if (fs.existsSync(dbPath)) {
    try { fs.unlinkSync(dbPath); } catch (e) {}
  }

  // Start server
  const server = spawn('node', ['server.js'], { cwd: __dirname });
  await new Promise(r => setTimeout(r, 1500));

  const collectionPath = path.join(__dirname, '..', 'task6-postman-and-readme', 'postman', 'ToolTown.postman_collection.json');
  const collection = JSON.parse(fs.readFileSync(collectionPath, 'utf-8'));

  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;

  try {
    for (const folder of collection.item) {
      console.log(`${ANSI.bold}${ANSI.yellow}📁 ${folder.name}${ANSI.reset}`);

      for (const item of folder.item) {
        const req = item.request;
        const method = req.method;
        const rawUrl = req.url.raw.replace('{{baseUrl}}', '');
        let body = null;
        if (req.body && req.body.raw) {
          try { body = JSON.parse(req.body.raw); } catch (e) {}
        }

        const res = await sendRequest(method, rawUrl, body);

        // Evaluate expected status from item tests
        let expectedStatus = null;
        for (const ev of (item.event || [])) {
          if (ev.listen === 'test') {
            for (const line of ev.script.exec) {
              const m = line.match(/status\((\d+)\)/);
              if (m) expectedStatus = parseInt(m[1], 10);
            }
          }
        }

        totalTests++;
        const isPass = expectedStatus ? (res.statusCode === expectedStatus) : (res.statusCode >= 200 && res.statusCode < 300);

        if (isPass) {
          passedTests++;
          console.log(`  ${ANSI.green}✔ PASS${ANSI.reset} [${ANSI.bold}${method}${ANSI.reset}] ${rawUrl} - ${ANSI.green}${res.statusCode} ${res.statusMessage}${ANSI.reset} ${ANSI.gray}(${res.duration}ms)${ANSI.reset} - ${item.name}`);
        } else {
          failedTests++;
          console.log(`  ${ANSI.red}✖ FAIL${ANSI.reset} [${ANSI.bold}${method}${ANSI.reset}] ${rawUrl} - ${ANSI.red}${res.statusCode} (Expected: ${expectedStatus})${ANSI.reset} - ${item.name}`);
        }
      }
      console.log('');
    }
  } finally {
    server.kill();
  }

  console.log(`${ANSI.bold}----------------------------------------------------${ANSI.reset}`);
  console.log(`Total Requests: ${totalTests} | ${ANSI.green}Passed: ${passedTests}${ANSI.reset} | ${failedTests > 0 ? ANSI.red : ANSI.gray}Failed: ${failedTests}${ANSI.reset}`);
  console.log(`${ANSI.bold}----------------------------------------------------${ANSI.reset}\n`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});

