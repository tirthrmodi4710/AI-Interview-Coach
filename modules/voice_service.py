def get_voice_component():
    """
    Returns an HTML/JS component that uses the Web Speech API.
    Records the user's voice in the browser and returns the transcript
    via a hidden Streamlit text input.
    Works best in Chrome and Edge.
    """

    html = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        .voice-container {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            padding: 24px 28px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            transition: all 0.2s ease;
            margin: 8px 0;
        }

        .voice-container:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border-color: #D1D5DB;
        }

        .voice-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .voice-title {
            font-size: 14px;
            font-weight: 600;
            color: #111827;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .voice-title-icon {
            font-size: 18px;
        }

        .voice-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 99px;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
            background: #F1F5F9;
            color: #6B7280;
            border: 1px solid #E5E7EB;
        }

        .voice-status-badge.idle {
            background: #F1F5F9;
            color: #6B7280;
            border-color: #E5E7EB;
        }

        .voice-status-badge.recording {
            background: #FEF2F2;
            color: #991B1B;
            border-color: #FCA5A5;
            animation: pulseBadge 1.2s ease-in-out infinite;
        }

        .voice-status-badge.success {
            background: #ECFDF5;
            color: #065F46;
            border-color: #A7F3D0;
        }

        .voice-status-badge.error {
            background: #FEF2F2;
            color: #991B1B;
            border-color: #FCA5A5;
        }

        @keyframes pulseBadge {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            transition: all 0.3s ease;
            background: #9CA3AF;
        }

        .status-dot.idle {
            background: #9CA3AF;
        }

        .status-dot.recording {
            background: #EF4444;
            animation: blink 1.2s ease-in-out infinite;
        }

        .status-dot.success {
            background: #10B981;
        }

        .status-dot.error {
            background: #EF4444;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.3; transform: scale(0.8); }
        }

        .voice-controls {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        .voice-btn {
            padding: 10px 24px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }

        .voice-btn::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .voice-btn:hover::before {
            opacity: 1;
        }

        .voice-btn:active {
            transform: scale(0.97);
        }

        .voice-btn-start {
            background: #2563EB;
            color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
        }

        .voice-btn-start:hover:not(:disabled) {
            background: #1E40AF;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
        }

        .voice-btn-start:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }

        .voice-btn-start:disabled::before {
            display: none;
        }

        .voice-btn-stop {
            background: #F1F5F9;
            color: #111827;
            border: 1px solid #E5E7EB;
        }

        .voice-btn-stop:hover:not(:disabled) {
            background: #E5E7EB;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }

        .voice-btn-stop:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }

        .voice-btn-stop:disabled::before {
            display: none;
        }

        .voice-btn-success {
            background: #10B981;
            color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(16, 185, 129, 0.12);
        }

        .voice-btn-success:hover:not(:disabled) {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(16, 185, 129, 0.25);
        }

        .voice-btn-success:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }

        .voice-btn-success:disabled::before {
            display: none;
        }

        .voice-status-text {
            font-size: 13px;
            color: #6B7280;
            margin: 0 0 12px 0;
            padding: 8px 16px;
            background: #F8FAFC;
            border-radius: 8px;
            border: 1px solid #F1F5F9;
            transition: all 0.3s ease;
            min-height: 40px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .voice-status-text.recording {
            background: #FEF2F2;
            border-color: #FCA5A5;
            color: #991B1B;
        }

        .voice-status-text.success {
            background: #ECFDF5;
            border-color: #A7F3D0;
            color: #065F46;
        }

        .voice-status-text.error {
            background: #FEF2F2;
            border-color: #FCA5A5;
            color: #991B1B;
        }

        .voice-transcript-container {
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 16px 20px;
            min-height: 60px;
            max-height: 180px;
            overflow-y: auto;
            transition: all 0.3s ease;
            margin-top: 4px;
        }

        .voice-transcript-container:empty::before {
            content: 'Transcript will appear here...';
            color: #9CA3AF;
            font-size: 13px;
        }

        .voice-transcript-container.active {
            border-color: #2563EB;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.05);
        }

        .voice-transcript-text {
            font-size: 14px;
            line-height: 1.7;
            color: #111827;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .voice-transcript-text:empty {
            color: #9CA3AF;
            font-size: 13px;
        }

        .voice-transcript-text:empty::before {
            content: 'Transcript will appear here...';
            color: #9CA3AF;
            font-size: 13px;
        }

        .voice-transcript-container::-webkit-scrollbar {
            width: 4px;
        }

        .voice-transcript-container::-webkit-scrollbar-track {
            background: #F1F5F9;
            border-radius: 2px;
        }

        .voice-transcript-container::-webkit-scrollbar-thumb {
            background: #2563EB;
            border-radius: 2px;
        }

        .voice-transcript-container::-webkit-scrollbar-thumb:hover {
            background: #1E40AF;
        }

        .voice-actions {
            display: flex;
            gap: 10px;
            margin-top: 12px;
            flex-wrap: wrap;
        }

        .voice-action-btn {
            padding: 8px 20px;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-flex;
            align-items: center;
            gap: 6px;
            position: relative;
            overflow: hidden;
        }

        .voice-action-btn::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .voice-action-btn:hover::before {
            opacity: 1;
        }

        .voice-action-btn:active {
            transform: scale(0.97);
        }

        .voice-action-btn-primary {
            background: #2563EB;
            color: #FFFFFF;
            box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12);
        }

        .voice-action-btn-primary:hover:not(:disabled) {
            background: #1E40AF;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
        }

        .voice-action-btn-primary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
            box-shadow: none !important;
        }

        .voice-action-btn-primary:disabled::before {
            display: none;
        }

        .voice-action-btn-secondary {
            background: #F1F5F9;
            color: #111827;
            border: 1px solid #E5E7EB;
        }

        .voice-action-btn-secondary:hover:not(:disabled) {
            background: #E5E7EB;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }

        .voice-action-btn-secondary:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }

        .voice-action-btn-secondary:disabled::before {
            display: none;
        }

        @media (max-width: 768px) {
            .voice-container {
                padding: 16px 18px;
            }

            .voice-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }

            .voice-controls {
                flex-direction: column;
                width: 100%;
            }

            .voice-btn {
                width: 100%;
                justify-content: center;
                padding: 12px 20px;
            }

            .voice-actions {
                flex-direction: column;
                width: 100%;
            }

            .voice-action-btn {
                width: 100%;
                justify-content: center;
                padding: 10px 16px;
            }

            .voice-status-text {
                font-size: 12px;
                padding: 6px 12px;
                min-height: 32px;
            }

            .voice-transcript-container {
                padding: 12px 14px;
                min-height: 50px;
                max-height: 140px;
            }

            .voice-transcript-text {
                font-size: 13px;
            }
        }

        @media (max-width: 480px) {
            .voice-container {
                padding: 12px 14px;
            }

            .voice-title {
                font-size: 13px;
            }

            .voice-status-badge {
                font-size: 11px;
                padding: 4px 10px;
            }

            .voice-btn {
                font-size: 13px;
                padding: 10px 16px;
            }

            .voice-action-btn {
                font-size: 12px;
                padding: 8px 14px;
            }

            .voice-transcript-container {
                padding: 10px 12px;
                min-height: 40px;
                max-height: 120px;
            }

            .voice-transcript-text {
                font-size: 12px;
            }
        }
    </style>

    <div class="voice-container">
        <div class="voice-header">
            <div class="voice-title">
                <span class="voice-title-icon">🎤</span>
                Voice Recording
            </div>
            <div class="voice-status-badge idle" id="statusBadge">
                <span class="status-dot idle" id="statusDot"></span>
                <span id="badgeText">Idle</span>
            </div>
        </div>

        <div class="voice-controls">
            <button
                class="voice-btn voice-btn-start"
                id="startBtn"
                onclick="startRecording()"
            >
                🎙️ Start Recording
            </button>

            <button
                class="voice-btn voice-btn-stop"
                id="stopBtn"
                onclick="stopRecording()"
                disabled
            >
                ⏹ Stop Recording
            </button>
        </div>

        <div class="voice-status-text" id="statusText">
            <span>💡</span>
            <span>Click "Start Recording" and speak your answer clearly.</span>
        </div>

        <div class="voice-transcript-container" id="transcriptContainer">
            <div class="voice-transcript-text" id="transcriptText"></div>
        </div>

        <div class="voice-actions" id="actionsContainer" style="display: none;">
            <button
                class="voice-action-btn voice-action-btn-primary"
                id="useTranscriptBtn"
                onclick="useTranscript()"
            >
                ✓ Use This Answer
            </button>
            <button
                class="voice-action-btn voice-action-btn-secondary"
                id="clearTranscriptBtn"
                onclick="clearTranscript()"
            >
                ✕ Clear
            </button>
        </div>

        <input type="hidden" id="transcriptOutput" />
    </div>

    <script>
        let recognition;
        let finalTranscript = "";
        let isRecording = false;

        function updateUIState(state, message) {
            const badge = document.getElementById('statusBadge');
            const dot = document.getElementById('statusDot');
            const badgeText = document.getElementById('badgeText');
            const statusText = document.getElementById('statusText');
            const transcriptContainer = document.getElementById('transcriptContainer');
            const actionsContainer = document.getElementById('actionsContainer');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');

            // Reset classes
            badge.className = 'voice-status-badge';
            dot.className = 'status-dot';
            statusText.className = 'voice-status-text';

            switch(state) {
                case 'idle':
                    badge.classList.add('idle');
                    dot.classList.add('idle');
                    badgeText.textContent = 'Idle';
                    statusText.classList.add('idle');
                    statusText.innerHTML = '<span>💡</span><span>Click "Start Recording" and speak your answer clearly.</span>';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    transcriptContainer.classList.remove('active');
                    actionsContainer.style.display = 'none';
                    break;

                case 'recording':
                    badge.classList.add('recording');
                    dot.classList.add('recording');
                    badgeText.textContent = 'Recording';
                    statusText.classList.add('recording');
                    statusText.innerHTML = '<span>🔴</span><span>Recording in progress... Speak now.</span>';
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                    transcriptContainer.classList.add('active');
                    break;

                case 'success':
                    badge.classList.add('success');
                    dot.classList.add('success');
                    badgeText.textContent = 'Complete';
                    statusText.classList.add('success');
                    statusText.innerHTML = '<span>✅</span><span>Recording complete! Review your transcript below.</span>';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    transcriptContainer.classList.remove('active');
                    actionsContainer.style.display = 'flex';
                    break;

                case 'error':
                    badge.classList.add('error');
                    dot.classList.add('error');
                    badgeText.textContent = 'Error';
                    statusText.classList.add('error');
                    statusText.innerHTML = '<span>❌</span><span>' + message + '</span>';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    transcriptContainer.classList.remove('active');
                    actionsContainer.style.display = 'none';
                    break;

                case 'no-speech':
                    badge.classList.add('error');
                    dot.classList.add('error');
                    badgeText.textContent = 'No Speech';
                    statusText.classList.add('error');
                    statusText.innerHTML = '<span>⚠️</span><span>No speech detected. Please try again.</span>';
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    transcriptContainer.classList.remove('active');
                    actionsContainer.style.display = 'none';
                    break;
            }
        }

        function updateTranscript(text) {
            const transcriptText = document.getElementById('transcriptText');
            transcriptText.textContent = text;
            if (text) {
                document.getElementById('transcriptContainer').classList.add('active');
            }
        }

        function startRecording() {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                updateUIState('error', 'Speech recognition not supported. Please use Chrome or Edge.');
                return;
            }

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = "en-US";

            finalTranscript = "";
            isRecording = true;

            recognition.onstart = function() {
                updateUIState('recording');
                updateTranscript('');
            };

            recognition.onresult = function(event) {
                let interimTranscript = "";

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + " ";
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                const displayText = finalTranscript + interimTranscript;
                updateTranscript(displayText);
            };

            recognition.onerror = function(event) {
                if (event.error === 'no-speech') {
                    updateUIState('no-speech');
                } else {
                    updateUIState('error', 'Error: ' + event.error + '. Please try again.');
                }
                isRecording = false;
            };

            recognition.onend = function() {
                if (isRecording) {
                    if (finalTranscript.trim()) {
                        updateUIState('success');
                        document.getElementById('transcriptOutput').value = finalTranscript.trim();
                    } else {
                        updateUIState('no-speech');
                    }
                }
                isRecording = false;
            };

            recognition.start();
        }

        function stopRecording() {
            if (recognition) {
                isRecording = false;
                recognition.stop();
            }
        }

        function useTranscript() {
            const transcript = document.getElementById('transcriptOutput').value;
            if (transcript) {
                // Find the Streamlit text input and set its value
                const textInputs = window.parent.document.querySelectorAll('textarea');
                for (let input of textInputs) {
                    if (input.placeholder && input.placeholder.includes('Type your answer')) {
                        input.value = transcript;
                        // Trigger input event for Streamlit
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        break;
                    }
                }
                // Also try to find by common class
                const streamlitTextareas = window.parent.document.querySelectorAll('[data-testid="stTextArea"] textarea');
                for (let textarea of streamlitTextareas) {
                    if (textarea.placeholder && textarea.placeholder.includes('Type your answer')) {
                        textarea.value = transcript;
                        textarea.dispatchEvent(new Event('input', { bubbles: true }));
                        break;
                    }
                }
                updateUIState('idle');
                updateTranscript('');
                document.getElementById('transcriptOutput').value = '';
            }
        }

        function clearTranscript() {
            finalTranscript = "";
            updateTranscript('');
            document.getElementById('transcriptOutput').value = '';
            updateUIState('idle');
        }

        // Initialize with idle state
        updateUIState('idle');
    </script>
    """

    return html