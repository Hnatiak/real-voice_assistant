import { writable } from 'svelte/store';

export const assistantSettings = writable({
  name: 'Assistant',
  voice: 'Male',
  speed: 1.0
});