/**
 * OmniCare AI - Web Audio API Pulmonary Acoustics Synthesizer
 * Generates realistic acoustic simulations of human respiratory breath sounds:
 * - Normal Vesicular Breath Sound
 * - Inspiratory Fine/Coarse Crackles (Pneumonia / Pulmonary Fibrosis)
 * - High-Pitched Wheezing (Asthma / Bronchospasm / COPD)
 * - Stridor (Upper Airway Obstruction)
 * Plays through HP Poly Studio Dual Speakers with realistic acoustic filtering.
 */

class PulmonaryAudioSynthesizer {
  constructor() {
    this.audioCtx = null;
    this.isPlaying = false;
    this.currentSource = null;
    this.currentGain = null;
  }

  _initContext() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.audioCtx = new AudioContext();
    }
    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }
  }

  stop() {
    if (this.currentGain && this.audioCtx) {
      try {
        this.currentGain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.2);
        setTimeout(() => {
          if (this.currentSource) {
            try { this.currentSource.stop(); } catch(e){}
            this.currentSource = null;
          }
          this.isPlaying = false;
        }, 220);
      } catch (e) {
        this.isPlaying = false;
      }
    } else {
      this.isPlaying = false;
    }
  }

  playRespiratorySound(type = 'crackles', duration = 4.0) {
    this._initContext();
    this.stop();

    const ctx = this.audioCtx;
    const sampleRate = ctx.sampleRate;
    const bufferSize = sampleRate * duration;
    const buffer = ctx.createBuffer(1, bufferSize, sampleRate);
    const data = buffer.getChannelData(0);

    // Respiratory Cycle: ~3 seconds per breath (1.2s Inspiration, 1.8s Expiration)
    for (let i = 0; i < bufferSize; i++) {
      const t = i / sampleRate;
      const cycleTime = t % 3.0;
      
      // Breathing envelope: Inspiration (rise) then Expiration (fall)
      let breathEnv = 0.0;
      if (cycleTime < 1.2) {
        breathEnv = Math.sin((cycleTime / 1.2) * Math.PI) * 0.7; // Inspiration
      } else if (cycleTime < 2.8) {
        breathEnv = Math.sin(((cycleTime - 1.2) / 1.6) * Math.PI) * 0.4; // Expiration
      }

      // Base pink/brown respiratory airflow noise
      const white = (Math.random() * 2 - 1) * 0.25;
      let sample = white * breathEnv;

      // 1. Fine / Coarse Crackles: Discontinuous explosive micro-clicks during late inspiration
      if (type === 'crackles') {
        if (cycleTime > 0.5 && cycleTime < 1.15) {
          // Probability of micro-explosive crackle pop
          if (Math.random() < 0.035) {
            const cracklePop = (Math.random() * 2 - 1) * Math.exp(-((i % 300) / 40)) * 0.85;
            sample += cracklePop;
          }
        }
      }

      // 2. High-Pitched Wheezing: Continuous musical harmonic oscillation
      if (type === 'wheezing') {
        if (cycleTime > 0.3 && cycleTime < 2.5) {
          const freq = 440 + Math.sin(t * 4) * 45; // 440 Hz musical wheeze with vibrato
          const harmonic = Math.sin(2 * Math.PI * freq * t) * 0.35 * breathEnv;
          sample += harmonic;
        }
      }

      // 3. Stridor: Harsh high-pitched continuous inspiratory monophonic sound
      if (type === 'stridor') {
        if (cycleTime < 1.2) {
          const stridorTone = (Math.sin(2 * Math.PI * 850 * t) + 0.4 * Math.sin(2 * Math.PI * 1700 * t)) * 0.45 * breathEnv;
          sample += stridorTone;
        }
      }

      data[i] = sample;
    }

    // Connect nodes through acoustic low-pass stethoscopic filter
    const source = ctx.createBufferSource();
    source.buffer = buffer;

    const biquadFilter = ctx.createBiquadFilter();
    biquadFilter.type = 'lowpass';
    biquadFilter.frequency.setValueAtTime(type === 'wheezing' ? 1200 : (type === 'stridor' ? 2400 : 750), ctx.currentTime);
    biquadFilter.Q.setValueAtTime(type === 'wheezing' ? 4.0 : 1.2, ctx.currentTime);

    const gainNode = ctx.createGain();
    gainNode.gain.setValueAtTime(0.85, ctx.currentTime);

    source.connect(biquadFilter);
    biquadFilter.connect(gainNode);
    gainNode.connect(ctx.destination);

    source.start();
    this.currentSource = source;
    this.currentGain = gainNode;
    this.isPlaying = true;

    source.onended = () => {
      this.isPlaying = false;
    };
  }
}

// Global synthesizer instance
window.pulmonarySynth = new PulmonaryAudioSynthesizer();
