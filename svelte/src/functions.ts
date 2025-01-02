import { writable } from 'svelte/store';

export const settings = writable({
  assistantName: 'Assistant',
  assistantVoice: 'Male',
  assistantSpeed: 1.0,
});

export function updateSettings(newSettings: any) {
  settings.set(newSettings);
}