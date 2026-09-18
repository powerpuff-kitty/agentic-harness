import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateEntry } from '../src/domain/entry.ts';
import { createReadingList } from '../src/application/services/readingList.ts';

test('title limits, trimming and optional link', () => {
  assert.deepEqual(validateEntry({ title: '  Notes  ', url: ' ' }), { ok: true, value: { title: 'Notes', url: null } });
  assert.equal(validateEntry({ title: 'x'.repeat(120), url: '' }).ok, true);
  for (const title of ['', '   ', 'x'.repeat(121)]) assert.equal(validateEntry({ title, url: '' }).ok, false);
});

test('untrusted schemes, relative and malformed links are rejected', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,test', '/relative', '//example.test', 'https://', 'https:example.test', 'https://exa mple.test', 'https://example.test\\path']) {
    assert.equal(validateEntry({ title: 'Title', url }).ok, false, url);
  }
  for (const url of ['http://example.test', 'https://example.test/path?q=value#section']) {
    assert.equal(validateEntry({ title: 'Title', url }).ok, true, url);
  }
});

test('rejection leaves session unchanged; duplicates have distinct IDs', () => {
  const service = createReadingList();
  service.add({ title: 'Same', url: '' });
  assert.equal(service.add({ title: '', url: '' }).ok, false);
  service.add({ title: 'Same', url: '' });
  assert.deepEqual(service.list().map(entry => entry.id), [1, 2]);
});

test('toggle affects one entry, snapshots cannot mutate service and sessions are isolated', () => {
  const service = createReadingList();
  service.add({ title: 'One', url: '' });
  service.add({ title: 'Two', url: '' });
  const before = service.list();
  service.toggle(before[0].id);
  assert.deepEqual(service.list().map(entry => entry.read), [true, false]);
  assert.equal(before[0].read, false);
  (before[0] as { title: string }).title = 'Changed snapshot';
  assert.equal(service.list()[0].title, 'One');
  service.toggle(999);
  assert.equal(service.list().length, 2);
  assert.equal(createReadingList().list().length, 0);
});
