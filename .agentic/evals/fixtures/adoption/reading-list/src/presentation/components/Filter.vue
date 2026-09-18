<script setup lang="ts">
import { ref } from 'vue';
defineProps<{ modelValue: 'all' | 'unread' }>();
defineEmits<{ 'update:modelValue': [value: 'all' | 'unread'] }>();
const select = ref<HTMLSelectElement>();
defineExpose({ focus: () => select.value?.focus() });
</script>

<template>
  <div class="field">
    <label for="filter">Show entries</label>
    <select id="filter" ref="select" :value="modelValue"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value as 'all' | 'unread')">
      <option value="all">All</option><option value="unread">Unread</option>
    </select>
  </div>
</template>
