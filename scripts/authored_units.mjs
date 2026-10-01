#!/usr/bin/env node
/** Inventory complete authored Scene statements without executing source code.
 * Source offsets use Unicode code points to match Python bindings, not JS UTF-16.
 * AST structure only suggests units; a director must review their real AV edges.
 */
import { parse } from 'acorn';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const sha = s => createHash('sha256').update(s).digest('hex');
function* children(node) {
  for (const value of Object.values(node)) {
    if (Array.isArray(value)) { for (const item of value) if (item?.type) yield item; }
    else if (value?.type) yield value;
  }
}
function walk(node, visit) { visit(node); for (const child of children(node)) walk(child, visit); }
function iifeBody(statement) {
  const call = statement.type === 'ExpressionStatement' && statement.expression;
  return call?.type === 'CallExpression' && ['ArrowFunctionExpression', 'FunctionExpression'].includes(call.callee.type)
    && call.callee.body.type === 'BlockStatement' ? call.callee.body : null;
}
function constantNumber(node, bindings = {}) {
  if (!node) return null;
  if (node.type === 'Literal' && typeof node.value === 'number') return node.value;
  if (node.type === 'Identifier') return bindings[node.name] ?? null;
  if (node.type === 'UnaryExpression' && ['+', '-'].includes(node.operator)) {
    const value = constantNumber(node.argument, bindings);
    return value === null ? null : node.operator === '-' ? -value : value;
  }
  if (node.type === 'BinaryExpression') {
    const a = constantNumber(node.left, bindings), b = constantNumber(node.right, bindings);
    if (a === null || b === null) return null;
    const ops = {'+':()=>a+b,'-':()=>a-b,'*':()=>a*b,'/':()=>a/b,'%':()=>a%b,'**':()=>a**b};
    const value = ops[node.operator]?.();
    return Number.isFinite(value) ? value : null;
  }
  return null;
}

export function inventory(source, sourceName = 'scenes.js') {
  const ast = parse(source, { ecmaVersion: 2022, sourceType: 'script', locations: true });
  const helpers = new Set();
  walk(ast, node => {
    if (node.type !== 'FunctionDeclaration' || !node.id) return;
    let creates = false;
    walk(node.body, n => { if (n.type === 'NewExpression' && n.callee.name === 'Scene') creates = true; });
    if (creates) helpers.add(node.id.name);
  });
  const creations = node => {
    const found = [];
    function visit(n, env) {
      if (n.type === 'FunctionDeclaration') return;
      if (['BlockStatement', 'Program'].includes(n.type)) {
        const local = Object.create(env);
        for (const child of n.body) visit(child, local);
        return;
      }
      if (n.type === 'VariableDeclaration') {
        for (const declaration of n.declarations) {
          if (declaration.id.type === 'Identifier') {
            const value = constantNumber(declaration.init, env);
            if (value !== null) env[declaration.id.name] = value;
          }
          if (declaration.init) visit(declaration.init, env);
        }
        return;
      }
      if ((n.type === 'NewExpression' && n.callee.name === 'Scene') ||
          (n.type === 'CallExpression' && helpers.has(n.callee.name))) {
        const a = constantNumber(n.arguments[0], env), b = constantNumber(n.arguments[1], env);
        if (a !== null && b !== null && b > a) found.push({ start: a, end: b });
      }
      for (const child of children(n)) visit(child, env);
    }
    visit(node, Object.create(null));
    return found;
  };
  const scopes = [];
  const units = [];
  function scan(body, scopePrelude = '') {
    const candidates = body.body.filter(statement => creations(statement).length === 1 &&
      (iifeBody(statement) || statement.type === 'BlockStatement' || statement.type === 'VariableDeclaration'));
    const excluded = new Set(candidates);
    // Preserve all helper statements in this lexical scope. For the outer
    // wrapper, nested scopes containing several scenes are containers, not helpers.
    const containers = body.body.filter(s => !excluded.has(s) && creations(s).length > 1 && (iifeBody(s) || s.type === 'BlockStatement'));
    const prelude = scopePrelude + body.body.filter(s => !excluded.has(s) && !containers.includes(s))
      .map(s => source.slice(s.start, s.end)).join('\n');
    scopes.push({ preludeSha256: sha(prelude), startLine: body.loc.start.line });
    for (const statement of body.body) {
      if (excluded.has(statement)) {
        const block = source.slice(statement.start, statement.end), timing = creations(statement)[0];
        const strings = [];
        const candidate = `(() => {\n${prelude}\n${block}\n})();`;
        const candidateAST = parse(candidate, { ecmaVersion: 2022, locations: true });
        const offset = value => [...candidate.slice(0, value)].length;
        walk(candidateAST, n => {
          if (n.type === 'Literal' && typeof n.value === 'string') {
            strings.push({ start: offset(n.start + 1), end: offset(n.end - 1), raw: candidate.slice(n.start + 1, n.end - 1),
                           value: n.value, kind: 'string' });
          } else if (n.type === 'TemplateElement' && n.value.raw) {
            strings.push({ start: offset(n.start), end: offset(n.end), raw: n.value.raw, value: n.value.cooked,
                           kind: 'template-quasi' });
          }
        });
        units.push({ index: units.length, sourceFile: sourceName, source: timing,
                     sourceLines: { start: statement.loc.start.line, end: statement.loc.end.line },
                     sourceStatementSha256: sha(block), helperSha256: sha(prelude),
                     sourceBlockSha256: sha(candidate), block: candidate, strings });
      } else if (containers.includes(statement)) scan(iifeBody(statement) || statement, prelude + '\n');
    }
  }
  scan(ast);
  if (!units.length) throw new Error('No complete static Scene units found; retain the source and register an engine adapter');
  return { schema: 'adu-authored-units/1', sourceFile: sourceName, sourceFileSha256: sha(source),
           boundaryReview: 'required: AST boundaries do not certify audiovisual or semantic independence', units };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [file, output] = process.argv.slice(2);
  if (!file || !output) throw new Error('Usage: node authored_units.mjs source.js NEW-inventory.json');
  const result = inventory(readFileSync(file, 'utf8'), file);
  writeFileSync(output, JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
  console.log(JSON.stringify({ units: result.units.length, source: file, output }));
}
