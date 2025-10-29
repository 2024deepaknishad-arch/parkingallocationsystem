// static/scripts/main.js - Modern Advanced UI
const gridEl = document.getElementById("grid");
const parkBtn = document.getElementById("parkBtn");
const removeBtn = document.getElementById("removeBtn");
const undoBtn = document.getElementById("undoBtn");
const redoBtn = document.getElementById("redoBtn");
const statusBtn = document.getElementById("statusBtn");
// BST elements removed as per user request
const plateIn = document.getElementById("plate");
const removeSlot = document.getElementById("removeSlot");
const notificationsEl = document.getElementById("notifications");

// Stats
const totalSlotsEl = document.getElementById("totalSlots");
const availableSlotsEl = document.getElementById("availableSlots");
const queueCountEl = document.getElementById("queueCount");
const weatherInfoEl = document.getElementById("weatherInfo");

// Chat
const chatBtn = document.getElementById("chatBtn");
const chatPopup = document.getElementById("chatPopup");
const chatLog = document.getElementById("chatLog");
const chatIn = document.getElementById("chatIn");
const chatSend = document.getElementById("chatSend");
const closeChat = document.getElementById("closeChat");

// Notification System
function showNotification(title, message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  };
  
  notification.innerHTML = `
    <div class="notification-icon">${icons[type] || icons.info}</div>
    <div class="notification-content">
      <div class="notification-title">${title}</div>
      <div class="notification-message">${message}</div>
    </div>
  `;
  
  notificationsEl.appendChild(notification);
  
  // Auto-remove after 4 seconds
  setTimeout(() => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(400px)';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

// Render parking grid
function renderGrid(slots) {
  gridEl.innerHTML = "";
  let available = 0;
  
  slots.forEach(s => {
    const slotDiv = document.createElement("div");
    slotDiv.className = "slot";
    
    if (!s.occupied) {
      slotDiv.classList.add("empty");
      slotDiv.innerHTML = `
        <span>🅿️</span>
        <div class="meta">Slot ${s.slot}</div>
      `;
      available++;
    } else {
      slotDiv.classList.add("occupied");
      slotDiv.innerHTML = `
        <div class="plate-info">${s.plate}</div>
        <span>🚗</span>
        <div class="meta">Slot ${s.slot}</div>
      `;
    }
    
    slotDiv.onclick = () => {
      removeSlot.value = s.slot;
      if (s.occupied) {
        showNotification('Slot Selected', `Slot #${s.slot} - ${s.plate}`, 'info');
      }
    };
    
    gridEl.appendChild(slotDiv);
  });
  
  // Update stats
  availableSlotsEl.textContent = available;
}

// Fetch and refresh status
async function fetchStatus() {
  try {
    const response = await fetch("/status");
    const data = await response.json();
    renderGrid(data.slots);
    queueCountEl.textContent = data.queue.length;
  } catch (error) {
    showNotification('Error', 'Failed to fetch parking status', 'error');
  }
}

// Park vehicle
parkBtn.onclick = async () => {
  const plate = plateIn.value.trim();
  
  try {
    const response = await fetch("/park", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plate })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      if (data.allocated_slot) {
        showNotification(
          'Vehicle Parked! 🎉',
          `${data.plate} assigned to Slot #${data.allocated_slot}`,
          'success'
        );
      } else {
        showNotification(
          'Added to Queue',
          `${data.plate} is in waiting queue (Position: ${data.queue_len})`,
          'warning'
        );
      }
      plateIn.value = "";
      await fetchStatus();
    } else {
      if (data.error === 'duplicate') {
        showNotification('Duplicate Entry', data.message, 'error');
      } else {
        showNotification('Error', data.message || 'Failed to park vehicle', 'error');
      }
    }
  } catch (error) {
    showNotification('Error', 'Failed to park vehicle', 'error');
  }
};

// Remove vehicle
removeBtn.onclick = async () => {
  const slot = parseInt(removeSlot.value);
  
  if (!slot || slot < 1 || slot > 20) {
    showNotification('Invalid Slot', 'Please enter a valid slot number (1-20)', 'warning');
    return;
  }
  
  try {
    const response = await fetch("/remove", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slot_no: slot })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      let message = `${data.plate} removed from Slot #${data.freed}. Fee: ₹${data.fee}`;
      if (data.assigned_next) {
        message += ` | Next vehicle assigned to Slot #${data.assigned_next}`;
      }
      showNotification('Vehicle Removed', message, 'success');
      removeSlot.value = "";
      await fetchStatus();
    } else {
      showNotification('Error', data.error || 'Slot not occupied', 'error');
    }
  } catch (error) {
    showNotification('Error', 'Failed to remove vehicle', 'error');
  }
};

// Undo
undoBtn.onclick = async () => {
  try {
    const response = await fetch("/undo", { method: "POST" });
    const data = await response.json();
    
    if (data.undone) {
      showNotification('Action Undone', `Undid: ${data.undone}`, 'info');
    } else {
      showNotification('Nothing to Undo', data.msg || 'No actions to undo', 'warning');
    }
    await fetchStatus();
  } catch (error) {
    showNotification('Error', 'Failed to undo action', 'error');
  }
};

// Redo
redoBtn.onclick = async () => {
  try {
    const response = await fetch("/redo", { method: "POST" });
    const data = await response.json();
    
    if (data.redone) {
      showNotification('Action Redone', `Redid: ${data.redone}`, 'info');
    } else {
      showNotification('Nothing to Redo', data.msg || 'No actions to redo', 'warning');
    }
    await fetchStatus();
  } catch (error) {
    showNotification('Error', 'Failed to redo action', 'error');
  }
};

// Refresh status
statusBtn.onclick = async () => {
  await fetchStatus();
  showNotification('Refreshed', 'Parking status updated', 'success');
};

// BST Visualization removed as per user request

// Chat functionality
chatBtn.onclick = () => {
  chatPopup.classList.toggle('hidden');
};

closeChat.onclick = () => {
  chatPopup.classList.add('hidden');
};

chatSend.onclick = async () => {
  const question = chatIn.value.trim();
  if (!question) return;
  
  chatLog.innerHTML += `<div><b>You:</b> ${question}</div>`;
  chatIn.value = "";
  
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q: question })
    });
    
    const data = await response.json();
    chatLog.innerHTML += `<div><b>🤖 Assistant:</b> ${data.reply}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  } catch (error) {
    chatLog.innerHTML += `<div><b>🤖 Assistant:</b> Sorry, I encountered an error.</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  }
};

// Limit vehicle number input to 10 characters
plateIn.addEventListener('input', (e) => {
  if (e.target.value.length > 10) {
    e.target.value = e.target.value.slice(0, 10);
    showNotification('Input Limit', 'Vehicle number limited to 10 characters', 'warning');
  }
});

// Enter key support for inputs
plateIn.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') parkBtn.click();
});

removeSlot.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') removeBtn.click();
});

chatIn.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') chatSend.click();
});

// Fetch weather information
async function fetchWeather() {
  try {
    const response = await fetch("/weather");
    const data = await response.json();
    
    // Display weather info in the navbar
    weatherInfoEl.innerHTML = `
      <div>${data.city}</div>
      <div style="font-size: 0.8rem; color: var(--text-muted);">${data.temperature}°C, ${data.condition}</div>
    `;
  } catch (error) {
    weatherInfoEl.textContent = "Weather N/A";
  }
}

// Auto-load on page load
fetchStatus();
fetchWeather();

// Show welcome notification
setTimeout(() => {
  showNotification(
    'Welcome to Smart Parking! 👋',
    'Manage your parking slots efficiently with our advanced system',
    'info'
  );
}, 500);