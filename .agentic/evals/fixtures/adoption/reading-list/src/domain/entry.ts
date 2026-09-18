export type Entry = Readonly<{ id: number; title: string; url: string | null; read: boolean }>;
export type EntryInput = { title: string; url: string };
export type Errors = Partial<Record<keyof EntryInput, string>>;
export type Validation =
  | { ok: true; value: { title: string; url: string | null } }
  | { ok: false; errors: Errors };

export function validateEntry(input: EntryInput): Validation {
  const title = input.title.trim();
  const link = input.url.trim();
  const errors: Errors = {};
  if (!title || title.length > 120) errors.title = 'Enter a title between 1 and 120 characters.';
  let url: string | null = null;
  if (link) {
    try {
      if (!/^https?:\/\//i.test(link) || /[\s\\]/.test(link)) throw new Error('Invalid URL');
      const parsed = new URL(link);
      if (!parsed.hostname || !['http:', 'https:'].includes(parsed.protocol)) throw new Error('Invalid URL');
      url = parsed.href;
    } catch {
      errors.url = 'Enter an absolute http:// or https:// link, or leave it blank.';
    }
  }
  return Object.keys(errors).length ? { ok: false, errors } : { ok: true, value: { title, url } };
}

export function toggleEntry(entries: readonly Entry[], id: number): readonly Entry[] {
  return entries.map(entry => entry.id === id ? { ...entry, read: !entry.read } : entry);
}
