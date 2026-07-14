---
title: "Projects"
layout: "single"
hidemeta: true
showtoc: false
comments: false
---

<style>
.projects-section-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin: 2.5rem 0 1.2rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.project-card {
  background: var(--entry);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.project-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

.project-card.placeholder {
  opacity: 0.45;
  cursor: default;
  pointer-events: none;
}

.project-thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  background: var(--tertiary);
  display: block;
}

.project-thumb-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: var(--tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--secondary);
}

.project-body {
  padding: 1.1rem 1.2rem 1.2rem;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.project-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--primary);
  margin: 0 0 0.3rem;
}

.project-period {
  font-size: 0.78rem;
  color: var(--secondary);
  margin: 0 0 0.7rem;
}

.project-desc {
  font-size: 0.875rem;
  color: var(--content);
  line-height: 1.6;
  margin: 0 0 1rem;
  flex: 1;
}

.project-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.project-tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
  background: var(--code-bg);
  color: var(--secondary);
  white-space: nowrap;
}

.project-links {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  align-items: center;
}

.project-link {
  font-size: 0.73rem;
  font-weight: 600;
  padding: 0.3rem 0.75rem;
  border-radius: 20px;
  text-decoration: none !important;
  border: 1.5px solid var(--tertiary);
  color: var(--secondary);
  background: var(--code-bg);
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  letter-spacing: 0.01em;
}

.project-link:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--code-bg);
}

.project-link.primary-link {
  background: var(--primary);
  color: var(--theme);
  border-color: var(--primary);
}

.project-link.primary-link:hover {
  opacity: 0.75;
}
</style>

<p style="color: var(--secondary); font-size: 0.9rem; margin-top: -0.5rem; margin-bottom: 2rem;">
학부 연구부터 석사 과정까지 진행한 프로젝트들을 정리했습니다.
</p>

<div class="projects-section-title">주요 프로젝트</div>

<div class="project-grid">

  <!-- HBOT Chamber -->
  <div class="project-card">
    <img class="project-thumb" src="/images/projects/hbot-chamber.png" alt="HBOT Chamber" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
    <div class="project-thumb-placeholder" style="display:none;">🫁</div>
    <div class="project-body">
      <div class="project-name">IoT 고압산소챔버 시스템</div>
      <div class="project-period">2024 · 석사 학위논문 프로젝트</div>
      <div class="project-desc">
        Tinker Board 2S 기반 고압산소챔버 원격 제어 및 모니터링 플랫폼.
        Android 앱이 SBC 위에서 직접 실행되며 GPIO·SPI·I2C로 하드웨어를 제어하고,
        PID 압력 제어 및 실시간 센서 스트리밍을 수행. NestJS 서버 + Vue3 대시보드와 WebSocket으로 연동.
      </div>
      <div class="project-tags">
        <span class="project-tag">Android</span>
        <span class="project-tag">Java</span>
        <span class="project-tag">MVVM</span>
        <span class="project-tag">Tinker Board 2S</span>
        <span class="project-tag">MRAA</span>
        <span class="project-tag">PID</span>
        <span class="project-tag">NestJS</span>
        <span class="project-tag">Vue 3</span>
        <span class="project-tag">MongoDB</span>
        <span class="project-tag">WebSocket</span>
      </div>
      <div class="project-links">
        <a class="project-link primary-link" href="/projects/hbot-chamber/">Overview</a>
        <a class="project-link" href="https://github.com/bromine1997/HbotChamberApp" target="_blank">GitHub (App)</a>
        <a class="project-link" href="https://github.com/bromine1997/tinkerboard-test" target="_blank">GitHub (Server)</a>
      </div>
    </div>
  </div>

  <!-- ESP32 재활자전거 -->
  <div class="project-card">
    <img class="project-thumb" src="/images/projects/rehab-bicycle.png" alt="재활 자전거" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
    <div class="project-thumb-placeholder" style="display:none;">🚲</div>
    <div class="project-body">
      <div class="project-name">재활 자전거 실시간 측정 시스템</div>
      <div class="project-period">2022 ~ 2023 · 학부연구 / 석사</div>
      <div class="project-desc">
        ESP32 Feather V2 기반 4채널 로드셀 동기화 수집 시스템.
        ADS1232를 4개 병렬 운용해 SCLK 인터럽트로 팔·다리 페달의 힘을 동시에 측정하고,
        PSRAM에 버퍼링 후 WebSocket으로 브라우저 기반 실시간 모니터링 및 CSV 다운로드 제공.
      </div>
      <div class="project-tags">
        <span class="project-tag">ESP32</span>
        <span class="project-tag">Arduino</span>
        <span class="project-tag">ADS1232 ×4</span>
        <span class="project-tag">AS5600</span>
        <span class="project-tag">WebSocket</span>
        <span class="project-tag">SPIFFS</span>
        <span class="project-tag">PSRAM</span>
        <span class="project-tag">JavaScript</span>
      </div>
      <div class="project-links">
        <a class="project-link primary-link" href="/projects/rehab-bicycle/">Overview</a>
        <a class="project-link" href="https://github.com/bromine1997/RehabilitationBicycle" target="_blank">GitHub</a>
      </div>
    </div>
  </div>

</div>

<div class="projects-section-title">사이드 프로젝트</div>

<div class="project-grid">

  <!-- ATMega -->
  <div class="project-card">
    <img class="project-thumb" src="/images/projects/atmega-project.jpg" alt="ATmega4809" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
    <div class="project-thumb-placeholder" style="display:none;">⚙️</div>
    <div class="project-body">
      <div class="project-name">ATmega4809 Peripheral Driver</div>
      <div class="project-period">2021 · 마이크로컴퓨터시스템 수업</div>
      <div class="project-desc">
        커스텀 PCB 직접 납땜 후 ATmega4809 펌웨어 구현.
        GPIO, UART, SPI, I2C, ADC 등 주변장치 드라이버를 외부 라이브러리 없이
        레지스터 수준에서 직접 작성.
      </div>
      <div class="project-tags">
        <span class="project-tag">ATmega4809</span>
        <span class="project-tag">C</span>
        <span class="project-tag">Bare-metal</span>
        <span class="project-tag">Microchip Studio</span>
        <span class="project-tag">AVR</span>
      </div>
      <div class="project-links">
        <a class="project-link primary-link" href="/projects/atmega4809/">Overview</a>
        <a class="project-link" href="https://github.com/bromine1997/atmega4809-project" target="_blank">GitHub</a>
      </div>
    </div>
  </div>

  <!-- Placeholder 1 -->
  <div class="project-card placeholder">
    <div class="project-thumb-placeholder">📌</div>
    <div class="project-body">
      <div class="project-name">Coming Soon</div>
      <div class="project-period">—</div>
      <div class="project-desc">정리 중입니다.</div>
      <div class="project-tags"></div>
    </div>
  </div>

  <!-- Placeholder 2 -->
  <div class="project-card placeholder">
    <div class="project-thumb-placeholder">📌</div>
    <div class="project-body">
      <div class="project-name">Coming Soon</div>
      <div class="project-period">—</div>
      <div class="project-desc">정리 중입니다.</div>
      <div class="project-tags"></div>
    </div>
  </div>

</div>
