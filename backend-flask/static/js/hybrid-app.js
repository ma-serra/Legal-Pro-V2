// ==========================================
// MAIN APPLICATION CLASS
// ==========================================
class VoiceMindApp {
  constructor() {
    this.transcriptionEngine = new HybridTranscriptionEngine();
    this.currentTranscription = null;
    this.isRecording = false;
    this.mediaRecorder = null;
    this.recordedChunks = [];
    
    this.initializeUI();
    this.setupEventListeners();
    
    console.log('🚀 VoiceMind Hybrid System Ready!');
  }

  initializeUI() {
    // Set up progress bar
    this.progressBar = document.getElementById('progress-bar');
    this.progressText = document.getElementById('progress-text');
    
    // Set up result display
    this.resultContainer = document.getElementById('transcription-result');
    this.confidenceDisplay = document.getElementById('confidence-display');
    
    // Set up controls
    this.fileInput = document.getElementById('file-input');
    this.recordButton = document.getElementById('record-button');
    this.stopButton = document.getElementById('stop-button');
    this.clearButton = document.getElementById('clear-button');
    
    // Setup progress callback
    this.transcriptionEngine.setProgressCallback((percent, status) => {
      this.updateProgressDisplay(percent, status);
    });
  }

  setupEventListeners() {
    // File upload
    this.fileInput?.addEventListener('change', (e) => this.handleFileUpload(e));
    
    // Recording controls
    this.recordButton?.addEventListener('click', () => this.startRecording());
    this.stopButton?.addEventListener('click', () => this.stopRecording());
    this.clearButton?.addEventListener('click', () => this.clearResults());
    
    // API key configuration
    document.getElementById('save-keys')?.addEventListener('click', () => this.saveApiKeys());
    
    // Engine selection
    document.getElementById('engine-select')?.addEventListener('change', (e) => {
      this.transcriptionEngine.config.preferredEngine = e.target.value;
    });
    
    // Export buttons
    document.getElementById('export-docx')?.addEventListener('click', () => this.exportResults('docx'));
    document.getElementById('export-pdf')?.addEventListener('click', () => this.exportResults('pdf'));
  }

  async handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
      this.showProgress(true);
      this.updateProgressDisplay(0, 'Iniciando transcrição híbrida...');
      
      const result = await this.transcriptionEngine.transcribe(file, {
        includeWordTimestamps: true,
        enablePunctuation: true
      });

      this.displayResults(result);
      this.showNotification('Transcrição concluída com sucesso!', 'success');
      
    } catch (error) {
      this.showError(`Erro na transcrição: ${error.message}`);
      this.showNotification('Erro na transcrição', 'error');
    } finally {
      this.showProgress(false);
    }
  }

  async startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 48000
        } 
      });

      this.isRecording = true;
      this.recordedChunks = [];
      
      // Setup MediaRecorder for buffering
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.recordedChunks, { 
          type: 'audio/webm;codecs=opus' 
        });
        
        // Process recorded audio with hybrid engine
        try {
          this.showProgress(true);
          const result = await this.transcriptionEngine.transcribe(audioBlob);
          this.displayResults(result);
          this.showNotification('Gravação processada com sucesso!', 'success');
        } catch (error) {
          this.showError(`Erro no processamento: ${error.message}`);
        } finally {
          this.showProgress(false);
        }
      };

      // Start real-time transcription with Web Speech API
      this.transcriptionEngine.transcribe(stream, {
        realTime: true,
        continuous: true,
        interimResults: true,
        onResult: (result) => this.updateRealTimeResults(result),
        onError: (error) => console.warn('Real-time error:', error)
      });

      this.mediaRecorder.start(1000); // Collect data every second
      this.updateRecordingUI(true);
      this.showNotification('Gravação iniciada', 'info');

    } catch (error) {
      this.showError(`Erro ao acessar microfone: ${error.message}`);
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      
      // Stop Web Speech API
      if (this.transcriptionEngine.webSpeechEngine.recognition) {
        this.transcriptionEngine.webSpeechEngine.stop();
      }
      
      this.updateRecordingUI(false);
      this.showNotification('Gravação finalizada', 'info');
    }
  }

  updateRealTimeResults(result) {
    const realTimeContainer = document.getElementById('realtime-transcription');
    if (realTimeContainer) {
      realTimeContainer.innerHTML = `
        <div class="real-time-result">
          <div class="final-text">${result.finalTranscript}</div>
          <div class="interim-text text-muted">${result.interimTranscript}</div>
        </div>
      `;
    }
  }

  displayResults(result) {
    this.currentTranscription = result;
    
    // Main transcription text
    const textArea = document.getElementById('transcription-text');
    if (textArea) {
      textArea.value = result.text;
    }

    // Confidence and metadata
    this.updateMetadataDisplay(result);
    
    // Segments timeline (if available)
    this.updateSegmentsDisplay(result.segments);
    
    // Show result container
    if (this.resultContainer) {
      this.resultContainer.classList.remove('hidden');
    }
  }

  updateMetadataDisplay(result) {
    const metadataContainer = document.getElementById('metadata-display');
    if (!metadataContainer) return;

    const engineUsed = result.engine || 'unknown';
    const confidence = ((result.confidence || 0) * 100).toFixed(1);
    const duration = result.metadata?.processingTime || 0;
    const repetitionFixes = result.video_info?.repetition_fixes_applied || 0;

    metadataContainer.innerHTML = `
      <div class="row">
        <div class="col-md-3">
          <div class="stat-card">
            <i class="fas fa-microchip"></i>
            <div class="stat-value">${engineUsed.toUpperCase()}</div>
            <div class="stat-label">Engine Usado</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <i class="fas fa-percent"></i>
            <div class="stat-value">${confidence}%</div>
            <div class="stat-label">Confiança</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <i class="fas fa-clock"></i>
            <div class="stat-value">${(duration / 1000).toFixed(1)}s</div>
            <div class="stat-label">Tempo</div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="stat-card">
            <i class="fas fa-magic"></i>
            <div class="stat-value">${repetitionFixes}</div>
            <div class="stat-label">Correções</div>
          </div>
        </div>
      </div>
    `;

    // Show alternatives if available
    if (result.metadata?.alternatives?.length > 0) {
      this.displayAlternatives(result.metadata.alternatives);
    }
  }

  updateSegmentsDisplay(segments) {
    const segmentsContainer = document.getElementById('segments-display');
    if (!segmentsContainer || !segments) return;

    const segmentsList = segments.map((segment, index) => `
      <div class="segment-item" data-start="${segment.startTime || segment.start_time}" data-end="${segment.endTime || segment.end_time}">
        <div class="segment-time">
          ${this.formatTime(segment.startTime || segment.start_time)} - ${this.formatTime(segment.endTime || segment.end_time)}
        </div>
        <div class="segment-text">${segment.text}</div>
        <div class="segment-confidence">
          <span class="badge ${this.getConfidenceBadgeClass(segment.confidence)}">
            ${((segment.confidence || 0) * 100).toFixed(1)}%
          </span>
        </div>
      </div>
    `).join('');

    segmentsContainer.innerHTML = `
      <h5>Segmentos da Transcrição</h5>
      <div class="segments-list">${segmentsList}</div>
    `;
  }

  displayAlternatives(alternatives) {
    const alternativesContainer = document.getElementById('alternatives-display');
    if (!alternativesContainer) return;

    const alternativesList = alternatives.map((alt, index) => `
      <div class="alternative-option" data-index="${index}">
        <div class="alternative-text">${alt.text}</div>
        <div class="alternative-engine">
          <span class="badge badge-info">${alt.engine}</span>
          <span class="badge badge-secondary">${((alt.confidence || 0) * 100).toFixed(1)}%</span>
        </div>
      </div>
    `).join('');

    alternativesContainer.innerHTML = `
      <h5>Resultados Alternativos</h5>
      <div class="alternatives-list">${alternativesList}</div>
    `;
  }

  saveApiKeys() {
    const whisperKey = document.getElementById('whisper-api-key')?.value;
    const googleKey = document.getElementById('google-api-key')?.value;
    
    this.transcriptionEngine.setApiKeys(whisperKey, googleKey);
    
    // Save to localStorage
    if (whisperKey) localStorage.setItem('whisper-api-key', whisperKey);
    if (googleKey) localStorage.setItem('google-api-key', googleKey);
    
    this.showNotification('Chaves de API salvas com sucesso!', 'success');
  }

  loadApiKeys() {
    const whisperKey = localStorage.getItem('whisper-api-key');
    const googleKey = localStorage.getItem('google-api-key');
    
    if (whisperKey) {
      document.getElementById('whisper-api-key').value = whisperKey;
    }
    if (googleKey) {
      document.getElementById('google-api-key').value = googleKey;
    }
    
    this.transcriptionEngine.setApiKeys(whisperKey, googleKey);
  }

  async exportResults(format) {
    if (!this.currentTranscription) {
      this.showNotification('Nenhuma transcrição disponível para exportar', 'warning');
      return;
    }

    try {
      const response = await fetch('/video/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcription: this.currentTranscription,
          format: format
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcricao_${new Date().toISOString().slice(0, 10)}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showNotification(`Arquivo ${format.toUpperCase()} exportado com sucesso!`, 'success');
      } else {
        throw new Error('Erro ao exportar arquivo');
      }
    } catch (error) {
      this.showError(`Erro na exportação: ${error.message}`);
    }
  }

  clearResults() {
    this.currentTranscription = null;
    
    const textArea = document.getElementById('transcription-text');
    if (textArea) textArea.value = '';
    
    const realTimeContainer = document.getElementById('realtime-transcription');
    if (realTimeContainer) realTimeContainer.innerHTML = '';
    
    if (this.resultContainer) {
      this.resultContainer.classList.add('hidden');
    }
    
    this.showNotification('Resultados limpos', 'info');
  }

  updateProgressDisplay(percent, status) {
    if (this.progressBar) {
      this.progressBar.style.width = `${percent}%`;
      this.progressBar.setAttribute('aria-valuenow', percent);
    }
    
    if (this.progressText) {
      this.progressText.textContent = status;
    }
  }

  updateRecordingUI(recording) {
    if (this.recordButton) {
      this.recordButton.disabled = recording;
      this.recordButton.innerHTML = recording ? 
        '<i class="fas fa-microphone-slash"></i> Gravando...' : 
        '<i class="fas fa-microphone"></i> Iniciar Gravação';
    }
    
    if (this.stopButton) {
      this.stopButton.disabled = !recording;
    }
  }

  showProgress(show) {
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
      progressContainer.style.display = show ? 'block' : 'none';
    }
  }

  showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 5000);
  }

  showError(message) {
    this.showNotification(message, 'danger');
    console.error('App Error:', message);
  }

  formatTime(seconds) {
    if (!seconds) return '00:00';
    
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  getConfidenceBadgeClass(confidence) {
    if (confidence > 0.8) return 'badge-success';
    if (confidence > 0.6) return 'badge-warning';
    return 'badge-danger';
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new VoiceMindApp();
  
  // Load saved API keys
  app.loadApiKeys();
  
  // Make app globally available for debugging
  window.voiceMindApp = app;
});