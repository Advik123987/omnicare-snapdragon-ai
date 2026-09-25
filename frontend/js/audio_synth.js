/**
 * OmniCare AI - Clinical Web Audio API Pulmonary Acoustics Synthesizer
 * Generates clinically authentic acoustic simulations of human respiratory sounds:
 * - Normal Vesicular Breath Sound (100-400 Hz soft rustling murmur)
 * - Inspiratory Fine/Coarse Crackles (Pneumonia / Fibrosis - discrete explosive pops)
 * - High-Pitched Wheezing (Asthma / Bronchospasm - phase-accumulated musical harmonics)
 * - Stridor (Upper Airway Obstruction - harsh monophonic inspiratory sound)
 * Features real-time FFT AnalyserNode integration for synchronized spectrogram telemetry.
 */

class PulmonaryAudioSynthesizer {
  constructor() {
    this.audioCtx = null;
    this.isPlaying = false;
    this.currentSource = null;
    this.currentGain = null;
    this.analyser = null;
    this.visualizerCallback = null;
    this.animationFrameId = null;
    this.stethoscopeMode = 'diaphragm'; // 'diaphragm' (100-1200 Hz) or 'bell' (20-250 Hz)
  }

  setStethoscopeMode(mode = 'diaphragm') {
    this.stethoscopeMode = mode;
  }

  _initContext() {
    if (!this.audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContextClass();
    }
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
    if (!this.analyser && this.audioCtx) {
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 64; // 32 frequency bins
      this.analyser.smoothingTimeConstant = 0.75;
    }
    return this.audioCtx;
  }

  stop() {
    if (this.currentGain && this.audioCtx) {
      const sourceToStop = this.currentSource;
      const gainToStop = this.currentGain;
      try {
        const now = this.audioCtx.currentTime;
        gainToStop.gain.cancelScheduledValues(now);
        gainToStop.gain.setValueAtTime(gainToStop.gain.value, now);
        gainToStop.gain.exponentialRampToValueAtTime(0.0001, now + 0.05);
        setTimeout(() => {
          try {
            if (sourceToStop) sourceToStop.stop();
          } catch (e) {}
        }, 60);
      } catch (e) {
        if (sourceToStop) {
          try { sourceToStop.stop(); } catch (err) {}
        }
      }
    }
    this.currentSource = null;
    this.currentGain = null;
    this.isPlaying = false;
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  setVisualizerCallback(callback) {
    this.visualizerCallback = callback;
  }

  getFrequencyData(targetArray) {
    if (this.analyser && this.isPlaying) {
      this.analyser.getByteFrequencyData(targetArray);
    } else {
      targetArray.fill(0);
    }
  }

  playRespiratorySound(type = 'crackles', duration = 3.8) {
    const ctx = this._initContext();
    this.stop();

    const sampleRate = ctx.sampleRate;
    const bufferSize = Math.floor(sampleRate * duration);
    const buffer = ctx.createBuffer(1, bufferSize, sampleRate);
    const data = buffer.getChannelData(0);

    // Paul Kellet / Gardner Pink Noise Filter States (velvety airflow simulation)
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;

    // Pre-calculate discrete crackle events (fine / coarse rales)
    // In pulmonology: 12-20 explosive bursts during mid-to-late inspiration (t = 0.45s to 1.25s)
    const crackleEvents = [];
    if (type === 'crackles') {
      const cycleLength = 3.0;
      const totalCycles = Math.ceil(duration / cycleLength);
      for (let c = 0; c < totalCycles; c++) {
        const cycleStart = c * cycleLength;
        const numCrackles = Math.floor(Math.random() * 8 + 14); // 14 to 22 crackles per breath
        for (let k = 0; k < numCrackles; k++) {
          const crackleTime = cycleStart + 0.42 + Math.random() * 0.78; // Mid-to-late inspiration
          if (crackleTime < duration) {
            crackleEvents.push({
              timeSec: crackleTime,
              freqHz: Math.random() * 260 + 440, // 440 - 700 Hz (fine crackle dominant frequency)
              decayMs: Math.random() * 4 + 3,    // 3 - 7 ms rapid pressure equalization decay
              amplitude: Math.random() * 0.45 + 0.55
            });
          }
        }
      }
    }

    let wheezePhase = 0;
    const wheezeBaseFreq = 440; // A4 musical wheeze characteristic of acute bronchial constriction

    // Generate Synthesized Pulmonary Waveform
    for (let i = 0; i < bufferSize; i++) {
      const t = i / sampleRate;
      const cycleTime = t % 3.0;

      // Asymmetrical respiratory cycle:
      // Inspiration: 0.0s - 1.3s (crescendo / decrescendo)
      // Expiration: 1.3s - 2.8s (prolonged soft decrescendo)
      let breathEnv = 0.0;
      let isExpiration = false;

      if (cycleTime < 1.3) {
        breathEnv = Math.sin((cycleTime / 1.3) * Math.PI) * 0.75;
      } else if (cycleTime < 2.8) {
        breathEnv = Math.sin(((cycleTime - 1.3) / 1.5) * Math.PI) * 0.38;
        isExpiration = true;
      }

      // Generate filtered pink noise for turbulent bronchovesicular airflow
      const white = Math.random() * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      const pinkNoise = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.09;
      b6 = white * 0.115926;

      let sample = pinkNoise * breathEnv;

      // 1. Fine / Coarse Crackles (Pneumonia): Add discrete explosive popping bursts
      if (type === 'crackles') {
        for (let e = 0; e < crackleEvents.length; e++) {
          const ev = crackleEvents[e];
          const dt = t - ev.timeSec;
          if (dt >= 0 && dt < 0.018) { // 18 ms window
            const tau = ev.decayMs / 1000.0;
            const popWaveform = ev.amplitude * Math.sin(2 * Math.PI * ev.freqHz * dt) * Math.exp(-dt / tau);
            sample += popWaveform;
          }
        }
      }

      // 2. High-Pitched Wheezing (Asthma / COPD): Phase-accumulated continuous musical sound
      if (type === 'wheezing') {
        if (isExpiration && breathEnv > 0.05) {
          // Vibrato and pitch modulation characteristic of fluttering airway walls
          const instFreq = wheezeBaseFreq + Math.sin(t * 5.2) * 35;
          wheezePhase += (2 * Math.PI * instFreq) / sampleRate;
          // Fundamental + soft second harmonic
          const wheezeTone = (Math.sin(wheezePhase) + 0.35 * Math.sin(wheezePhase * 2.0)) * 0.42 * breathEnv;
          sample += wheezeTone;
        } else if (!isExpiration && cycleTime > 0.6) {
          // Milder inspiratory monophonic wheeze
          wheezePhase += (2 * Math.PI * 410) / sampleRate;
          sample += Math.sin(wheezePhase) * 0.18 * breathEnv;
        }
      }

      // 3. Stridor (Upper Airway Critical Obstruction): Harsh inspiratory monophonic peak
      if (type === 'stridor') {
        if (!isExpiration && breathEnv > 0.08) {
          const stridorTone = (Math.sin(2 * Math.PI * 840 * t) + 0.4 * Math.sin(2 * Math.PI * 1680 * t)) * 0.5 * breathEnv;
          sample += stridorTone;
        }
      }

      // Hard limiter / soft clip to prevent audio distortion
      data[i] = Math.max(-1.0, Math.min(1.0, sample));
    }

    // Acoustic Signal Processing: Stethoscopic Biquad Filtering
    const source = ctx.createBufferSource();
    source.buffer = buffer;

    const biquadFilter = ctx.createBiquadFilter();
    biquadFilter.type = 'lowpass';
    // Bell Mode (20-260 Hz) vs Diaphragm Mode (100-1400 Hz)
    const isBell = this.stethoscopeMode === 'bell';
    const cutoffFreq = isBell ? 260 : (type === 'wheezing' ? 1400 : (type === 'stridor' ? 2600 : 850));
    const filterQ = isBell ? 2.2 : (type === 'wheezing' ? 3.5 : 1.2);
    biquadFilter.frequency.setValueAtTime(cutoffFreq, ctx.currentTime);
    biquadFilter.Q.setValueAtTime(filterQ, ctx.currentTime);

    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.85, ctx.currentTime);

    // Node graph: source -> biquadFilter -> gainNode -> analyser -> destination
    source.connect(biquadFilter);
    biquadFilter.connect(gainNode);
    gainNode.connect(this.analyser);
    this.analyser.connect(ctx.destination);

    source.start();
    this.currentSource = source;
    this.currentGain = gainNode;
    this.isPlaying = true;

    // Start telemetry visualizer loop if callback registered
    if (this.visualizerCallback) {
      const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
      const loop = () => {
        if (!this.isPlaying) return;
        this.analyser.getByteFrequencyData(dataArray);
        this.visualizerCallback(dataArray);
        this.animationFrameId = requestAnimationFrame(loop);
      };
      this.animationFrameId = requestAnimationFrame(loop);
    }

    source.onended = () => {
      this.isPlaying = false;
      if (this.animationFrameId) {
        cancelAnimationFrame(this.animationFrameId);
        this.animationFrameId = null;
      }
      if (this.visualizerCallback) {
        this.visualizerCallback(new Uint8Array(32)); // Reset to resting state
      }
    };
  }
}

// Global synthesizer instance
window.pulmonarySynth = new PulmonaryAudioSynthesizer();

