import anywidget
import traitlets

class StopwatchWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let intervalId = null;
        let startTime = null;
        let pausedTime = 0;
        
        // Create container
        let container = document.createElement("div");
        container.className = "stopwatch-container";
        
        // Create display
        let display = document.createElement("div");
        display.className = "stopwatch-display";
        
        // Create button container
        let buttonContainer = document.createElement("div");
        buttonContainer.className = "button-container";
        
        // Create buttons
        let startBtn = document.createElement("button");
        startBtn.innerHTML = "Start";
        startBtn.className = "btn btn-start";
        
        let stopBtn = document.createElement("button");
        stopBtn.innerHTML = "Stop";  
        stopBtn.className = "btn btn-stop";
        
        let resetBtn = document.createElement("button");
        resetBtn.innerHTML = "Reset";
        resetBtn.className = "btn btn-reset";
        
        // Theme management
        function applyTheme(theme) {
            container.setAttribute('data-theme', theme);
        }
        
        // Initialize theme and listen for changes
        let initialTheme = model.get("theme") || 'auto';
        applyTheme(initialTheme);
        
        model.on("change:theme", () => {
            applyTheme(model.get("theme"));
        });
        
        // Format time helper
        function formatTime(milliseconds) {
            let totalSeconds = Math.floor(milliseconds / 1000);
            let minutes = Math.floor(totalSeconds / 60);
            let seconds = totalSeconds % 60;
            let ms = Math.floor((milliseconds % 1000) / 10);
            return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
        }
        
        // Update display
        function updateDisplay() {
            let elapsed = model.get("elapsed_time");
            display.innerHTML = formatTime(elapsed);
        }
        
        // Start stopwatch
        function startStopwatch() {
            if (!intervalId) {
                startTime = Date.now() - pausedTime;
                intervalId = setInterval(() => {
                    // Safety check - ensure we're still supposed to be running
                    if (!model.get("is_running")) {
                        clearInterval(intervalId);
                        intervalId = null;
                        return;
                    }
                    
                    let elapsed = Date.now() - startTime;
                    
                    // Update display immediately (smooth UI)
                    display.innerHTML = formatTime(elapsed);
                    
                    // Only sync to Python every 100ms or when seconds change
                    let currentSeconds = Math.floor(elapsed / 10);
                    let lastSeconds = Math.floor(model.get("elapsed_time") / 10);
                    
                    if (currentSeconds !== lastSeconds || elapsed % 100 < 10) {
                        model.set("elapsed_time", elapsed);
                        model.set("last_updated", Date.now()); 
                        // Don't set is_running here to avoid recursive calls
                        model.save_changes();
                    }
                }, 10);
                    
                // Set running state after starting interval
                model.set("is_running", true);
                model.save_changes();
            }
        }
        
        // Stop stopwatch
        function stopStopwatch() {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
                pausedTime = model.get("elapsed_time");
                model.set("is_running", false);
                model.set("last_updated", Date.now());  
                model.save_changes();
            }
        }
        
        // Reset stopwatch  
        function resetStopwatch() {
            // Always clear interval first
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            pausedTime = 0;
            model.set("elapsed_time", 0);
            model.set("is_running", false);
            model.set("last_updated", Date.now());  
            model.save_changes();
        }
        
        // Event listeners
        startBtn.addEventListener("click", startStopwatch);
        stopBtn.addEventListener("click", stopStopwatch);
        resetBtn.addEventListener("click", resetStopwatch);
        
        // Model change listeners
        // Listen for programmatic start/stop/reset from Python
        model.on("change:is_running", () => {
            if (model.get("is_running") && !intervalId) {
                // Start programmatically - sync pausedTime with model
                pausedTime = model.get("elapsed_time");
                startTime = Date.now() - pausedTime;
                intervalId = setInterval(() => {
                    // Safety check - ensure we're still supposed to be running
                    if (!model.get("is_running")) {
                        clearInterval(intervalId);
                        intervalId = null;
                        return;
                    }
                    
                    let elapsed = Date.now() - startTime;
                    
                    // Update display immediately (smooth UI)
                    display.innerHTML = formatTime(elapsed);
                    
                    // Only sync to Python every 100ms or when seconds change
                    let currentSeconds = Math.floor(elapsed / 10);
                    let lastSeconds = Math.floor(model.get("elapsed_time") / 10);
                    
                    if (currentSeconds !== lastSeconds || elapsed % 100 < 10) {
                        model.set("elapsed_time", elapsed);
                        model.set("last_updated", Date.now()); 
                        model.save_changes();
                    }
                }, 10);
            } else if (!model.get("is_running") && intervalId) {
                // Force stop - clear interval immediately
                clearInterval(intervalId);
                intervalId = null;
                pausedTime = model.get("elapsed_time");
            }
        });
        
        // Listen for elapsed_time changes (for reset functionality)
        model.on("change:elapsed_time", () => {
            let elapsed = model.get("elapsed_time");
            if (elapsed === 0 && !model.get("is_running")) {
                // This is likely a reset - update pausedTime
                pausedTime = 0;
            }
            updateDisplay();
        });
        
        // Initial display
        updateDisplay();
        
        // Assemble the widget
        container.appendChild(display);
        buttonContainer.appendChild(startBtn);
        buttonContainer.appendChild(stopBtn);
        buttonContainer.appendChild(resetBtn);
        container.appendChild(buttonContainer);
        el.appendChild(container);
        
        // Cleanup function to prevent memory leaks
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
        };
    }
    export default { render };
    """
    
    _css = """
    .stopwatch-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        text-align: center;
        padding: 32px 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(226, 232, 240, 0.8);
        display: inline-block;
        min-width: 280px;
        position: relative;
        transition: all 0.3s ease;
    }

    .stopwatch-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
        pointer-events: none;
    }

    .stopwatch-display {
        font-size: 48px;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        margin-bottom: 24px;
        color: #1e293b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .button-container {
        display: flex;
        gap: 12px;
        justify-content: center;
        position: relative;
        z-index: 1;
    }

    .btn {
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        color: white;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }

    .btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }

    .btn:hover::before {
        left: 100%;
    }

    .btn-start {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: 1px solid rgba(5, 150, 105, 0.3);
    }

    .btn-start:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(5, 150, 105, 0.3);
    }

    .btn-stop {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: 1px solid rgba(220, 38, 38, 0.3);
    }

    .btn-stop:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(220, 38, 38, 0.3);
    }

    .btn-reset {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        border: 1px solid rgba(75, 85, 99, 0.3);
    }

    .btn-reset:hover {
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(75, 85, 99, 0.3);
    }

    .btn:active {
        transform: translateY(0);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }

    /* Manual dark mode - takes precedence over system preference */
    .stopwatch-container[data-theme="dark"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(51, 65, 85, 0.8);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.3),
            0 2px 4px -1px rgba(0, 0, 0, 0.2);
    }
    
    .stopwatch-container[data-theme="dark"]::before {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
    }
    
    .stopwatch-container[data-theme="dark"] .stopwatch-display {
        color: #f1f5f9;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .stopwatch-container[data-theme="dark"] .btn {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-start {
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
        border: 1px solid rgba(6, 95, 70, 0.5);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-start:hover {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        box-shadow: 0 4px 8px rgba(6, 95, 70, 0.4);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-stop {
        background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
        border: 1px solid rgba(153, 27, 27, 0.5);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-stop:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
        box-shadow: 0 4px 8px rgba(153, 27, 27, 0.4);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-reset {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
        border: 1px solid rgba(55, 65, 81, 0.5);
    }
    
    .stopwatch-container[data-theme="dark"] .btn-reset:hover {
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        box-shadow: 0 4px 8px rgba(55, 65, 81, 0.4);
    }

    /* Manual light mode - overrides system preference */
    .stopwatch-container[data-theme="light"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stopwatch-container[data-theme="light"]::before {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
    }
    
    .stopwatch-container[data-theme="light"] .stopwatch-display {
        color: #1e293b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    /* Auto mode - follows system preference */
    .stopwatch-container[data-theme="auto"] {
        /* Light mode styles by default */
    }

    @media (prefers-color-scheme: dark) {
        .stopwatch-container[data-theme="auto"] {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(51, 65, 85, 0.8);
            box-shadow: 
                0 4px 6px -1px rgba(0, 0, 0, 0.3),
                0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }
        
        .stopwatch-container[data-theme="auto"]::before {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
        }
        
        .stopwatch-container[data-theme="auto"] .stopwatch-display {
            color: #f1f5f9;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .stopwatch-container[data-theme="auto"] .btn {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-start {
            background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
            border: 1px solid rgba(6, 95, 70, 0.5);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-start:hover {
            background: linear-gradient(135deg, #047857 0%, #065f46 100%);
            box-shadow: 0 4px 8px rgba(6, 95, 70, 0.4);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-stop {
            background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
            border: 1px solid rgba(153, 27, 27, 0.5);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-stop:hover {
            background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
            box-shadow: 0 4px 8px rgba(153, 27, 27, 0.4);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-reset {
            background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
            border: 1px solid rgba(55, 65, 81, 0.5);
        }
        
        .stopwatch-container[data-theme="auto"] .btn-reset:hover {
            background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
            box-shadow: 0 4px 8px rgba(55, 65, 81, 0.4);
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .stopwatch-container,
        .btn,
        .btn::before {
            transition: none;
        }
        
        .btn:hover {
            transform: none;
        }
    }
    """
    
    elapsed_time = traitlets.Int(0).tag(sync=True)  # Time in milliseconds
    is_running = traitlets.Bool(False).tag(sync=True)  # Stopwatch state
    last_updated = traitlets.Float(0.0).tag(sync=True)  # Last update timestamp
    theme = traitlets.Unicode('auto').tag(sync=True)  # Theme preference: 'light', 'dark', 'auto'
    
    def start(self):
        """Start the stopwatch programmatically"""
        if not self.is_running:
            self.is_running = True
    
    def stop(self):
        """Stop the stopwatch programmatically"""
        if self.is_running:
            self.is_running = False
    
    def reset(self):
        """Reset the stopwatch programmatically"""
        was_running = self.is_running
        self.is_running = False
        self.elapsed_time = 0
        # If it was running, the state change will trigger the JS listener
        # If it wasn't running, we still need to update the display
        if not was_running:
            # Force a state change to trigger frontend update
            self.last_updated = __import__('time').time()
    
class TimerWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let intervalId = null;
        let endTime = null;
        
        // Create container
        let container = document.createElement("div");
        container.className = "timer-container";
        
        // Theme management
        function applyTheme(theme) {
            container.setAttribute('data-theme', theme);
        }
        
        // Initialize theme and listen for changes
        let initialTheme = model.get("theme") || 'auto';
        applyTheme(initialTheme);
        
        model.on("change:theme", () => {
            applyTheme(model.get("theme"));
        });
        
        // Sound function
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
         function playBeep() {
            try {
                if (audioContext.state === 'suspended') {
                    audioContext.resume();
                }
                
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
                
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.5);
            } catch (error) {
                console.log('Audio not supported or blocked');
            }
        }

        // Create time input section
        let inputSection = document.createElement("div");
        inputSection.className = "input-section";
        
        let inputLabel = document.createElement("div");
        inputLabel.innerHTML = "Set Timer (HH:MM:SS):";
        inputLabel.className = "input-label";
        
        let inputContainer = document.createElement("div");
        inputContainer.className = "input-container";
        
        // Hours input
        let hoursInput = document.createElement("input");
        hoursInput.type = "number";
        hoursInput.min = "0";
        hoursInput.max = "23";
        hoursInput.value = "0";
        hoursInput.className = "time-input";
        
        let colon1 = document.createElement("span");
        colon1.innerHTML = ":";
        colon1.className = "colon";
        
        // Minutes input
        let minutesInput = document.createElement("input");
        minutesInput.type = "number";
        minutesInput.min = "0";
        minutesInput.max = "59";
        minutesInput.value = "5";
        minutesInput.className = "time-input";
        
        let colon2 = document.createElement("span");
        colon2.innerHTML = ":";
        colon2.className = "colon";
        
        // Seconds input
        let secondsInput = document.createElement("input");
        secondsInput.type = "number";
        secondsInput.min = "0";
        secondsInput.max = "59";
        secondsInput.value = "0";
        secondsInput.className = "time-input";
        
        // Create display
        let display = document.createElement("div");
        display.className = "timer-display";
        
        // Create button container
        let buttonContainer = document.createElement("div");
        buttonContainer.className = "button-container";
        
        // Create buttons
        let startBtn = document.createElement("button");
        startBtn.innerHTML = "Start";
        startBtn.className = "btn btn-start";
        
        let stopBtn = document.createElement("button");
        stopBtn.innerHTML = "Stop";
        stopBtn.className = "btn btn-stop";
        
        let resetBtn = document.createElement("button");
        resetBtn.innerHTML = "Reset";
        resetBtn.className = "btn btn-reset";
        
        // Format time helper
        function formatTime(totalSeconds) {
            let hours = Math.floor(totalSeconds / 3600);
            let minutes = Math.floor((totalSeconds % 3600) / 60);
            let seconds = totalSeconds % 60;
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Get total seconds from inputs
        function getTotalSecondsFromInputs() {
            let hours = parseInt(hoursInput.value) || 0;
            let minutes = parseInt(minutesInput.value) || 0;
            let seconds = parseInt(secondsInput.value) || 0;
            return hours * 3600 + minutes * 60 + seconds;
        }
        
        // Update display
        function updateDisplay() {
            let remaining = model.get("remaining_time");
            display.innerHTML = formatTime(remaining);
            
            // Change color when time is low
            if (remaining <= 10 && remaining > 0) {
                display.className = "timer-display warning";
            } else if (remaining === 0) {
                display.className = "timer-display finished";
                display.innerHTML = "TIME'S UP!";
            } else {
                display.className = "timer-display";
            }
        }
        
        // Update inputs based on remaining time (when not running)
        function updateInputs() {
            if (!model.get("is_running")) {
                let totalSeconds = model.get("remaining_time");
                let hours = Math.floor(totalSeconds / 3600);
                let minutes = Math.floor((totalSeconds % 3600) / 60);
                let seconds = totalSeconds % 60;
                
                hoursInput.value = hours;
                minutesInput.value = minutes;
                secondsInput.value = seconds;
            }
        }
        
        // Start timer
        function startTimer() {
            if (!intervalId) {
                let totalSeconds = model.get("remaining_time");
                if (totalSeconds <= 0) {
                    totalSeconds = getTotalSecondsFromInputs();
                    model.set("remaining_time", totalSeconds);
                    model.save_changes();
                }
                
                if (totalSeconds > 0) {
                    endTime = Date.now() + (totalSeconds * 1000);
                    intervalId = setInterval(() => {
                        // Safety check - ensure we're still supposed to be running
                        if (!model.get("is_running")) {
                            clearInterval(intervalId);
                            intervalId = null;
                            return;
                        }
                        
                        let now = Date.now();
                        let remaining = Math.max(0, Math.ceil((endTime - now) / 1000));
                        
                        model.set("remaining_time", remaining);
                        model.save_changes();
                        
                        if (remaining === 0) {
                            clearInterval(intervalId);
                            intervalId = null;
                            model.set("is_running", false);
                            model.save_changes();
                            // Play sound and show alert when timer reaches zero
                            playBeep();
                            setTimeout(() => {
                                alert("⏰ Timer finished!");
                            }, 100);
                        }
                    }, 100); // Update every 100ms
                    
                    model.set("is_running", true);
                    model.save_changes();
                }
            }
        }
        
        // Stop timer
        function stopTimer() {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
                model.set("is_running", false);
                model.save_changes();
            }
        }
        
        // Reset timer
        function resetTimer() {
            // Always clear interval first
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
            let totalSeconds = model.get("initial_time");
            model.set("remaining_time", totalSeconds);
            model.set("is_running", false);
            model.save_changes();
        }
        
        // Event listeners
        startBtn.addEventListener("click", startTimer);
        stopBtn.addEventListener("click", stopTimer);
        resetBtn.addEventListener("click", resetTimer);
        
        // Update timer when inputs change
        [hoursInput, minutesInput, secondsInput].forEach(input => {
            input.addEventListener("change", () => {
                if (!model.get("is_running")) {
                    let totalSeconds = getTotalSecondsFromInputs();
                    model.set("initial_time", totalSeconds);
                    model.set("remaining_time", totalSeconds);
                    model.save_changes();
                }
            });
        });
        
        // Model change listeners
        model.on("change:remaining_time", updateDisplay);
        
        model.on("change:initial_time", () => {
            if (!model.get("is_running")) {
                let totalSeconds = model.get("initial_time");
                model.set("remaining_time", totalSeconds);
                model.save_changes();
                updateInputs();
            }
        });
        
        // Listen for programmatic start/stop/reset from Python
        model.on("change:is_running", () => {
            let isRunning = model.get("is_running");
            
            if (isRunning && !intervalId) {
                // Start timer programmatically
                let totalSeconds = model.get("remaining_time");
                if (totalSeconds > 0) {
                    endTime = Date.now() + (totalSeconds * 1000);
                    intervalId = setInterval(() => {
                        // Safety check - ensure we're still supposed to be running
                        if (!model.get("is_running")) {
                            clearInterval(intervalId);
                            intervalId = null;
                            return;
                        }
                        
                        let now = Date.now();
                        let remaining = Math.max(0, Math.ceil((endTime - now) / 1000));
                        
                        model.set("remaining_time", remaining);
                        model.save_changes();
                        
                        if (remaining === 0) {
                            clearInterval(intervalId);
                            intervalId = null;
                            model.set("is_running", false);
                            model.save_changes();
                            // Play sound and show alert when timer reaches zero
                            playBeep();
                            setTimeout(() => {
                                alert("⏰ Timer finished!");
                            }, 100);
                        }
                    }, 100);
                }
            } else if (!isRunning && intervalId) {
                // Stop timer programmatically - force clear
                clearInterval(intervalId);
                intervalId = null;
            }
            
            // Update button states
            if (isRunning) {
                startBtn.classList.add("disabled");
            } else {
                startBtn.classList.remove("disabled");
            }
            startBtn.disabled = isRunning;
            
            // Disable inputs when running
            [hoursInput, minutesInput, secondsInput].forEach(input => {
                input.disabled = isRunning;
                if (isRunning) {
                    input.classList.add("disabled");
                } else {
                    input.classList.remove("disabled");
                }
            });
        });
        
        // Initialize display and inputs
        updateDisplay();
        updateInputs();
        
        // Set initial button states
        let isRunning = model.get("is_running");
        startBtn.disabled = isRunning;
        if (isRunning) {
            startBtn.classList.add("disabled");
        }
        
        // Assemble the widget
        inputContainer.appendChild(hoursInput);
        inputContainer.appendChild(colon1);
        inputContainer.appendChild(minutesInput);
        inputContainer.appendChild(colon2);
        inputContainer.appendChild(secondsInput);
        
        inputSection.appendChild(inputLabel);
        inputSection.appendChild(inputContainer);
        
        buttonContainer.appendChild(startBtn);
        buttonContainer.appendChild(stopBtn);
        buttonContainer.appendChild(resetBtn);
        
        container.appendChild(inputSection);
        container.appendChild(display);
        container.appendChild(buttonContainer);
        el.appendChild(container);
        
        // Cleanup function
        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }
    export default { render };
    """
    
    _css = """
    .timer-container {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        text-align: center;
        padding: 32px 24px;
        border-radius: 16px;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(226, 232, 240, 0.8);
        display: inline-block;
        min-width: 320px;
        position: relative;
        transition: all 0.3s ease;
    }

    .timer-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
        pointer-events: none;
    }
    
    .input-section {
        margin-bottom: 24px;
        position: relative;
        z-index: 1;
    }
    
    .input-label {
        margin-bottom: 12px;
        font-weight: 600;
        color: #475569;
        font-size: 14px;
    }
    
    .input-container {
        display: flex;
        gap: 8px;
        justify-content: center;
        align-items: center;
    }
    
    .time-input {
        width: 60px;
        text-align: center;
        padding: 10px 8px;
        border: 2px solid rgba(226, 232, 240, 0.8);
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.8);
        color: #1e293b;
        transition: all 0.2s ease;
        backdrop-filter: blur(10px);
    }
    
    .time-input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .time-input.disabled {
        opacity: 0.5;
        cursor: not-allowed;
        background: rgba(248, 250, 252, 0.5);
    }
    
    .colon {
        font-weight: bold;
        font-size: 20px;
        color: #64748b;
    }
    
    .timer-display {
        font-size: 48px;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
        margin: 24px 0;
        color: #1e293b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
        transition: all 0.3s ease;
    }
    
    .timer-display.warning {
        color: #dc2626;
        animation: pulse 1s infinite;
    }
    
    .timer-display.finished {
        color: #dc2626;
        font-size: 28px;
        animation: bounce 0.5s ease-in-out;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    .button-container {
        display: flex;
        gap: 12px;
        justify-content: center;
        position: relative;
        z-index: 1;
    }
    
    .btn {
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        color: white;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
    }


    .btn::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.6s;
    }

    .btn:hover:not(.disabled)::before {
        left: 100%;
    }
    
    .btn.disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
    }
    
    .btn-start {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: 1px solid rgba(5, 150, 105, 0.3);
    }
    
    .btn-start:hover:not(.disabled) {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(5, 150, 105, 0.3);
    }
    
    .btn-stop {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: 1px solid rgba(220, 38, 38, 0.3);
    }
    
    .btn-stop:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(220, 38, 38, 0.3);
    }
    
    .btn-reset {
        background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        border: 1px solid rgba(75, 85, 99, 0.3);
    }
    
    .btn-reset:hover {
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(75, 85, 99, 0.3);
    }

    .btn:active:not(.disabled) {
        transform: translateY(0);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }

    /* Manual dark mode - takes precedence over system preference */
    .timer-container[data-theme="dark"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(51, 65, 85, 0.8);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.3),
            0 2px 4px -1px rgba(0, 0, 0, 0.2);
    }
    
    .timer-container[data-theme="dark"]::before {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
    }

    .timer-container[data-theme="dark"] .input-label {
        color: #cbd5e1;
    }

    .timer-container[data-theme="dark"] .time-input {
        background: rgba(30, 41, 59, 0.8);
        border: 2px solid rgba(51, 65, 85, 0.8);
        color: #f1f5f9;
    }

    .timer-container[data-theme="dark"] .time-input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    .timer-container[data-theme="dark"] .time-input.disabled {
        background: rgba(15, 23, 42, 0.5);
        color: #64748b;
    }

    .timer-container[data-theme="dark"] .colon {
        color: #94a3b8;
    }
    
    .timer-container[data-theme="dark"] .timer-display {
        color: #f1f5f9;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    .timer-container[data-theme="dark"] .btn {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .timer-container[data-theme="dark"] .btn-start {
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
        border: 1px solid rgba(6, 95, 70, 0.5);
    }
    
    .timer-container[data-theme="dark"] .btn-start:hover:not(.disabled) {
        background: linear-gradient(135deg, #047857 0%, #065f46 100%);
        box-shadow: 0 4px 8px rgba(6, 95, 70, 0.4);
    }
    
    .timer-container[data-theme="dark"] .btn-stop {
        background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
        border: 1px solid rgba(153, 27, 27, 0.5);
    }
    
    .timer-container[data-theme="dark"] .btn-stop:hover {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
        box-shadow: 0 4px 8px rgba(153, 27, 27, 0.4);
    }
    
    .timer-container[data-theme="dark"] .btn-reset {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
        border: 1px solid rgba(55, 65, 81, 0.5);
    }
    
    .timer-container[data-theme="dark"] .btn-reset:hover {
        background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
        box-shadow: 0 4px 8px rgba(55, 65, 81, 0.4);
    }

    /* Manual light mode - overrides system preference */
    .timer-container[data-theme="light"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1),
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .timer-container[data-theme="light"]::before {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%);
    }
    
    .timer-container[data-theme="light"] .timer-display {
        color: #1e293b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    /* Auto mode - follows system preference */
    .timer-container[data-theme="auto"] {
        /* Light mode styles by default */
    }

    @media (prefers-color-scheme: dark) {
        .timer-container[data-theme="auto"] {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(51, 65, 85, 0.8);
            box-shadow: 
                0 4px 6px -1px rgba(0, 0, 0, 0.3),
                0 2px 4px -1px rgba(0, 0, 0, 0.2);
        }
        
        .timer-container[data-theme="auto"]::before {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
        }

        .timer-container[data-theme="auto"] .input-label {
            color: #cbd5e1;
        }

        .timer-container[data-theme="auto"] .time-input {
            background: rgba(30, 41, 59, 0.8);
            border: 2px solid rgba(51, 65, 85, 0.8);
            color: #f1f5f9;
        }

        .timer-container[data-theme="auto"] .time-input:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }

        .timer-container[data-theme="auto"] .time-input.disabled {
            background: rgba(15, 23, 42, 0.5);
            color: #64748b;
        }

        .timer-container[data-theme="auto"] .colon {
            color: #94a3b8;
        }
        
        .timer-container[data-theme="auto"] .timer-display {
            color: #f1f5f9;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .timer-container[data-theme="auto"] .btn {
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .timer-container[data-theme="auto"] .btn-start {
            background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
            border: 1px solid rgba(6, 95, 70, 0.5);
        }
        
        .timer-container[data-theme="auto"] .btn-start:hover:not(.disabled) {
            background: linear-gradient(135deg, #047857 0%, #065f46 100%);
            box-shadow: 0 4px 8px rgba(6, 95, 70, 0.4);
        }
        
        .timer-container[data-theme="auto"] .btn-stop {
            background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
            border: 1px solid rgba(153, 27, 27, 0.5);
        }
        
        .timer-container[data-theme="auto"] .btn-stop:hover {
            background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
            box-shadow: 0 4px 8px rgba(153, 27, 27, 0.4);
        }
        
        .timer-container[data-theme="auto"] .btn-reset {
            background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
            border: 1px solid rgba(55, 65, 81, 0.5);
        }
        
        .timer-container[data-theme="auto"] .btn-reset:hover {
            background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
            box-shadow: 0 4px 8px rgba(55, 65, 81, 0.4);
        }
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .timer-container,
        .btn,
        .btn::before,
        .timer-display {
            transition: none;
            animation: none;
        }
        
        .btn:hover {
            transform: none;
        }
    }
    """
    
    remaining_time = traitlets.Int(300).tag(sync=True)  # Remaining time in seconds
    is_running = traitlets.Bool(False).tag(sync=True)  # Timer state
    initial_time = traitlets.Int(300).tag(sync=True)  # Initial time in seconds (default 5 minutes)
    theme = traitlets.Unicode('auto').tag(sync=True)  # Theme preference: 'light', 'dark', 'auto'
    
    def __init__(self, initial_time=300, **kwargs):
        """Initialize the timer widget with optional initial time"""
        # Set the initial_time first
        kwargs['initial_time'] = initial_time
        # Also set remaining_time to match initial_time
        kwargs['remaining_time'] = initial_time
        super().__init__(**kwargs)
    
    def set_time(self, hours=0, minutes=0, seconds=0):
        """Set the timer time programmatically"""
        total_seconds = hours * 3600 + minutes * 60 + seconds
        self.initial_time = total_seconds
        if not self.is_running:
            self.remaining_time = total_seconds
    
    def start(self):
        """Start the timer programmatically"""
        if not self.is_running and self.remaining_time > 0:
            self.is_running = True
    
    def stop(self):
        """Stop the timer programmatically"""
        if self.is_running:
            self.is_running = False
    
    def reset(self):
        """Reset the timer programmatically"""
        was_running = self.is_running
        self.is_running = False
        self.remaining_time = self.initial_time
        # If it wasn't running, we still need to trigger an update
        if not was_running:
            # Force a state change to trigger frontend update
            self.remaining_time = self.initial_time  # This will trigger the change event