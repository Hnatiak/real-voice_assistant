<script>
    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
  
    function sendSettings() {
      dispatch('save', { name: 'Assistant', voice: 'Male', speed: 1.0 });
    }
  </script>
  
  <button on:click={sendSettings}>Зберегти налаштування</button>