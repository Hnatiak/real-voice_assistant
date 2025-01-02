<script>
    import { onMount } from 'svelte';
  
    let assistantName = "Assistant";
    let assistantVoice = "Male";
    let assistantSpeed = 1.0;
  
    let socket; // Змінна для зберігання WebSocket підключення
  
    // Функція для створення WebSocket з'єднання
    function createWebSocketConnection() {
      socket = new WebSocket('ws://localhost:8765');
  
      // Обробка повідомлень від сервера
      socket.onmessage = (event) => {
        console.log('Received:', event.data);
      };
  
      // Обробка закриття з'єднання
      socket.onclose = () => {
        console.log('WebSocket connection closed');
      };
    }
  
    // Функція для відправки налаштувань через WebSocket
    function sendSettings() {
      if (socket && socket.readyState === WebSocket.OPEN) {
        const settings = {
          name: assistantName,
          voice: assistantVoice,
          speed: assistantSpeed
        };
        socket.send(JSON.stringify(settings));
        console.log('Settings sent:', settings);
      } else {
        console.log('WebSocket is not connected');
      }
    }
  
    // Викликаємо створення WebSocket підключення при завантаженні компонента
    onMount(() => {
      createWebSocketConnection();
    });
  
    // Функції для обробки кнопок
    function closeWindow() {
      window.close(); // Закриття вікна
    }
  
    function goToSettings() {
      alert('Настройки відкриті');
    }
  
    function goToHome() {
      alert('Перехід на головну');
    }
  
    function saveSettings() {
      console.log("Збережено налаштування:", assistantName, assistantVoice, assistantSpeed);
      sendSettings(); // Відправляємо налаштування через WebSocket
    }
  </script>
  
  <style>
    /* Стили для вікна */
    .window {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background-color: white;
      border: 2px solid #ccc;
      padding: 20px;
      width: 400px;
      border-radius: 10px;
      box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
    }
  
    .button-group {
      display: flex;
      justify-content: space-between;
    }
  
    button {
      padding: 10px 20px;
      margin: 5px;
      border-radius: 5px;
      border: none;
      cursor: pointer;
      background-color: #007BFF;
      color: white;
      font-size: 14px;
    }
  
    .button-group button:hover {
      background-color: #0056b3;
    }
  
    label {
      font-size: 14px;
      margin-bottom: 5px;
    }
  
    input, select {
      width: 100%;
      padding: 8px;
      margin: 10px 0;
      border: 1px solid #ccc;
      border-radius: 5px;
    }
  </style>
  
  <div class="window">
    <div class="button-group">
      <button on:click={closeWindow}>Закрити</button>
      <button on:click={goToSettings}>Налаштування</button>
      <button on:click={goToHome}>Головна</button>
    </div>
  
    <h3>Налаштування асистента</h3>
  
    <label for="assistantName">Ім'я асистента:</label>
    <input type="text" id="assistantName" bind:value={assistantName} />
  
    <label for="assistantVoice">Голос асистента:</label>
    <select id="assistantVoice" bind:value={assistantVoice}>
      <option value="Male">Чоловічий</option>
      <option value="Female">Жіночий</option>
    </select>
  
    <label for="assistantSpeed">Швидкість мови:</label>
    <input type="range" id="assistantSpeed" min="0.5" max="2" step="0.1" bind:value={assistantSpeed} />
  
    <button on:click={saveSettings}>Зберегти налаштування</button>
  </div>