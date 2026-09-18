<script setup lang="ts">
import { ref } from 'vue';
defineProps<{ id: string; label: string; modelValue: string; error?: string; inputmode?: 'text' | 'url' }>();
defineEmits<{ 'update:modelValue': [value: string] }>();
const input = ref<HTMLInputElement>();
defineExpose({ focus: () => input.value?.focus() });
</script>

<template>
  <div class="field">
    <label :for="id">{{ label }}</label>
    <input :id="id" ref="input" type="text" :inputmode="inputmode ?? 'text'" :value="modelValue"
      :aria-invalid="error ? 'true' : undefined" :aria-describedby="error ? `${id}-error` : undefined"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)" />
    <p v-if="error" :id="`${id}-error`" class="error">{{ error }}</p>
  </div>
</template>
