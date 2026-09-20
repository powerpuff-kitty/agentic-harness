<script setup lang="ts">
import { computed, nextTick, ref } from 'vue';
import { createReadingList } from '../../application/services/readingList.ts';
import type { Errors } from '../../domain/entry.ts';
import TextField from '../components/TextField.vue';
import Button from '../components/Button.vue';
import Filter from '../components/Filter.vue';

const service = createReadingList();
const entries = ref(service.list());
const title = ref('');
const url = ref('');
const errors = ref<Errors>({});
const filter = ref<'all' | 'unread'>('all');
const titleField = ref<InstanceType<typeof TextField>>();
const urlField = ref<InstanceType<typeof TextField>>();
const filterField = ref<InstanceType<typeof Filter>>();
const list = ref<HTMLElement>();
const announcement = ref('');
const visible = computed(() => entries.value.filter(entry => filter.value === 'all' || !entry.read));

async function add() {
  const result = service.add({ title: title.value, url: url.value });
  errors.value = result.ok ? {} : result.errors;
  if (!result.ok) {
    await nextTick();
    (result.errors.title ? titleField : urlField).value?.focus();
    return;
  }
  entries.value = service.list();
  title.value = '';
  url.value = '';
  announcement.value = `Added ${result.value.title}. ${entries.value.length} entries in this session.`;
  await nextTick();
  titleField.value?.focus();
}

async function toggle(id: number) {
  const index = visible.value.findIndex(entry => entry.id === id);
  service.toggle(id);
  entries.value = service.list();
  if (filter.value === 'unread') {
    await nextTick();
    const buttons = list.value?.querySelectorAll<HTMLButtonElement>('button');
    if (buttons?.length) buttons[Math.min(index, buttons.length - 1)].focus();
    else filterField.value?.focus();
  }
}
</script>

<template>
  <main>
    <h1>Reading list</h1>
    <p>Keep a few things to read, just for now.</p>
    <p class="notice">This list stays in this tab only. Reloading clears every entry.</p>
    <form novalidate @submit.prevent="add">
      <TextField id="title" ref="titleField" v-model="title" label="Title" :error="errors.title" />
      <TextField id="url" ref="urlField" v-model="url" label="Link (optional)" inputmode="url" :error="errors.url" />
      <Button type="submit">Add entry</Button>
    </form>
    <p role="status" class="status">{{ announcement }}</p>
    <section aria-labelledby="entries-heading">
      <h2 id="entries-heading">Your entries</h2>
      <Filter ref="filterField" v-model="filter" />
      <p v-if="!entries.length">No entries yet. Add a title above to start your list.</p>
      <p v-else-if="!visible.length">Nothing unread. Choose All to see your read entries.</p>
      <ul v-else ref="list">
        <li v-for="entry in visible" :key="entry.id">
          <div>
            <a v-if="entry.url" :href="entry.url" target="_blank" rel="noopener noreferrer">{{ entry.title }}</a>
            <span v-else>{{ entry.title }}</span>
            <p class="muted">{{ entry.read ? 'Read' : 'Unread' }}</p>
          </div>
          <Button :pressed="entry.read" :aria-label="`Read: ${entry.title}`" @click="toggle(entry.id)">
            {{ entry.read ? 'Mark unread' : 'Mark read' }}
          </Button>
        </li>
      </ul>
    </section>
    <p class="muted">Links open an external site in a new tab. Following one shares a request with that site.</p>
  </main>
</template>
