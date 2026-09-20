#!/usr/bin/env python3
"""Outline explicit JS/TS source with a reviewed, already-installed compiler.

Python 3.10+ standard library, an explicit Node executable and hash-pinned TypeScript
5/6 CommonJS compiler entry. No installation, project build, target execution or
provider calls. Parser/runtime/helper directories must be trusted and quiescent.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import types
from typing import Any

MAX_FILES = 32
MAX_FILE_BYTES = 262_144
MAX_TOTAL_BYTES = 2_097_152
MAX_PARSER_BYTES = 16_777_216
MAX_OUTPUT_BYTES = 2_097_152
DEFAULT_BUDGET = 65_536
EXTENSIONS = {'.ts', '.tsx', '.mts', '.cts', '.js', '.jsx', '.mjs', '.cjs'}


class OutlineError(ValueError):
    """Fixed error codes only, never source text or provider diagnostics."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise OutlineError(code)


def load_reader():
    """Bootstrap only bounded current sibling source, never a cached .pyc."""
    path = Path(__file__).absolute().with_name('evidence_snapshot.py')

    def identity(meta):
        require(stat.S_ISREG(meta.st_mode) and not
                (getattr(meta, 'st_file_attributes', 0) & 0x400), 'reader-unavailable')
        return (meta.st_dev, meta.st_ino, meta.st_size, meta.st_mtime_ns, meta.st_ctime_ns)

    before = path.lstat()
    expected = identity(before)
    require(before.st_size <= 65_536, 'reader-unavailable')
    flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        require(identity(os.fstat(stream.fileno())) == expected, 'reader-unavailable')
        raw = stream.read(65_537)
        after = identity(os.fstat(stream.fileno()))
    require(after == expected == identity(path.lstat()) and len(raw) == before.st_size,
            'reader-unavailable')
    module = types.ModuleType('_typescript_evidence_reader')
    module.__file__ = str(path)
    code = compile(raw, str(path), 'exec', dont_inherit=True)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        exec(code, module.__dict__)
    finally:
        sys.dont_write_bytecode = previous
    return module


# Fixed adapter supplied to Node directly: never generated from target text.
ADAPTER = r"""
'use strict';
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const fail = code => { throw new Error(code); };
const sha = bytes => 'sha256:' + crypto.createHash('sha256').update(bytes).digest('hex');
const allowedErrors = new Set(['parser-changed', 'unsupported-parser', 'unsupported-syntax', 'structure-limit']);
try {
  const [compilerPath, compilerHash] = process.argv.slice(1);
  const parserBytes = fs.readFileSync(compilerPath);
  if (parserBytes.length > 16777216 || sha(parserBytes) !== compilerHash) fail('parser-changed');
  const ts = require(compilerPath); // Explicitly reviewed executable parser, NOT target source.
  if (!/^[56]\./.test(ts.version || '') || typeof ts.createSourceFile !== 'function' ||
      typeof ts.forEachChild !== 'function') fail('unsupported-parser');
  if (sha(fs.readFileSync(compilerPath)) !== compilerHash) fail('parser-changed');
  const inputs = JSON.parse(fs.readFileSync(0, 'utf8'));
  const files = [];
  let totalDefinitions = 0, totalNodes = 0, nameBytes = 0;
  for (const input of inputs) {
    const text = input.text;
    const extension = path.extname(input.path);
    const kind = extension === '.tsx' ? ts.ScriptKind.TSX : extension === '.jsx' ? ts.ScriptKind.JSX :
      ['.js', '.mjs', '.cjs'].includes(extension) ? ts.ScriptKind.JS : ts.ScriptKind.TS;
    // No Program, CompilerHost, tsconfig, emit, type checker or import resolution.
    const source = ts.createSourceFile(input.path, text, ts.ScriptTarget.Latest, true, kind);
    if (source.parseDiagnostics.length) fail('unsupported-syntax');
    const lineStarts = [0];
    for (let i = 0; i < text.length; i++) if (text[i] === '\n') lineStarts.push(i + 1);
    const line = offset => {
      let lo = 0, hi = lineStarts.length;
      while (lo + 1 < hi) { const mid = (lo + hi) >>> 1; if (lineStarts[mid] <= offset) lo = mid; else hi = mid; }
      return lo + 1; // LF numbering, not TypeScript's Unicode/CR line numbering.
    };
    const declarations = [];
    const stack = [{node: source, parent: null, prefix: '', bound: false}];
    let nodes = 0, unnamed = 0;
    while (stack.length) {
      const frame = stack.pop();
      const node = frame.node;
      if (++nodes > 50000) fail('structure-limit');
      let label = null, category = null, container = false, bind = null;
      const name = node.name;
      if (name && (ts.isIdentifier(name) || ts.isPrivateIdentifier(name))) label = name.text;
      if (ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)) { category = 'function'; container = true; }
      else if (ts.isClassDeclaration(node) || ts.isClassExpression(node)) { category = 'class'; container = true; }
      else if (ts.isInterfaceDeclaration(node)) { category = 'interface'; container = true; }
      else if (ts.isTypeAliasDeclaration(node)) { category = 'type'; container = true; }
      else if (ts.isEnumDeclaration(node)) { category = 'enum'; container = true; }
      else if (ts.isModuleDeclaration(node)) { category = 'namespace'; container = true; }
      else if (ts.isMethodDeclaration(node) || ts.isMethodSignature(node)) { category = 'method'; container = true; }
      else if (ts.isGetAccessorDeclaration(node) || ts.isSetAccessorDeclaration(node)) { category = 'accessor'; container = true; }
      else if (ts.isConstructorDeclaration(node)) { label = 'constructor'; category = 'constructor'; container = true; }
      else if ((ts.isVariableDeclaration(node) || ts.isPropertyDeclaration(node) || ts.isPropertyAssignment(node)) && node.initializer) {
        let value = node.initializer;
        while (ts.isParenthesizedExpression(value) || ts.isAsExpression(value) || ts.isSatisfiesExpression(value)) value = value.expression;
        if (ts.isArrowFunction(value) || ts.isFunctionExpression(value) || ts.isClassExpression(value)) {
          category = ts.isClassExpression(value) ? 'class-binding' : 'function-binding'; container = true; bind = value;
        }
      }
      let parent = frame.parent, prefix = frame.prefix;
      const start = node.getStart(source, false);
      if (category && label && !frame.bound) {
        if (++totalDefinitions > 2048 || label.length > 512 || prefix.length + label.length > 4096) fail('structure-limit');
        const qualified = prefix + label;
        nameBytes += Buffer.byteLength(qualified) + Buffer.byteLength(label);
        if (nameBytes > 262144) fail('structure-limit');
        const id = String(start) + ':' + String(node.end); // UTF-16 source offsets, file-local.
        let rangeStart = start;
        // A split-line const/export belongs to a single-binding declaration's range.
        if (ts.isVariableDeclaration(node) && node.parent.declarations.length === 1 &&
            ts.isVariableStatement(node.parent.parent)) rangeStart = node.parent.parent.getStart(source, false);
        declarations.push({id, name: label, qualified_name: qualified, parent_id: parent, kind: category,
          start_line: line(rangeStart), end_line: line(Math.max(rangeStart, node.end - 1))});
        if (container) { parent = id; prefix = qualified + '.'; }
      } else if ((container || ts.isArrowFunction(node)) && !frame.bound) {
        // Do not falsely assign anonymous-callback children to the enclosing named function.
        unnamed++;
        parent = null;
        prefix += '<anonymous@' + start + '>.';
      }
      const children = [];
      ts.forEachChild(node, child => { children.push(child); }); // Must not return Array.push's number.
      for (let i = children.length - 1; i >= 0; i--) {
        const child = children[i];
        // Binding wrappers inherit a name; parenthesized/cast wrappers propagate to their expression.
        const propagate = frame.bound && (ts.isParenthesizedExpression(node) || ts.isAsExpression(node) || ts.isSatisfiesExpression(node));
        stack.push({node: child, parent, prefix, bound: child === bind ||
          (bind !== null && child === node.initializer) || (propagate && child === node.expression)});
      }
    }
    totalNodes += nodes;
    declarations.sort((a, b) => Number(a.id.split(':')[0]) - Number(b.id.split(':')[0]));
    files.push({path: input.path, sha256: input.sha256, definitions: declarations, unnamed_scopes: unnamed});
  }
  const output = JSON.stringify({version: ts.version, node_version: process.version, files,
    definitions: totalDefinitions, ast_nodes: totalNodes});
  if (Buffer.byteLength(output) > 2097152) fail('structure-limit');
  process.stdout.write(output);
} catch (error) {
  process.stdout.write(JSON.stringify({error: allowedErrors.has(error.message) ? error.message : 'parser-failed'}));
  process.exitCode = 2;
}
"""


def clean_environment() -> dict[str, str]:
    # Do not forward NODE_OPTIONS/NODE_PATH, API keys, preload hooks or other ambient config.
    return {key: os.environ[key] for key in ('SystemRoot', 'WINDIR', 'SYSTEMDRIVE') if key in os.environ}


def outline(root: Path, selections: list, node: Path, compiler: Path, compiler_pin: str,
            budget: int = DEFAULT_BUDGET) -> dict[str, Any]:
    reader = load_reader()
    require(type(budget) is int and 1 <= budget <= MAX_OUTPUT_BYTES, 'invalid-budget')
    require(isinstance(selections, list) and 1 <= len(selections) <= MAX_FILES, 'invalid-selection')
    pins = {}
    for selection in selections:
        require(isinstance(selection, (list, tuple)) and len(selection) == 2, 'invalid-selection')
        name, pin = selection
        reader.selection([name])
        require(Path(name).suffix in EXTENSIONS, 'unsupported-language')
        require(reader.valid_digest(pin), 'invalid-source-pin')
        require(name not in pins or pins[name] == pin, 'conflicting-source-pins')
        pins[name] = pin
    names = reader.selection(list(pins))
    require(node.is_absolute() and compiler.is_absolute(), 'absolute-tool-paths-required')
    require(node.is_file() and os.access(node, os.X_OK), 'node-unavailable')
    require(reader.valid_digest(compiler_pin), 'invalid-parser-pin')
    parser_bytes = reader.read_text(compiler, MAX_PARSER_BYTES)
    require(reader.sha(parser_bytes) == compiler_pin, 'parser-changed')
    root = reader.real_directory(root)
    inputs, metadata, total = [], {}, 0
    for name in names:
        raw = reader.read_text(root / name, min(MAX_FILE_BYTES, MAX_TOTAL_BYTES - total))
        require(reader.sha(raw) == pins[name], 'source-changed')
        total += len(raw)
        inputs.append({'path': name, 'sha256': pins[name], 'text': raw.decode('utf-8')})
        metadata[name] = {'source_bytes': len(raw), 'total_lines': raw.count(b'\n') + bool(raw and not raw.endswith(b'\n'))}
    try:
        run = subprocess.run([str(node), '--max-old-space-size=128', '--input-type=commonjs', '-e',
                              ADAPTER, str(compiler), compiler_pin], input=reader.encoded(inputs),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15,
                             cwd=Path(__file__).absolute().parent, env=clean_environment(), check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise OutlineError('parser-unavailable-or-timeout') from None
    require(len(run.stdout) <= MAX_OUTPUT_BYTES, 'parser-output-limit')
    try:
        result = json.loads(run.stdout.decode('utf-8'), object_pairs_hook=reader.unique,
                            parse_constant=reader.constant)
    except (ValueError, UnicodeError, RecursionError):
        raise OutlineError('parser-failed') from None
    if run.returncode:
        code = result.get('error') if isinstance(result, dict) else None
        raise OutlineError(code if isinstance(code, str) and code in {'parser-changed', 'unsupported-parser', 'unsupported-syntax',
                                           'structure-limit'} else 'parser-failed')
    require(isinstance(result, dict) and set(result) == {'version', 'node_version', 'files',
            'definitions', 'ast_nodes'} and isinstance(result['files'], list), 'invalid-parser-output')
    require(all(isinstance(item, dict) for item in result['files']) and
            [item.get('path') for item in result['files']] == names, 'invalid-parser-output')
    for item in result['files']:
        require(item.get('sha256') == pins[item['path']], 'invalid-parser-output')
        item.update(metadata[item['path']])
    report = {'format_version': 1, 'kind': 'selected-typescript-outline', 'status': 'ready',
              'files': result['files'],
              'parser': {'name': 'typescript', 'version': result['version'], 'sha256': compiler_pin,
                         'node_version': result['node_version'], 'entry_bytes': len(parser_bytes)},
              'measurement': {'unit': 'utf8-bytes', 'source_bytes_read': total,
                              'definitions': result['definitions'], 'ast_nodes': result['ast_nodes'],
                              'budget_bytes': budget},
              'limits': {'content_authority': 'navigation-only', 'source_bodies_emitted': False,
                         'required_evidence_emitted': False, 'dependencies_resolved': False,
                         'checks_verified': False, 'evidence_sufficient': None, 'model_tokens': None,
                         'provider_calls': 0, 'parser_executed': True, 'target_code_executed': False}}
    required = len(reader.encoded(report))
    if required > budget:
        return {'format_version': 1, 'kind': report['kind'], 'status': 'budget-exceeded', 'files': [],
                'budget_bytes': budget, 'required_output_bytes': required,
                'source_bodies_emitted': False, 'required_evidence_emitted': False}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--file', action='append', nargs=2, required=True, metavar=('PATH', 'SHA256'))
    parser.add_argument('--node', type=Path, required=True, help='absolute reviewed Node executable path')
    parser.add_argument('--typescript', nargs=2, required=True, metavar=('PATH', 'SHA256'),
                        help='absolute reviewed TypeScript CommonJS entry and its actual hash')
    parser.add_argument('--budget-bytes', type=int, default=DEFAULT_BUDGET)
    args = parser.parse_args()
    try:
        result = outline(args.root, args.file, args.node, Path(args.typescript[0]),
                         args.typescript[1], args.budget_bytes)
        output = (json.dumps(result, ensure_ascii=True, sort_keys=True, separators=(',', ':'),
                             allow_nan=False) + '\n').encode('utf-8')
    except OutlineError as error:
        print(json.dumps({'kind': 'typescript-outline-error', 'code': str(error)}), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, SyntaxError, RecursionError):
        print('{"kind":"typescript-outline-error","code":"invalid-or-unavailable-input"}', file=sys.stderr)
        return 2
    sys.stdout.buffer.write(output)
    return 1 if result['status'] == 'budget-exceeded' else 0


if __name__ == '__main__':
    raise SystemExit(main())
