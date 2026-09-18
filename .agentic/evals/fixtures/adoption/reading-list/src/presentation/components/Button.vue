<script setup lang="ts">
withDefaults(defineProps<{ type?: 'button' | 'submit'; pressed?: boolean }>(), { type: 'button' });
</script>

<template><button :type="type" :aria-pressed="pressed"><slot /></button></template>
