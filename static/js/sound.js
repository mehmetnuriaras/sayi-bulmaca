import { state } from './state.js';

let audioCtx = null;

function getAudioContext() {
    if (state.isMuted) return null;
    if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    // resume if suspended (common in browser security models)
    if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    return audioCtx;
}

export function initSoundState() {
    const savedMute = localStorage.getItem('game_muted');
    state.isMuted = savedMute === 'true';
    updateMuteButtonUI();
}

export function toggleMute() {
    state.isMuted = !state.isMuted;
    localStorage.setItem('game_muted', state.isMuted);
    updateMuteButtonUI();
    if (state.isMuted && audioCtx) {
        audioCtx.close();
        audioCtx = null;
    } else {
        getAudioContext();
    }
}

export function updateMuteButtonUI() {
    const el = document.getElementById('btn-mute');
    if (!el) return;
    el.innerText = state.isMuted ? '🔇' : '🔊';
    el.title = state.isMuted ? 'Sesi Aç (Unmute)' : 'Sesi Kapat (Mute)';
}

function playTone(freq, type, duration, volume = 0.1) {
    const ctx = getAudioContext();
    if (!ctx) return;

    try {
        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        
        gainNode.gain.setValueAtTime(volume, ctx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);

        osc.connect(gainNode);
        gainNode.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + duration);
    } catch (e) {
        console.warn('Audio play failed:', e);
    }
}

export function playClick() {
    playTone(1200, 'sine', 0.05, 0.05);
}

export function playCorrectDigit() {
    playTone(880, 'sine', 0.15, 0.08); // high pleasing beep
}

export function playIncorrectDigit() {
    playTone(220, 'triangle', 0.2, 0.1); // low pleasant thud
}

export function playSuccess() {
    // Upward arpeggio
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;
    [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        setTimeout(() => {
            playTone(freq, 'sine', 0.25, 0.08);
        }, i * 100);
    });
}

export function playError() {
    playTone(150, 'sawtooth', 0.35, 0.12); // low buzz
}

export function playWin() {
    const ctx = getAudioContext();
    if (!ctx) return;
    // Energetic retro win chime
    const baseFreqs = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99];
    baseFreqs.forEach((freq, i) => {
        setTimeout(() => {
            playTone(freq, 'sine', 0.4, 0.08);
        }, i * 80);
    });
    setTimeout(() => {
        playTone(1046.50, 'sine', 0.8, 0.1);
    }, baseFreqs.length * 80);
}

export function playLose() {
    const ctx = getAudioContext();
    if (!ctx) return;
    // Sad falling slide
    try {
        const osc = ctx.createOscillator();
        const gainNode = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(300, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(80, ctx.currentTime + 0.8);
        
        gainNode.gain.setValueAtTime(0.12, ctx.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + 0.8);

        osc.connect(gainNode);
        gainNode.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + 0.8);
    } catch (e) {
        console.warn('Audio play failed:', e);
    }
}

export function playTick() {
    playTone(150, 'triangle', 0.04, 0.05); // quiet tick
}
