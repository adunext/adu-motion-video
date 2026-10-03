#!/usr/bin/env node
// Teach the existing static inventory about core.js's external scene helper.
import {readFileSync, writeFileSync} from 'node:fs';
import {parse} from 'acorn';
import {createHash} from 'node:crypto';
import {inventory} from '../../scripts/authored_units.mjs';
const [filename, output] = process.argv.slice(2);
if (!filename || !output) throw Error('Usage: inventory.mjs scenes.js NEW.json');
const source = readFileSync(filename, 'utf8');
const stub = 'function scene(s,e,opt){return new Scene(s,e,"transparent",opt);}\n';
const found = inventory(stub + source, 'scenes.js');
const ast = parse(source, {ecmaVersion: 2022, locations: true});
const statements = ast.body.filter(node => node.type === 'BlockStatement');
const sha = value => createHash('sha256').update(value).digest('hex');
if (statements.length !== found.units.length) throw Error('Unexpected source block shape');
found.units.forEach((unit, i) => {
  const node = statements[i], statement = source.slice(node.start, node.end);
  if (unit.sourceStatementSha256 !== sha(statement)) throw Error('Existing AST inventory disagrees with source statement');
  unit.statement = statement;
  unit.sourceLines = {start: node.loc.start.line, end: node.loc.end.line};
});
found.sourceFileSha256 = sha(source);
found.prelude = source.slice(0, statements[0].start);
const keys = [];
function walk(node) {
  if (node.type === 'CallExpression' && node.callee?.name === 'tkKey') {
    if (node.arguments[0]?.type !== 'Literal' || typeof node.arguments[0].value !== 'number')
      throw Error('Dynamic talk-key time needs a new adapter review');
    keys.push({at: node.arguments[0].value, source: source.slice(node.start, node.end) + ';'});
  }
  for (const child of Object.values(node)) {
    if (Array.isArray(child)) child.forEach(item => {if (item?.type) walk(item);});
    else if (child?.type) walk(child);
  }
}
walk(ast); found.talkKeys = keys;
writeFileSync(output, JSON.stringify(found, null, 2) + '\n', {flag: 'wx'});
