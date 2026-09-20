import { toggleEntry, validateEntry, type Entry, type EntryInput } from '../../domain/entry.ts';

/** Synchronous session API; no storage, network, Vue or shared global state. */
export function createReadingList() {
  let entries: readonly Entry[] = [];
  let nextId = 1;
  return {
    list: (): readonly Entry[] => entries.map(entry => ({ ...entry })),
    add(input: EntryInput) {
      const result = validateEntry(input);
      if (result.ok) entries = [...entries, { ...result.value, id: nextId++, read: false }];
      return result;
    },
    toggle(id: number) { entries = toggleEntry(entries, id); },
  };
}
