/**
 * IoT Control JavaScript
 * WebSocket client для real-time управління IoT пристроями
 */

class IoTController {
    constructor(location) {
        this.location = location;
        this.ws = null;
        this.reconnectInterval = 3000;
        this.maxReconnectAttempts = 5;
        this.reconnectAttempts = 0;
        this.eventHandlers = {};
        
        this.init();
    }
    
    init() {
        this.connect();
    }
    
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/iot/control/${this.location}/`;
        
        console.log(`[IoT] Connecting to ${wsUrl}`);
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onerror = (error) => this.handleError(error);
            this.ws.onclose = (event) => this.handleClose(event);
        } catch (error) {
            console.error('[IoT] WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }
    
    handleOpen() {
        console.log(`[IoT] Connected to location: ${this.location}`);
        this.reconnectAttempts = 0;
        this.trigger('connected', { location: this.location });
    }
    
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('[IoT] Received:', data);
            
            switch (data.type) {
                case 'connection_established':
                    this.trigger('devices_status', data.devices);
                    break;
                
                case 'device_update':
                    this.trigger('device_update', data);
                    break;
                
                case 'scene_update':
                    this.trigger('scene_update', data);
                    break;
                
                case 'control_result':
                    this.trigger('control_result', data.result);
                    break;
                
                case 'scene_activated':
                    this.trigger('scene_activated', data.result);
                    break;
                
                case 'status_update':
                    this.trigger('status_update', data);
                    break;
                
                case 'error':
                    this.trigger('error', { message: data.message });
                    break;
                
                default:
                    console.warn('[IoT] Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('[IoT] Error parsing message:', error);
        }
    }
    
    handleError(error) {
        console.error('[IoT] WebSocket error:', error);
        this.trigger('error', { message: 'Connection error' });
    }
    
    handleClose(event) {
        console.log(`[IoT] Connection closed. Code: ${event.code}`);
        this.trigger('disconnected', { code: event.code });
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            console.error('[IoT] Max reconnect attempts reached');
            this.trigger('connection_failed');
        }
    }
    
    scheduleReconnect() {
        this.reconnectAttempts++;
        console.log(`[IoT] Reconnecting in ${this.reconnectInterval}ms (attempt ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }
    
    // === Control Methods ===
    
    controlDevice(deviceId, action, value = null) {
        const command = {
            command: 'control_device',
            device_id: deviceId,
            action: action
        };
        
        if (value !== null) {
            command.value = value;
        }
        
        this.send(command);
    }
    
    activateScene(sceneId) {
        this.send({
            command: 'activate_scene',
            scene_id: sceneId
        });
    }
    
    getStatus() {
        this.send({
            command: 'get_status'
        });
    }
    
    setLighting(brightness, color = null) {
        const value = { brightness: brightness };
        if (color) {
            value.color = color;
        }
        
        // Знайти всі lighting пристрої та керувати ними
        this.trigger('lighting_control', value);
    }
    
    setTemperature(temperature) {
        this.trigger('temperature_control', { temperature: temperature });
    }
    
    // === WebSocket Methods ===
    
    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('[IoT] WebSocket not connected');
            this.trigger('error', { message: 'Not connected' });
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
    
    // === Event System ===
    
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }
    
    off(event, handler) {
        if (!this.eventHandlers[event]) return;
        
        const index = this.eventHandlers[event].indexOf(handler);
        if (index > -1) {
            this.eventHandlers[event].splice(index, 1);
        }
    }
    
    trigger(event, data) {
        if (!this.eventHandlers[event]) return;
        
        this.eventHandlers[event].forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`[IoT] Error in ${event} handler:`, error);
            }
        });
    }
}


// === API Helper Functions ===

class IoTAPI {
    static BASE_URL = '/api/iot';
    
    static async getDevices(location = null) {
        const url = location 
            ? `${this.BASE_URL}/devices/?location=${location}`
            : `${this.BASE_URL}/devices/`;
        
        const response = await fetch(url, {
            headers: this.getHeaders()
        });
        
        return await response.json();
    }
    
    static async getScenes(publicOnly = false) {
        const url = publicOnly
            ? `${this.BASE_URL}/scenes/?public=true`
            : `${this.BASE_URL}/scenes/`;
        
        const response = await fetch(url, {
            headers: this.getHeaders()
        });
        
        return await response.json();
    }
    
    static async controlLighting(location, brightness, color = null) {
        const response = await fetch(`${this.BASE_URL}/devices/lighting/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                location: location,
                brightness: brightness,
                color: color
            })
        });
        
        return await response.json();
    }
    
    static async controlTemperature(location, temperature) {
        const response = await fetch(`${this.BASE_URL}/devices/temperature/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({
                location: location,
                temperature: temperature
            })
        });
        
        return await response.json();
    }
    
    static async activateScene(sceneId) {
        const response = await fetch(`${this.BASE_URL}/scenes/${sceneId}/activate/`, {
            method: 'POST',
            headers: this.getHeaders()
        });
        
        return await response.json();
    }
    
    static getHeaders() {
        const token = localStorage.getItem('access_token');
        return {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : ''
        };
    }
}


// === UI Helper Functions ===

function initIoTControls(location) {
    const controller = new IoTController(location);
    
    // Connection status
    controller.on('connected', () => {
        updateConnectionStatus('connected');
    });
    
    controller.on('disconnected', () => {
        updateConnectionStatus('disconnected');
    });
    
    controller.on('error', (data) => {
        showNotification('error', data.message);
    });
    
    // Device updates
    controller.on('device_update', (data) => {
        updateDeviceUI(data.device_id, data.status);
        showNotification('info', `Device updated by ${data.updated_by}`);
    });
    
    // Scene updates
    controller.on('scene_activated', (data) => {
        if (data.success) {
            showNotification('success', `Scene "${data.scene_name}" activated`);
        } else {
            showNotification('error', `Failed to activate scene: ${data.errors}`);
        }
    });
    
    return controller;
}

function updateConnectionStatus(status) {
    const indicator = document.getElementById('connection-status');
    if (!indicator) return;
    
    indicator.className = `status-indicator status-${status}`;
    indicator.textContent = status === 'connected' ? 'Connected' : 'Disconnected';
}

function updateDeviceUI(deviceId, status) {
    const deviceElement = document.querySelector(`[data-device-id="${deviceId}"]`);
    if (!deviceElement) return;
    
    // Оновити UI елемент на основі нового статусу
    if (status.brightness !== undefined) {
        const brightnessSlider = deviceElement.querySelector('.brightness-slider');
        if (brightnessSlider) {
            brightnessSlider.value = status.brightness;
        }
    }
    
    if (status.temperature !== undefined) {
        const tempDisplay = deviceElement.querySelector('.temperature-display');
        if (tempDisplay) {
            tempDisplay.textContent = `${status.temperature}°F`;
        }
    }
    
    if (status.power !== undefined) {
        deviceElement.classList.toggle('device-on', status.power === 'on');
        deviceElement.classList.toggle('device-off', status.power === 'off');
    }
}

function showNotification(type, message) {
    // Створити notification елемент
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Додати до DOM
    const container = document.getElementById('notifications') || document.body;
    container.appendChild(notification);
    
    // Автоматично видалити через 5 секунд
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Export для використання
window.IoTController = IoTController;
window.IoTAPI = IoTAPI;
window.initIoTControls = initIoTControls;

